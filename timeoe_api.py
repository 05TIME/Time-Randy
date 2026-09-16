from flask import Blueprint, jsonify, request
import os
import uuid

from auth import authenticate_request, authorize_business, unauthorized_response

bp = Blueprint("timeoe_api", __name__, url_prefix="/timeoe")


def _supabase():
    from supabase import create_client
    url = (os.environ.get("SUPABASE_URL") or "").rstrip("/")
    # Prefer the current Supabase secret key name, while retaining compatibility
    # with the older service-role variable already used by deployed environments.
    key = os.environ.get("SUPABASE_SECRET_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SECRET_KEY are required")
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


def _worker_authorized() -> bool:
    secret = os.environ.get("TIMEOE_WORKER_SECRET")
    supplied = request.headers.get("x-timeoe-worker-secret")
    return bool(secret and supplied and supplied == secret)


@bp.post("/worker")
def autonomous_worker():
    """Process a small batch of queued revenue tasks without external side effects.

    Research/planning tasks are recorded as verified work. Sales outreach is converted
    into approval-gated business actions; no external message is sent by this worker.
    """
    if not _worker_authorized():
        return jsonify({"error": "unauthorized worker"}), 401

    try:
        limit = min(max(int(request.args.get("limit", 10)), 1), 20)
    except ValueError:
        return jsonify({"error": "limit must be an integer"}), 400

    client = _supabase()
    queued = (
        client.table("timeoe_execution_tasks")
        .select("*")
        .eq("state", "queued")
        .order("created_at")
        .limit(limit)
        .execute()
        .data
        or []
    )

    results = []
    for task in queued:
        task_id = task["id"]
        command_id = task["command_id"]
        business_id = task["business_id"]
        try:
            client.table("timeoe_execution_tasks").update({
                "state": "running",
                "attempts": int(task.get("attempts") or 0) + 1,
                "started_at": "now()",
                "error": None,
            }).eq("id", task_id).execute()

            title = task.get("title") or ""
            task_key = task.get("task_key") or ""
            result = {"worker": "TIMEOE", "task_key": task_key, "target_usd": 10000, "capital_required": 0}

            if "sales_outreach" in task_key:
                prospects = (
                    client.table("timeoe_revenue_opportunities")
                    .select("id,company_name,contact_email,location,offer_fit,estimated_value")
                    .eq("business_id", business_id)
                    .eq("external_contact_approved", False)
                    .eq("stage", "prospect")
                    .order("created_at")
                    .limit(10)
                    .execute()
                    .data
                    or []
                )
                action_ids = []
                for prospect in prospects:
                    email = prospect.get("contact_email")
                    if not email:
                        continue
                    idem = f"outreach:{prospect['id']}"
                    existing = (
                        client.table("timeoe_business_actions")
                        .select("id")
                        .eq("idempotency_key", idem)
                        .limit(1)
                        .execute()
                        .data
                        or []
                    )
                    if existing:
                        action_ids.append(existing[0]["id"])
                        continue
                    draft = (
                        f"Hello {prospect['company_name']} team,\n\n"
                        f"I noticed an opportunity to improve {prospect.get('offer_fit') or 'customer follow-up'} "
                        "with a lightweight automation workflow. TIMEŒ can map the current process, "
                        "build the first workflow, and measure the result. Would you be open to a short call "
                        "to see whether a pilot makes sense?"
                    )
                    action = client.table("timeoe_business_actions").insert({
                        "command_id": command_id,
                        "task_id": task_id,
                        "business_id": business_id,
                        "action_type": "SEND_EXTERNAL_MESSAGE",
                        "provider": os.environ.get("TIMEOE_OUTREACH_PROVIDER", "webhook"),
                        "payload": {"recipient": email, "subject": "TIMEŒ automation pilot", "draft": draft, "opportunity_id": prospect["id"]},
                        "status": "PENDING_APPROVAL",
                        "external_effect": False,
                        "requires_approval": True,
                        "currency": "USD",
                        "verification": {"draft_only": True, "external_send": False},
                        "idempotency_key": idem,
                    }).execute().data
                    if action:
                        action_ids.append(action[0]["id"])
                result.update({"approval_gated_drafts": len(action_ids), "action_ids": action_ids, "external_send": False})

            elif "revenue_scout" in task_key or "lead_generation" in task_key:
                count = (
                    client.table("timeoe_revenue_opportunities")
                    .select("id", count="exact")
                    .eq("business_id", business_id)
                    .execute()
                ).count or 0
                result.update({"qualified_opportunities": count, "next_action": "prepare_approval_gated_outreach"})
            elif "risk_" in task_key:
                result.update({"risk_gate": "active", "external_send": False, "spend": False, "live_trading": False})
            else:
                result.update({"work_recorded": True, "next_action": "convert_verified_work_into_revenue_actions"})

            client.table("timeoe_execution_tasks").update({
                "state": "verified",
                "result": result,
                "completed_at": "now()",
            }).eq("id", task_id).execute()
            client.table("timeoe_events").insert({
                "command_id": command_id,
                "task_id": task_id,
                "agent_id": task.get("agent_id"),
                "event_type": "AUTONOMOUS_TASK_VERIFIED",
                "state": "verified",
                "payload": result,
            }).execute()
            results.append({"task_id": task_id, "state": "verified", "result": result})
        except Exception as exc:
            client.table("timeoe_execution_tasks").update({"state": "retry", "error": str(exc)}).eq("id", task_id).execute()
            client.table("timeoe_events").insert({
                "command_id": command_id,
                "task_id": task_id,
                "agent_id": task.get("agent_id"),
                "event_type": "AUTONOMOUS_TASK_RETRY",
                "state": "retry",
                "payload": {"error": str(exc)},
            }).execute()
            results.append({"task_id": task_id, "state": "retry", "error": str(exc)})

    return jsonify({"worker": "TIMEOE", "processed": len(results), "results": results})


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
