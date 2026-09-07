from flask import Blueprint, jsonify, request
import os
import uuid

bp = Blueprint("timeoe_api", __name__, url_prefix="/timeoe")


def _supabase():
    from supabase import create_client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
    return create_client(url, key)


@bp.post("/commands")
def create_command():
    body = request.get_json(silent=True) or {}
    objective = str(body.get("objective", "")).strip()
    business_id = body.get("business_id")
    plan = body.get("plan") or []
    if not objective or not business_id:
        return jsonify({"error": "objective and business_id are required"}), 400

    client = _supabase()
    command_id = str(uuid.uuid4())
    command = {
        "id": command_id,
        "business_id": business_id,
        "objective": objective,
        "status": "planning",
        "plan": plan,
    }
    client.table("timeoe_commands").insert(command).execute()

    for i, item in enumerate(plan):
        if isinstance(item, str):
            title = item
            agent_id = None
            dependencies = [] if i == 0 else [f"task_{i-1}"]
        else:
            title = str(item.get("title") or item.get("name") or f"Task {i+1}")
            agent_id = item.get("agent_id")
            dependencies = item.get("dependencies", [] if i == 0 else [f"task_{i-1}"])
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
        "payload": {"objective": objective, "task_count": len(plan)},
    }).execute()
    return jsonify({"command_id": command_id, "status": "planning"}), 201


@bp.get("/commands/<command_id>")
def command_snapshot(command_id):
    client = _supabase()
    command = client.table("timeoe_commands").select("*").eq("id", command_id).single().execute().data
    tasks = client.table("timeoe_execution_tasks").select("*").eq("command_id", command_id).order("created_at").execute().data
    events = client.table("timeoe_events").select("*").eq("command_id", command_id).order("created_at", desc=False).execute().data
    return jsonify({"command": command, "tasks": tasks, "events": events})


@bp.get("/events")
def recent_events():
    client = _supabase()
    limit = min(int(request.args.get("limit", 100)), 500)
    rows = client.table("timeoe_events").select("*").order("created_at", desc=True).limit(limit).execute().data
    return jsonify({"events": rows})
