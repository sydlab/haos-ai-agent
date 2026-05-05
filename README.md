# Home Assistant AI Agent

An AI-assisted agent for **Home Assistant**: it pulls states, history, and core logs via the **REST API**, correlates what it finds, and produces a concise narrative—with a path toward **Cursor-native** operation (MCP + Skills) alongside the reference **Python + Anthropic** runner.

This is **not** Home Assistant OS (HAOS) and **not** the built-in Home Assistant **Supervisor** add-on. The GitHub repository may still use the historical slug **`haos-supervisor`**.

## Branches

| Branch | Purpose |
|--------|---------|
| **`main`** | Project overview, architecture mental map, and **phased implementation plan** for the Cursor/MCP track. |
| **`dev`** | Reference implementation: Python + Anthropic agent, HA REST client, tools, and cron-friendly `run.py`. |

Switch to `dev` for install, `.env`, and day-to-day code.

```bash
git checkout dev
```

## Mental map (Cursor track)

```text
You in Cursor chat (+ Skill: investigation playbook)
        │
        ▼
Cursor agent ──► model ──► MCP client (built-in)
                                │
                                ▼
                     HA MCP server (this repo, Phase 1)
                                │
                                ▼
                     Home Assistant REST API
```

**Skill / Rule** = procedure and report shape (no secrets). **MCP server** = `HA_URL` / `HA_TOKEN` and tool implementations.

## Phased implementation plan

### Phase 1 — HA MCP server

- Small **Python MCP server** (official `mcp` SDK + `httpx` or `requests`).
- Tools (mirror current behavior): `get_unavailable_entities`, `get_entity_history` (clamp hours, e.g. max 72), `get_error_log` (cap lines/payload), optional `send_notification`.
- Environment: `HA_URL`, `HA_TOKEN` via **Cursor MCP config** `env` (never committed).
- Structured errors: HTTP failures returned in tool results, not silent failures.

### Phase 2 — Cursor Skill (and optional Rule)

- **Skill** encodes: tool order (unavailable → error log when multi-domain → history samples), report format (&lt;250 words, priorities), **read-only default**; future `call_service` only with explicit user confirmation.
- Optional **Rule** if this repo is the dedicated HA ops workspace.

### Phase 3 — Notifications and headless

- **A:** Notification tool in MCP (HA reachable from MCP host).
- **B:** Chat-only report in Cursor.
- **C:** Keep **`dev`** `run.py` on a Pi for scheduled unattended checks.

Choose explicitly; avoid silent mobile-notify failures.

### Phase 4 — Hardening and extensions

- `raise_for_status` (or equivalent) on all HA calls; no bare `except` on push paths.
- **Roadmap alignment:** `call_service` remediation, baselines/trends, energy/automation signals, optional **Canvas** for dense timelines.

## Claude way vs Cursor way

| | **Claude way** (`dev`: Python loop) | **Cursor way** (this plan) |
|--|-------------------------------------|----------------------------|
| Orchestration | `agent.py` + Anthropic SDK | Cursor chat + model |
| HA access | In-process `ha_client` / `tools` | **MCP server** tools |
| Procedure | `SYSTEM_PROMPT` in code | **Skill** (+ optional Rule) |
| Trigger | Cron / `python run.py` | User message (± automation later) |
| Primary output | Terminal + HA notifications | Chat; optional HA via MCP or `dev` script |

## Local clone (work on `dev`)

```bash
git checkout dev
cp .env.example .env
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)   # prefer a dotenv loader for real use
python run.py
```

## License

Specify as needed once you add a `LICENSE` file on `dev` or here.
