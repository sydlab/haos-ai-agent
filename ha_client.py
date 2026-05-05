import requests
from datetime import datetime, timedelta, timezone
from config import HA_URL, HA_TOKEN

HEADERS = {
    "Authorization": f"Bearer {HA_TOKEN}",
    "Content-Type": "application/json",
}


def get_all_states() -> list[dict]:
    response = requests.get(f"{HA_URL}/api/states", headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()


def get_unavailable_entities() -> dict:
    all_states = get_all_states()

    unavailable = [
        {
            "entity_id": s["entity_id"],
            "state": s["state"],
            "friendly_name": s["attributes"].get("friendly_name", s["entity_id"]),
            "last_changed": s["last_changed"],
            "domain": s["entity_id"].split(".")[0],
        }
        for s in all_states
        if s["state"] in ("unavailable", "unknown")
    ]

    by_domain: dict[str, list] = {}
    for entity in unavailable:
        by_domain.setdefault(entity["domain"], []).append(entity)

    return {
        "total_unavailable": len(unavailable),
        "total_entities_checked": len(all_states),
        "by_domain": by_domain,
        "entities": unavailable,
    }


def get_entity_history(entity_id: str, hours: int = 24) -> dict:
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    response = requests.get(
        f"{HA_URL}/api/history/period/{start.isoformat()}",
        headers=HEADERS,
        timeout=10,
        params={
            "filter_entity_id": entity_id,
            "end_time": end.isoformat(),
            "minimal_response": "true",
        },
    )
    response.raise_for_status()
    raw = response.json()

    if not raw or not raw[0]:
        return {
            "entity_id": entity_id,
            "hours_checked": hours,
            "state_changes": [],
            "summary": "No history found.",
        }

    history = raw[0]
    state_changes = [
        {"state": h["state"], "changed_at": h["last_changed"]}
        for h in history
    ]

    unique_states = list({h["state"] for h in state_changes})
    unavailable_count = sum(
        1 for h in state_changes if h["state"] in ("unavailable", "unknown")
    )
    flapping = unavailable_count > 3

    return {
        "entity_id": entity_id,
        "hours_checked": hours,
        "total_state_changes": len(state_changes),
        "unique_states_seen": unique_states,
        "unavailable_count": unavailable_count,
        "flapping": flapping,
        "state_changes": state_changes[-30:],
        "summary": (
            f"Went unavailable {unavailable_count}x over {hours}h. "
            f"{'Flapping (unstable connection).' if flapping else 'Mostly stable before this.'}"
        ),
    }


def get_error_log() -> dict:
    response = requests.get(f"{HA_URL}/api/error_log", headers=HEADERS, timeout=10)
    response.raise_for_status()

    lines = response.text.splitlines()

    important_lines = [
        line for line in lines
        if any(level in line for level in ("WARNING", "ERROR", "CRITICAL"))
    ]

    seen = set()
    deduped = []
    for line in important_lines:
        key = line[25:105] if len(line) > 25 else line
        if key not in seen:
            seen.add(key)
            deduped.append(line)

    return {
        "total_log_lines": len(lines),
        "important_lines_found": len(deduped),
        "recent_warnings_and_errors": deduped[-40:],
    }


def send_notification(message: str, title: str = "HAOS AI Agent") -> dict:
    """
    Creates a persistent notification in HA sidebar and pushes to mobile app.
    Update mobile_service below to match your device name:
    HA → Developer Tools → Services → search notify.mobile_app
    """
    requests.post(
        f"{HA_URL}/api/services/persistent_notification/create",
        headers=HEADERS,
        timeout=10,
        json={"title": title, "message": message},
    )

    mobile_service = "notify/mobile_app_your_phone"  # TODO: update to your device
    try:
        requests.post(
            f"{HA_URL}/api/services/{mobile_service}",
            headers=HEADERS,
            timeout=10,
            json={"title": title, "message": message},
        )
    except Exception:
        pass

    return {"sent": True, "title": title, "message_length": len(message)}
