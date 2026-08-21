# seek · 邮箱注册痕迹反查

**中文** | [English](README_EN.md)

类似 [Holehe](https://github.com/megadose/holehe) 的邮箱 OSINT 工具，重点是**可扩展 YAML 规则引擎**：不用改代码就能加站点，并提供 Web 界面、CLI 和 HTTP API。

```text
输入邮箱 → 并发调度引擎 → 内置模块（MX / 域名情报）
                        → YAML 站点规则
                        →（可选）Holehe / AI 汇总
                              ↓
                     Web UI / CLI / JSON（SSE 流式）
```

---

## 使用前必读

仅限以下合法场景：

1. 梳理**自己的**邮箱在哪些平台留下了注册痕迹
2. 在**已取得书面授权**的渗透测试 / 红队评估中做资产收集

未经授权探测他人邮箱，可能违反《个人信息保护法》《网络安全法》及目标站点服务条款。**风险与法律责任由使用者自行承担。**

结果仅为探测推断（站点改版、风控、网络环境都会导致误报 / 漏报），不可当作结论性证据。

---

## 能查多少站点？

| 模式 | 说明 |
| --- | --- |
| **可靠模式（默认）** | 140+ 个实测模块：域名情报 + 自维护规则 + [User Scanner](https://github.com/kaifcodec/user-scanner) / Holehe 站点；使用线程隔离和高并发加速 |
| **完整模式** | 加载 `seek/definitions/` 下 100 条自维护规则（覆盖更大，但部分会 unknown / 限流） |
| **Holehe（可选）** | 完整模式下再加约 120 个站点模块（多数可能失效或被拦） |

中国及中国团队站点包括：**CSDN、博客园（CNBlogs）、Gitee（码云）、小众软件社区、飞致云社区、openEuler 论坛、HelloChinese、环球时报、她社区、万兴科技（Wondershare）**。手机号专用、强制验证码或会发送找回邮件的站点不会伪装成安全的邮箱检测结果。

成人站点仅保留经过双样本验证、不会发送找回邮件或验证码的注册可用性检查模块；该类结果属于高度敏感信息，只能查询本人邮箱或明确授权目标。

没有任何工具能保证「全世界网站都能查到且全部正常」。`unknown` / 失败很常见，不等于软件坏了。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置（建议）
copy .env.example .env      # Windows
# cp .env.example .env      # Linux / macOS

# 3. 启动 Web
python run.py               # http://127.0.0.1:8000
```

命令行：

```bash
python -m seek.cli providers                 # 查看模块
python -m seek.cli scan me@example.com       # 扫描
python -m seek.cli scan me@example.com -y --json
```

---

## 生产环境安全部署

默认配置只监听 `127.0.0.1`，适合本机使用。公网部署时，请在 Caddy / Nginx / Cloudflare 等反向代理上终止 HTTPS，并配置：

```bash
SEEK_ALLOWED_HOSTS=seek.example.com
SEEK_DOCS_ENABLED=false
SEEK_TRUST_PROXY_HEADERS=true
SEEK_TRUSTED_PROXIES=127.0.0.1/32,::1/128
SEEK_FORCE_HTTPS=true
SEEK_HSTS_ENABLED=true
```

- `SEEK_TRUSTED_PROXIES` 必须写实际反向代理的 IP/CIDR，不要设置为全网段。
- 只有在 HTTPS 已稳定工作后才开启 HSTS；错误开启会导致浏览器拒绝 HTTP。
- 生产环境建议使用 Redis/网关级限流取代单进程内存限流，并定期更新依赖。
- `.env` 中的 API Key 不要提交到 Git；建议使用部署平台的密钥管理功能。

## AI 可靠汇总（可选）

先跑检测工具，再用大模型把证据汇总成报告（不是让 AI 瞎猜）。

在 `.env` 中配置后**重启服务**：

```bash
SEEK_AI_API_KEY=sk-...
SEEK_AI_BASE_URL=https://api.deepseek.com/v1
SEEK_AI_MODEL=deepseek-chat
```

网页选择 **「AI 可靠汇总」**，或：

```bash
python -m seek.cli ai you@example.com -y
```

---

## 常用配置

复制 `.env.example` 为 `.env` 后按需修改：

| 变量 | 默认 | 说明 |
| --- | --- | --- |
| `SEEK_HOST` / `SEEK_PORT` | `127.0.0.1` / `8000` | 服务地址 |
| `SEEK_CONCURRENCY` | `24` | 并发数；兼顾 100+ 模块速度与 DNS 稳定性 |
| `SEEK_TIMEOUT` | `12` | 普通模块单次超时；User Scanner 多步模块有独立总预算（上游每次请求最多 15 秒） |
| `SEEK_SCAN_PROFILE` | `reliable` | `reliable` 或 `full`；Web UI 默认从完整模式开始 |
| `SEEK_AI_PROFILE` | `reliable` | AI 聚合档位；`full` 会跑 Holehe |
| `SEEK_PROXY` | 空 | 代理，如 `http://127.0.0.1:7890` |
| `SEEK_ALLOWED_DOMAINS` | 空 | 允许查询的邮箱域名（逗号分隔） |
| `SEEK_REQUIRE_CONSENT` | `true` | 是否强制勾选授权声明 |
| `HIBP_API_KEY` | 空 | Have I Been Pwned Key；不填则跳过 |

---

## 新增检测模块

### 方式一：YAML（推荐）

复制 `seek/definitions/_template.yaml`，改名并把 `enabled` 设为 `true`：

```yaml
name: demo_site
title: 示例站点
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
    detail: 该邮箱已注册
  - not_registered_if:
      status_in: [200, 404]
    detail: 未注册
  - rate_limited_if:
      status_in: [429]

default: unknown
```

常用变量：`{email}` `{email_lower}` `{email_md5}` `{email_sha256}` `{local}` `{domain}` `{env.KEY}`

常用判定：`status_in` / `body_contains` / `body_matches` / `json_path_exists` / `json_path_equals` / `json_path_truthy`

需要 CSRF 时用 `prepare` 多步请求，参考 `spotify.yaml`、`duolingo.yaml`。

### 方式二：Python

在 `seek/providers/builtin/` 新建模块，继承 `Provider`，用 `@register` 注册，并在 `builtin/__init__.py` 中 import。

---

## HTTP API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/meta` | 版本、模块数、限流 |
| `GET` | `/api/providers` | 模块列表与就绪状态 |
| `POST` | `/api/scan` | 同步扫描 |
| `GET` | `/api/scan/stream` | SSE 流式扫描 |
| `GET` | `/api/ai/investigate` | AI 汇总（SSE） |

交互式文档：`http://127.0.0.1:8000/docs`

```bash
curl -X POST http://127.0.0.1:8000/api/scan \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"me@example.com\",\"consent\":true}"
```

---

## 结果状态

| 状态 | 含义 |
| --- | --- |
| `registered` | 已注册 |
| `not_registered` | 未注册 |
| `info` | 情报（如 MX），不代表注册状态 |
| `unknown` | 无法判定（改版 / 风控） |
| `rate_limited` | 被限流 |
| `error` | 网络错误或异常 |
| `skipped` | 缺少 API Key 等前置条件 |

---

## 项目结构

```text
seek/
├─ run.py                 # 启动入口
├─ requirements.txt
├─ .env.example
├─ seek/
│  ├─ api.py              # FastAPI + SSE
│  ├─ cli.py
│  ├─ engine.py           # 并发引擎
│  ├─ aggregators.py      # 多工具聚合
│  ├─ ai_agent.py         # AI 汇总
│  ├─ definitions/        # YAML 规则
│  ├─ data/               # 可靠白名单等
│  └─ providers/          # 规则引擎与内置模块
└─ web/                   # 前端（无需构建）
```

---

## License

MIT。使用本工具产生的一切后果由使用者自行承担。
