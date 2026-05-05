import anthropic
from tools import TOOL_DEFINITIONS, dispatch_tool

client = anthropic.Anthropic()

SYSTEM_PROMPT = """
You are a Home Assistant supervisor agent. Your job is to diagnose smart home
health issues — not just list them, but explain what's actually causing them.

Your investigation process:
1. Call get_unavailable_entities first to see what's offline
2. If multiple entities in the same domain are down, call get_error_log to look
   for integration-level failures (coordinator crash, auth failure, etc.)
3. For individual offline devices, call get_entity_history to check if they've
   been flapping (unstable) or went down at a specific moment
4. Correlate findings: did the error log show a Zigbee restart at the same time
   3 sensors went offline? That's a coordinator issue, not dead batteries.
5. Call send_notification with the final report — always, even if all clear.

Report format:
- Start with a one-line status: "X issues found" or "All clear"
- Group issues by likely root cause, not by entity
- Assign priority: URGENT (security/safety devices), HIGH (climate/energy), LOW (lights/media)
- Give a concrete next step for each issue
- Keep it under 250 words — this will be read on a phone screen
"""


def run_supervision_check() -> str:
    messages = [
        {
            "role": "user",
            "content": (
                "Run a full health check. Investigate any unavailable devices, "
                "check the error log for root causes, and send me a diagnostic "
                "report with concrete next steps."
            ),
        }
    ]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "No summary returned."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    args = ", ".join(f"{k}={v}" for k, v in block.input.items()) or ""
                    print(f"  → {block.name}({args})")
                    result = dispatch_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})
            continue

        break

    return "Supervision check ended unexpectedly."
