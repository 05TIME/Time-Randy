from flask import Blueprint, jsonify, request
import os
import uuid

from auth import authenticate_request, authorize_business, unauthorized_response

bp = Blueprint("timeoe_api", __name__, url_prefix="/timeoe")


def _supabase():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
    return create_client(url, key)


def _authenticated_supabase():
    try:
        user_id = authenticate_request()
    except PermissionError as exc:
        return None, unauthorized_response(str(exc))
    except RuntimeError as exc:
        return None, jsonify({"error": str(exc)}), 503
    return user_id, None


def _require_business_access(client, user_id: str, business_id: str):
    if not authorize_business(client, user_id, business_id):
        return jsonify({"error": "forbidden"}), 403
    return None


@bp.post("/commands")
def create_command():
    user_id, auth_error = _authenticated_supabase()
    if auth_error:
        return auth_error

    body = request.get_json(silent=True) or {}
    objective = str(body.get("objective", "")).strip()
    business_id = body.get("business_id")
    plan = body.get("plan") or []
    if not objective or not business_id:
        return jsonify({"error": "objective and business_id are required"}), 400
    if not isinstance(plan, list):
        return jsonify({"error": "plan must be an array"}), 400

    # Validate the full plan before performing any writes.
    normalized_plan = []
    for i, item in enumerate(plan):
        if isinstance(item, str):
            title = item
            agent_id = None
            dependencies = [] if i == 0 else [f"task_{i-1}"]
        elif isinstance(item, dict):
            title = str(item.get("title") or item.get("name") or f"Task {i+1}")
            agent_id = item.get("agent_id")
            dependencies = item.get("dependencies", [] if i == 0 else [f"task_{i-1}"])
            if not isinstance(dependencies, list):
                return jsonify({"error": "task dependencies must be arrays"}), 400
        else:
            return jsonify({"error": "each plan item must be a string or object"}), 400
        normalized_plan.append((title, agent_id, dependencies))

    client = _supabase()
    access_error = _require_business_access(client, user_id, str(business_id))
    if access_error:
        return access_error

    for _, agent_id, _ in normalized_plan:
        if agent_id:
            agent = (
                client.table("timeoe_agents")
                .select("id")
                .eq("id", str(agent_id))
                .eq("business_id", str(business_id))
                .limit(1)
                .execute()
                .data
            )
            if not agent:
                return jsonify({"error": "agent does not belong to business"}), 403

    command_id = str(uuid.uuid4())
    command = {
        "id": command_id,
        "business_id": business_id,
        "objective": objective,
        "status": "planning",
        "plan": plan,
    }
    client.table("timeoe_commands").insert(command).execute()

    for i, (title, agent_id, dependencies) in enumerate(normalized_plan):
        client.table("timeoe_execution_tasks").insert({
            "command_id": command_id,
            "business_id": business_id,
            "agent_id": agent_id,
            "task_key": f"task_{i}",
            "title": title,
            "dependencies": dependencies,
        }).execute()

    client.table("timeoe_events").insert({
        "command_id": command_id,
        "event_type": "COMMAND_RECEIVED",
        "state": "queued",
        "payload": {"objective": objective, "task_count": len(plan), "user_id": user_id},
    }).execute()
    return jsonify({"command_id": command_id, "status": "planning"}), 201


@bp.get("/commands/<command_id>")
def command_snapshot(command_id):
    user_id, auth_error = _authenticated_supabase()
    if auth_error:
        return auth_error

    client = _supabase()
    command_response = client.table("timeoe_commands").select("*").eq("id", command_id).single().execute()
    command = command_response.data
    if not command:
        return jsonify({"error": "command not found"}), 404

    access_error = _require_business_access(client, user_id, str(command["business_id"]))
    if access_error:
        return access_error

    tasks = (
        client.table("timeoe_execution_tasks")
        .select("*")
        .eq("command_id", command_id)
        .order("created_at")
        .execute()
        .data
    )
    events = (
        client.table("timeoe_events")
        .select("*")
        .eq("command_id", command_id)
        .order("created_at", desc=False)
        .execute()
        .data
    )
    return jsonify({"command": command, "tasks": tasks, "events": events})


@bp.get("/events")
def recent_events():
    user_id, auth_error = _authenticated_supabase()
    if auth_error:
        return auth_error

    business_id = request.args.get("business_id")
    if not business_id:
        return jsonify({"error": "business_id is required"}), 400

    client = _supabase()
    access_error = _require_business_access(client, user_id, business_id)
    if access_error:
        return access_error

    try:
        limit = min(max(int(request.args.get("limit", 100)), 1), 500)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    command_rows = (
        client.table("timeoe_commands")
        .select("id")
        .eq("business_id", business_id)
        .limit(500)
        .execute()
        .data
    )
    command_ids = [row["id"] for row in command_rows]
    if not command_ids:
        return jsonify({"events": []})

    rows = (
        client.table("timeoe_events")
        .select("*")
        .in_("command_id", command_ids)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
        .data
    )
    return jsonify({"events": rows})
