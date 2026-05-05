import json
from ha_client import (
    get_unavailable_entities,
    get_entity_history,
    get_error_log,
    send_notification,
)

TOOL_DEFINITIONS = [
    {
        "name": "get_unavailable_entities",
        "description": (
            "Fetch all Home Assistant entities currently in 'unavailable' or 'unknown' state. "
            "Returns a breakdown by domain so you can identify whether the issue is isolated "
            "or affecting a whole integration. Always call this first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_entity_history",
        "description": (
            "Get state change history for a specific entity over the last N hours. "
            "Use this after get_unavailable_entities to check whether an offline device "
            "has been flapping (unstable) or went down suddenly. "
            "Helps distinguish 'dead battery' from 'intermittent connection issue'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "The entity ID to check, e.g. binary_sensor.front_door",
                },
                "hours": {
                    "type": "integer",
                    "description": "How many hours of history to fetch. Default 24, max 72.",
                    "default": 24,
                },
            },
            "required": ["entity_id"],
        },
    },
    {
        "name": "get_error_log",
        "description": (
            "Fetch Home Assistant's internal error and warning log. "
            "Use this to find integration failures, Z-Wave/Zigbee coordinator issues, "
            "YAML config errors, and add-on crashes. "
            "Correlate timestamps here against when devices went unavailable."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "send_notification",
        "description": (
            "Send the final diagnostic report as a notification. "
            "Call this once at the end, after all investigation is complete. "
            "Keep the message under 250 words — it will appear on a phone screen. "
            "If everything is healthy, send a brief 'All clear' message. "
            "Always send a notification — the user needs confirmation the check ran."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Short title, e.g. 'HA Health: 2 issues' or 'HA Health: All clear'",
                },
                "message": {
                    "type": "string",
                    "description": "The diagnostic report body.",
                },
            },
            "required": ["title", "message"],
        },
    },
]


def dispatch_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_unavailable_entities":
        return json.dumps(get_unavailable_entities(), indent=2, default=str)

    if tool_name == "get_entity_history":
        entity_id = tool_input["entity_id"]
        hours = tool_input.get("hours", 24)
        return json.dumps(get_entity_history(entity_id, hours), indent=2, default=str)

    if tool_name == "get_error_log":
        return json.dumps(get_error_log(), indent=2, default=str)

    if tool_name == "send_notification":
        result = send_notification(
            message=tool_input["message"],
            title=tool_input.get("title", "HA AI Agent"),
        )
        return json.dumps(result)

    return json.dumps({"error": f"Unknown tool: {tool_name}"})
