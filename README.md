# HAOS AI Agent

**Branch:** `dev` — reference Python + Anthropic agent (this README). For the **Cursor/MCP phased plan** and repo layout, see the default **`main`** branch on GitHub.

**HAOS AI Agent** is the project name (repository **`haos-ai-agent`**). It is **not** the official **Home Assistant OS** image and **not** the built-in **Supervisor** add-on stack; it is a standalone AI agent that reads your instance via the **REST API** and summarizes what it finds.

An AI agent that monitors your Home Assistant instance using Claude. It diagnoses device
failures, correlates root causes across multiple data sources, and sends you a plain-English
report — with concrete next steps.

## What it does

- Detects unavailable/unknown entities grouped by domain
- Checks entity history to distinguish flapping vs sudden failures
- Reads HA's error log and correlates timestamps with device outages
- Sends a prioritized diagnostic report to your HA sidebar and mobile app

## Setup

### 0. Clone this repository

```bash
git clone git@github.com:sydlab/haos-ai-agent.git
cd haos-ai-agent
git checkout dev
```

### 1. Get a Home Assistant long-lived token

HA → Profile (bottom-left avatar) → Long-Lived Access Tokens → Create Token

### 2. Find your mobile app service name

HA → Developer Tools → Services → search `notify.mobile_app`
Update `mobile_service` in `ha_client.py` with your device name.

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 4. Install and run

```bash
pip install -r requirements.txt

export $(cat .env | xargs)
python run.py
```

## Schedule on Raspberry Pi

```bash
# Run at 7am and 10pm daily
crontab -e

0  7 * * * cd /home/pi/haos-ai-agent && export $(cat .env | xargs) && python run.py >> /var/log/haos-ai-agent.log 2>&1
0 22 * * * cd /home/pi/haos-ai-agent && export $(cat .env | xargs) && python run.py >> /var/log/haos-ai-agent.log 2>&1
```

## Project structure

```
haos-ai-agent/   # example clone directory — https://github.com/sydlab/haos-ai-agent
├── config.py       # env var loading
├── ha_client.py    # HA REST API calls
├── tools.py        # Claude tool definitions + dispatcher
├── agent.py        # Claude agentic loop
└── run.py          # entry point
```

## Roadmap

- [ ] `call_service` — auto-remediation (reload integrations, restart devices)
- [ ] Baseline memory — track trends across days, detect gradual anomalies
- [ ] Energy monitoring — flag unusual consumption spikes
- [ ] Automation health check — detect automations that haven't fired
- [ ] Voice interface — wire into existing STT/TTS setup on Pi
