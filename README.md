# seek · 邮箱注册痕迹反查框架

一个类似 [Holehe](https://github.com/megadose/holehe) 的邮箱 OSINT 工具，但重点放在**可扩展的规则引擎**上：
检测逻辑用 YAML 声明，不用改代码就能新增站点；同时提供 Web 界面、命令行和 HTTP API。

```
输入邮箱  ─▶  并发调度引擎  ─▶  ┌ 内置 Python 模块（DNS / MX / 一次性邮箱）
                              └ YAML 规则模块（Gravatar / HIBP / 你自己加的站点）
                                        │
                              流式回传（SSE）─▶ Web UI / CLI / JSON
```

---

## ⚠️ 使用前必读

本项目仅面向**两种合法场景**：

1. 梳理**自己**的邮箱在哪些平台留下了注册痕迹；
2. 在**已取得书面授权**的渗透测试 / 红队评估中做资产收集。

未经授权对他人邮箱进行探测，在中国大陆可能违反《个人信息保护法》《网络安全法》，
在欧盟涉及 GDPR，同时几乎必然违反目标站点的服务条款。**风险与法律责任由使用者自行承担。**

框架自带两层检测能力：

1. **官方公开接口层**：Gravatar 公开头像与资料 API、Have I Been Pwned 官方 API、公开 DNS / MX 记录。稳定可靠。
2. **本项目自维护的枚举规则层**（`seek/definitions/*.yaml`）：目前包含 Spotify、Duolingo、Instagram、Pinterest 等，每条规则都写明依据。新增站点只需照 `_template.yaml` 写一个 YAML。
3. **Holehe 集成层（默认关闭）**：可选集成开源工具 [Holehe](https://github.com/megadose/holehe) 的约 120 个站点模块。因其多数模块已随站点改版失效或被反爬拦截，默认不加载；需要长尾覆盖时设 `SEEK_ENABLE_HOLEHE=true` 开启。

### 关于「一百多个网站，完全正常」的现实

必须坦白：没有任何工具能保证对 120 个第三方站点**全部稳定命中**——Holehe 本身也做不到。原因是各大站点普遍上了反爬（Cloudflare、验证码、IP 限流）。实测里你会看到相当一部分站点返回：

- `被限流`（HTTP 429 / 被风控拦截）—— 换出口 IP、降并发、隔一会儿再试可能缓解；
- `无法判定`（接口已改版，规则失配）—— 需要更新对应端点。

**真正稳定命中的是官方接口层**（HIBP 能反查该邮箱出现在数百个已知泄露库中，这是覆盖面最广且最可靠的信号）。Holehe 层是「尽力而为」的补充，请把它的结果当线索而非定论。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt
pip install holehe          # 可选：启用约 120 个站点的探测模块

# 2. 配置（可选，但建议）
copy .env.example .env      # Windows
# cp .env.example .env      # Linux / macOS

# 3. 启动 Web 界面
python run.py               # 打开 http://127.0.0.1:8000

# 或者用命令行
python -m seek.cli providers            # 查看所有模块
python -m seek.cli scan me@example.com  # 扫描
```

### AI 全工具汇总（可选）

流程不是「让 AI 猜」，而是：

1. **并行跑齐**同类工具：本项目规则引擎 + Holehe（约 120 站）+ Gravatar + 公开网页搜索 +（可选）socialscan  
2. 再用你的 **OpenAI 兼容 API Key** 把证据汇总成「已确认 / 疑似」报告  

在 `.env` 配置后重启：

```bash
SEEK_AI_API_KEY=sk-...
SEEK_AI_BASE_URL=https://api.openai.com/v1   # DeepSeek: https://api.deepseek.com/v1
SEEK_AI_MODEL=gpt-4o-mini                    # 或 deepseek-chat
```

建议同时安装聚合用到的后端：

```bash
pip install holehe
pip install socialscan   # 可选
```

网页点 **「AI 全工具汇总」**，或：`python -m seek.cli ai you@example.com -y`  
费用走大模型账单；**仍无法保证覆盖全世界所有网站**。

### 命令行用法

```bash
# 只跑某些分类或模块
python -m seek.cli scan me@example.com --only domain,gravatar

# 排除某些模块，显示全部结果（含未注册），并导出
python -m seek.cli scan me@example.com -x hibp --all --output result.json

# 机器可读输出
python -m seek.cli scan me@example.com --json -y

# 启动服务（等价于 python run.py）
python -m seek.cli serve --port 8080 --reload
```

---

## 配置项

所有配置都可以放在 `.env` 里，或作为环境变量传入。

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `SEEK_HOST` / `SEEK_PORT` | `127.0.0.1` / `8000` | Web 服务监听地址 |
| `SEEK_CONCURRENCY` | `12` | 并发请求数 |
| `SEEK_TIMEOUT` | `12` | 单模块超时（秒） |
| `SEEK_PROXY` | 空 | 出口代理，如 `http://127.0.0.1:7890` |
| `SEEK_ALLOWED_DOMAINS` | 空 | **建议设置**：只允许查询这些邮箱域名，逗号分隔。留空 = 不限制 |
| `SEEK_REQUIRE_CONSENT` | `true` | 是否强制前端勾选授权声明 |
| `SEEK_RATE_LIMIT_SCANS` | `12` | 单 IP 在窗口内的最大扫描次数 |
| `SEEK_RATE_LIMIT_WINDOW` | `600` | 限流窗口长度（秒） |
| `HIBP_API_KEY` | 空 | HIBP 官方 API Key，不填则该模块自动跳过 |

把 `SEEK_ALLOWED_DOMAINS` 设成自己的域名，就能把这个服务约束成纯粹的「自查工具」。

---

## 新增一个检测模块

### 方式一：写 YAML 规则（推荐）

复制 `seek/definitions/_template.yaml`，改名后把 `enabled` 设为 `true` 即可。最小示例：

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

**可用模板变量**：`{email}` `{email_lower}` `{email_urlenc}` `{email_md5}` `{email_sha1}`
`{email_sha256}` `{local}` `{local_urlenc}` `{domain}` `{nonce}` `{random_password}` `{env.KEY}`

**可用判定子句**（同一条规则内为 AND 关系，规则之间自上而下短路匹配）：

| 子句 | 含义 |
| --- | --- |
| `status_in: [200, 302]` | HTTP 状态码属于列表 |
| `status_eq: 200` | 状态码等于 |
| `body_contains: ["a","b"]` | 响应体同时包含所有项 |
| `body_not_contains: ["err"]` | 响应体不包含任何一项 |
| `body_matches: "user\\s+exists"` | 正则匹配（忽略大小写、跨行） |
| `json_path_exists: "data.id"` | JSON 路径存在且非 null |
| `json_path_truthy: "data.exists"` | JSON 路径取值为真 |
| `json_path_equals: {path: ..., value: ...}` | JSON 路径取值等于 |
| `header_contains: {name: Location, value: "/login"}` | 响应头包含子串 |

**动作**：`registered_if` / `not_registered_if` / `info_if` / `rate_limited_if` / `error_if`

`extract` 段可以把响应里的字段带回结果（JSON 路径支持数字下标和 `[]` 通配，如 `[].Name`、`entry.0.accounts[].shortname`）。

需要 API Key 的模块在 `requires` 里声明变量名，缺失时该模块会自动标记为「跳过」，不会拖慢整体扫描。

#### 账号枚举与两步请求

Holehe 类工具的核心手法，是利用站点**注册页 / 找回密码页**的邮箱查重接口：同一个邮箱是否已注册，
接口会返回不同响应，据此判断。本引擎原生支持这套流程；很多站点还需要先取 CSRF token，用 `prepare`
段做多步请求：

```yaml
prepare:
  - method: GET
    url: "https://example.com/signup"          # 先访问注册页
    save:
      csrf: { from: cookie, name: csrftoken }   # 从 Set-Cookie 里取 token

request:
  method: POST
  url: "https://example.com/api/email/exists"
  headers:
    X-CSRFToken: "{csrf}"                        # 带上刚取到的 token
  data:
    email: "{email}"
```

`save` 支持四种取值来源：`cookie`（按 `name`）、`header`（按 `name`）、`json`（按 `path`）、
`body_regex`（按 `pattern` + 可选 `group`）。`prepare` 里种下的 cookie 会由同一会话自动带到后续请求。

内置的 `spotify` / `instagram` / `pinterest` 就是这类枚举规则的实例，可作为写新规则的参考。

> **端点会失效**：站点随时可能改接口、加验证码或风控。规则跑出 `unknown` 往往就是接口变了。
> 维护规则的正确姿势——用浏览器 F12 的 Network 面板，在目标站点注册 / 找回密码页输入一个邮箱，
> 看它真正请求的是哪个接口、请求体长啥样、已注册与未注册时响应差在哪，再照着填进 YAML。

### 方式二：写 Python 模块

适合需要自定义逻辑（多步请求、非 HTTP 协议等）的场景。在 `seek/providers/builtin/` 下新建文件：

```python
from ...models import ProviderInfo, Result, Status
from ..base import CheckContext, Provider, Timer
from . import register

class MySiteProvider(Provider):
    def __init__(self) -> None:
        super().__init__(ProviderInfo(
            name="mysite", title="我的站点", category="social", kind="builtin",
        ))

    async def check(self, ctx: CheckContext) -> Result:
        with Timer() as t:
            resp = await ctx.client.post(
                "https://mysite.example/api/exists",
                json={"email": ctx.email}, timeout=ctx.timeout,
            )
        status = Status.REGISTERED if resp.json().get("exists") else Status.NOT_REGISTERED
        return self.make_result(status, elapsed_ms=t.elapsed_ms, http_status=resp.status_code)

@register
def _factory() -> Provider:
    return MySiteProvider()
```

最后在 `builtin/__init__.py` 底部 import 你的新文件即可（与 `dns_checks` 同理）。

---

## HTTP API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/api/meta` | 版本、模块数量、分类、限流额度 |
| `GET` | `/api/providers` | 所有模块及其就绪状态 |
| `POST` | `/api/scan` | 同步扫描，一次性返回全部结果 |
| `GET` | `/api/scan/stream` | SSE 流式扫描，结果逐条推送 |

交互式文档在 `/docs`。

```bash
curl -X POST http://127.0.0.1:8000/api/scan ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"me@example.com\",\"consent\":true}"
```

SSE 事件序列：`start` → 多个 `result` → `summary`，出错时下发 `error`。

---

## 结果状态说明

| 状态 | 含义 |
| --- | --- |
| `registered` | 判定为已注册 |
| `not_registered` | 判定为未注册 |
| `info` | 情报类结果（如 MX 记录、泄露事件），不代表注册状态 |
| `unknown` | 响应不匹配任何规则，通常意味着站点改版或被风控 |
| `rate_limited` | 被目标站点限流，建议降低并发或换出口 IP |
| `error` | 网络错误、超时或模块异常 |
| `skipped` | 缺少所需 API Key 等前置条件 |

结果是**探测推断**，不是事实断言。CDN 缓存、风控策略、站点改版都会造成误报或漏报，
请勿把单一模块的输出当作结论。

---

## 项目结构

```
seek/
├─ run.py                     快捷启动入口
├─ requirements.txt
├─ .env.example
├─ seek/
│  ├─ api.py                  FastAPI 路由 + SSE + 限流
│  ├─ cli.py                  命令行入口
│  ├─ engine.py               并发调度引擎
│  ├─ models.py               数据模型与状态定义
│  ├─ config.py               配置加载
│  ├─ utils.py                模板渲染 / 哈希 / JSON 路径
│  ├─ ratelimit.py            滑动窗口限流
│  ├─ data/                   一次性邮箱域名库
│  ├─ definitions/            YAML 规则（含 _template.yaml 模板）
│  └─ providers/
│     ├─ base.py              Provider 基类
│     ├─ declarative.py       YAML 规则引擎
│     ├─ registry.py          模块加载与筛选
│     └─ builtin/             内置 Python 模块
└─ web/                       前端（无需构建，原生 HTML/CSS/JS）
```

## License

MIT。使用本工具产生的一切后果由使用者自行承担。
#   s e e k  
 