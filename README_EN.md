# seek · Email Registration Trace Lookup
<img width="1119" height="559" alt="image" src="https://github.com/user-attachments/assets/26744594-4bb3-4fe5-a6d4-be9fa2c3ac69" />

[中文](README.md) | **English**

An email OSINT tool similar to [Holehe](https://github.com/megadose/holehe), focused on an **extensible YAML rule engine**: add sites without changing code. Includes a Web UI, CLI, and HTTP API.

```text
Email → concurrent engine → built-in modules (MX / domain intel)
                         → YAML site rules
                         → (optional) Holehe / AI summary
                                   ↓
                          Web UI / CLI / JSON (SSE stream)
```

---

## Read This First

Only use this tool for lawful purposes:

1. Mapping **your own** email across platforms where it may be registered
2. Authorized penetration tests / red-team assessments with **written consent**

Unauthorized probing of other people’s emails may violate privacy laws and site terms of service. **You are solely responsible for how you use this tool.**

Results are heuristic signals only (site changes, anti-bot controls, and network conditions can cause false positives/negatives). Do not treat them as definitive proof.

---

## How Many Sites Can It Check?

| Mode | Description |
| --- | --- |
| **Reliable (default)** | 140+ tested modules with thread isolation and high-concurrency scheduling |
| **Full** | Loads 50+ self-maintained rules under `seek/definitions/` (broader coverage; some may be unknown / rate-limited) |
| **Holehe (optional)** | Full mode adds ~120 more modules (many may be broken or blocked) |

Chinese coverage includes **CSDN, CNBlogs, Gitee, Appinn Community, FIT2CLOUD Community, the openEuler Forum, HelloChinese, Global Times, MeetYou, and Wondershare**. Phone-only or mandatory-CAPTCHA services are not presented as email-account checks.

No tool can guarantee “every website worldwide, always working.” `unknown` / failures are common and do **not** mean the app is broken.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (recommended)
copy .env.example .env      # Windows
# cp .env.example .env      # Linux / macOS

# 3. Start the Web UI
python run.py               # http://127.0.0.1:8000
```

CLI:

```bash
python -m seek.cli providers                 # list modules
python -m seek.cli scan me@example.com       # scan
python -m seek.cli scan me@example.com -y --json
python -m seek.cli audit-providers --output provider-audit.json
```

`audit-providers` rechecks the reliable profile with two random negative controls. It never uses the target email and never loads modules that send password-reset messages or login codes. A positive result in reliable mode must also be returned twice; inconsistent results are downgraded to unknown.

---

## Secure Production Deployment

The default binds only to `127.0.0.1` for local use. For an Internet-facing deployment, terminate HTTPS at a reverse proxy such as Caddy, Nginx, or Cloudflare and configure:

```bash
SEEK_ALLOWED_HOSTS=seek.example.com
SEEK_DOCS_ENABLED=false
SEEK_TRUST_PROXY_HEADERS=true
SEEK_TRUSTED_PROXIES=127.0.0.1/32,::1/128
SEEK_FORCE_HTTPS=true
SEEK_HSTS_ENABLED=true
```

- Set `SEEK_TRUSTED_PROXIES` to the proxy's real IP/CIDR, never a catch-all network.
- Enable HSTS only after HTTPS works reliably; a premature setting can make browsers reject HTTP.
- For a multi-instance production service, replace the in-process limiter with Redis or gateway-level rate limiting and regularly audit dependencies.
- Never commit API keys from `.env`; use the deployment platform's secret manager.

## AI Reliable Summary (Optional)

The flow runs detectors first, then uses an LLM to summarize evidence (it does **not** invent registrations).

Configure `.env` and **restart** the server:

```bash
SEEK_AI_API_KEY=sk-...
SEEK_AI_BASE_URL=https://api.deepseek.com/v1
SEEK_AI_MODEL=deepseek-chat
```

In the Web UI choose **“AI Reliable Summary”**, or:

```bash
python -m seek.cli ai you@example.com -y
```

---

## Configuration

Copy `.env.example` to `.env` and edit as needed:

| Variable | Default | Description |
| --- | --- | --- |
| `SEEK_HOST` / `SEEK_PORT` | `127.0.0.1` / `8000` | Listen address |
| `SEEK_CONCURRENCY` | `24` | Concurrent requests; balances 100+ module speed and DNS stability |
| `SEEK_TIMEOUT` | `12` | Native-rule timeout; multi-step User Scanner checks get a separate whole-check budget (upstream allows 15 seconds per request) |
| `SEEK_SCAN_PROFILE` | `reliable` | `reliable` or `full`; the Web UI starts in full mode |
| `SEEK_AI_PROFILE` | `reliable` | AI aggregation profile; `full` includes Holehe |
| `SEEK_PROXY` | empty | Proxy, e.g. `http://127.0.0.1:7890` |
| `SEEK_ALLOWED_DOMAINS` | empty | Allowed email domains (comma-separated) |
| `SEEK_REQUIRE_CONSENT` | `true` | Require consent checkbox in the UI |
| `HIBP_API_KEY` | empty | Have I Been Pwned API key; skip module if unset |

---

## Adding a Detection Module

### Option 1: YAML (recommended)

Copy `seek/definitions/_template.yaml`, rename it, and set `enabled: true`:

```yaml
name: demo_site
title: Demo Site
category: social
homepage: https://demo.example
enabled: true

request:
  method: POST
  url: "https://demo.example/api/check-email"
  headers:
    Content-Type: "application/json"
  json:
    email: "{email}"

rules:
  - registered_if:
      status_in: [200]
      json_path_truthy: "data.exists"
    detail: Email is registered
  - not_registered_if:
      status_in: [200, 404]
    detail: Not registered
  - rate_limited_if:
      status_in: [429]

default: unknown
```

Common variables: `{email}` `{email_lower}` `{email_md5}` `{email_sha256}` `{local}` `{domain}` `{env.KEY}`

Common matchers: `status_in` / `body_contains` / `body_matches` / `json_path_exists` / `json_path_equals` / `json_path_truthy`

For CSRF / multi-step flows, use `prepare`. See `spotify.yaml` and `duolingo.yaml`.

### Option 2: Python

Create a module under `seek/providers/builtin/`, subclass `Provider`, decorate with `@register`, and import it from `builtin/__init__.py`.

---

## HTTP API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/meta` | Version, module count, rate limits |
| `GET` | `/api/providers` | Module list and readiness |
| `POST` | `/api/scan` | Synchronous scan |
| `GET` | `/api/scan/stream` | SSE streaming scan |
| `GET` | `/api/ai/investigate` | AI summary (SSE) |

Interactive docs: `http://127.0.0.1:8000/docs`

```bash
curl -X POST http://127.0.0.1:8000/api/scan \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"me@example.com\",\"consent\":true}"
```

---

## Result Statuses

| Status | Meaning |
| --- | --- |
| `registered` | Likely registered |
| `not_registered` | Likely not registered |
| `info` | Intelligence only (e.g. MX), not a registration verdict |
| `unknown` | Cannot decide (API change / anti-bot) |
| `rate_limited` | Rate limited by the target |
| `error` | Network error or exception |
| `skipped` | Missing prerequisites (e.g. API key) |

---

## Project Layout

```text
seek/
├─ run.py                 # entrypoint
├─ requirements.txt
├─ .env.example
├─ seek/
│  ├─ api.py              # FastAPI + SSE
│  ├─ cli.py
│  ├─ engine.py           # concurrent engine
│  ├─ aggregators.py      # multi-tool aggregation
│  ├─ ai_agent.py         # AI summary
│  ├─ definitions/        # YAML rules
│  ├─ data/               # reliable allowlist, etc.
│  └─ providers/          # rule engine + builtins
└─ web/                   # frontend (no build step)
```

---

## License

MIT. You are solely responsible for any consequences of using this tool.
