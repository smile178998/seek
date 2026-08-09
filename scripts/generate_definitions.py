"""批量生成 seek/definitions/*.yaml（基于已知公开检测端点）。

运行：python scripts/generate_definitions.py
不会覆盖已存在的同名文件（除非加 --force）。
"""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "seek" / "definitions"
SKIP = {"gravatar", "gravatar_profile", "hibp", "spotify", "instagram", "pinterest", "duolingo"}


def yaml_block(site: dict) -> str:
    lines = [
        f"name: {site['name']}",
        f"title: {site['title']}",
        f"category: {site['category']}",
        f"homepage: {site['homepage']}",
        f"description: {site['description']}",
        f"notes: {site.get('notes', '端点可能随站点改版失效；仅限本人或已授权目标')}",
    ]
    if site.get("prepare"):
        lines.append("")
        lines.append("prepare:")
        for step in site["prepare"]:
            lines.append(f"  - method: {step['method']}")
            lines.append(f"    url: \"{step['url']}\"")
            if step.get("headers"):
                lines.append("    headers:")
                for k, v in step["headers"].items():
                    lines.append(f"      {k}: \"{v}\"")
            if step.get("save"):
                lines.append("    save:")
                for var, spec in step["save"].items():
                    lines.append(f"      {var}:")
                    for sk, sv in spec.items():
                        if isinstance(sv, bool):
                            lines.append(f"        {sk}: {str(sv).lower()}")
                        else:
                            val = str(sv)
                            if '"' in val:
                                lines.append(f"        {sk}: '{val}'")
                            else:
                                lines.append(f"        {sk}: \"{val}\"")
    lines.append("")
    lines.append("request:")
    req = site["request"]
    lines.append(f"  method: {req['method']}")
    lines.append(f"  url: \"{req['url']}\"")
    if req.get("params"):
        lines.append("  params:")
        for k, v in req["params"].items():
            lines.append(f"    {k}: \"{v}\"")
    if req.get("headers"):
        lines.append("  headers:")
        for k, v in req["headers"].items():
            lines.append(f"    {k}: \"{v}\"")
    if req.get("json"):
        lines.append("  json:")
        for k, v in req["json"].items():
            if v is None:
                lines.append(f"    {k}: null")
            elif isinstance(v, bool):
                lines.append(f"    {k}: {str(v).lower()}")
            else:
                lines.append(f"    {k}: \"{v}\"")
    if req.get("data"):
        if isinstance(req["data"], str):
            s = req["data"]
            if '"' in s:
                lines.append(f"  data: '{s}'")
            else:
                lines.append(f"  data: \"{s}\"")
        else:
            lines.append("  data:")
            for k, v in req["data"].items():
                sv = str(v)
                if '"' in sv:
                    lines.append(f"    {k}: '{sv}'")
                else:
                    lines.append(f"    {k}: \"{sv}\"")
    if req.get("follow_redirects") is False:
        lines.append("  follow_redirects: false")
    lines.append("")
    lines.append("rules:")
    for rule in site["rules"]:
        for action, cond in rule.items():
            if action == "detail":
                continue
            lines.append(f"  - {action}:")
            for ck, cv in cond.items():
                if isinstance(cv, dict):
                    lines.append(f"      {ck}:")
                    for dk, dv in cv.items():
                        if isinstance(dv, bool):
                            lines.append(f"        {dk}: {str(dv).lower()}")
                        elif isinstance(dv, (int, float)):
                            lines.append(f"        {dk}: {dv}")
                        else:
                            lines.append(f"        {dk}: \"{dv}\"")
                elif isinstance(cv, list):
                    def _qitem(x: str) -> str:
                        s = str(x)
                        if '"' in s:
                            return "'" + s.replace("'", "''") + "'"
                        return f'"{s}"'

                    items = ", ".join(_qitem(x) for x in cv)
                    lines.append(f"      {ck}: [{items}]")
                elif isinstance(cv, bool):
                    lines.append(f"      {ck}: {str(cv).lower()}")
                elif isinstance(cv, int):
                    lines.append(f"      {ck}: {cv}")
                else:
                    val = str(cv)
                    if '"' in val:
                        lines.append(f"      {ck}: '{val}'")
                    else:
                        lines.append(f"      {ck}: \"{cv}\"")
            if "detail" in rule:
                lines.append(f"    detail: {rule['detail']}")
    lines.append("")
    lines.append(f"default: {site.get('default', 'unknown')}")
    if site.get("default_detail"):
        lines.append(f"default_detail: {site['default_detail']}")
    if site.get("extract"):
        lines.append("")
        lines.append("extract:")
        for k, v in site["extract"].items():
            lines.append(f"  {k}: \"{v}\"")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# 站点定义（注册查重 / 登录探测 / 公开 API）
# ---------------------------------------------------------------------------
SITES: list[dict] = [
    # --- 社交 ---
    {
        "name": "twitter",
        "title": "Twitter / X",
        "category": "social",
        "homepage": "https://twitter.com",
        "description": "注册邮箱可用性接口（email_available）",
        "request": {
            "method": "GET",
            "url": "https://api.twitter.com/i/users/email_available.json",
            "params": {"email": "{email}"},
            "headers": {"Accept": "application/json"},
        },
        "rules": [
            {"registered_if": {"json_path_truthy": "taken"}, "detail": "邮箱已被占用"},
            {"not_registered_if": {"status_in": [200], "json_path_equals": {"path": "taken", "value": False}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "discord",
        "title": "Discord",
        "category": "social",
        "homepage": "https://discord.com",
        "description": "模拟注册请求，根据 EMAIL_ALREADY_REGISTERED 判断",
        "request": {
            "method": "POST",
            "url": "https://discord.com/api/v9/auth/register",
            "headers": {"Content-Type": "application/json", "Origin": "https://discord.com"},
            "json": {
                "fingerprint": "",
                "email": "{email}",
                "username": "{local}{nonce}",
                "password": "{random_password}",
                "invite": None,
                "consent": True,
                "date_of_birth": "",
            },
        },
        "rules": [
            {"registered_if": {"body_contains": ["EMAIL_ALREADY_REGISTERED"]}, "detail": "邮箱已注册"},
            {"not_registered_if": {"body_contains": ["captcha-required"]}, "detail": "需验证码（视为未触发已注册）"},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "github",
        "title": "GitHub",
        "category": "dev",
        "homepage": "https://github.com",
        "description": "注册页邮箱校验接口 signup_check/email",
        "prepare": [
            {
                "method": "GET",
                "url": "https://github.com/join",
                "save": {
                    "auth_token": {
                        "from": "body_regex",
                        "pattern": 'signup_check/email[\\s\\S]*?value="([^"]+)"',
                        "group": "1",
                    }
                },
            }
        ],
        "request": {
            "method": "POST",
            "url": "https://github.com/signup_check/email",
            "data": {"value": "{email}", "authenticity_token": "{auth_token}"},
        },
        "rules": [
            {"registered_if": {"status_eq": 422}, "detail": "邮箱已被占用"},
            {"not_registered_if": {"status_eq": 200}, "detail": "邮箱可用"},
            {"rate_limited_if": {"body_contains": ["Your browser did something unexpected"]}},
        ],
    },
    {
        "name": "replit",
        "title": "Replit",
        "category": "dev",
        "homepage": "https://replit.com",
        "description": "用户存在性接口 /data/user/exists",
        "request": {
            "method": "POST",
            "url": "https://replit.com/data/user/exists",
            "headers": {"Content-Type": "application/json", "Accept": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"json_path_truthy": "exists"}, "detail": "用户已存在"},
            {"not_registered_if": {"json_path_equals": {"path": "exists", "value": False}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "docker",
        "title": "Docker Hub",
        "category": "dev",
        "homepage": "https://hub.docker.com",
        "description": "注册接口返回邮箱占用提示",
        "request": {
            "method": "POST",
            "url": "https://hub.docker.com/v2/users/signup/",
            "headers": {"Content-Type": "application/json", "Origin": "https://hub.docker.com"},
            "json": {"email": "{email}", "password": "", "recaptcha_response": "", "redirect_value": "", "subscribe": True, "username": ""},
        },
        "rules": [
            {"registered_if": {"body_contains": ["This email is already in use"]}, "detail": "邮箱已注册"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "firefox",
        "title": "Firefox Account",
        "category": "dev",
        "homepage": "https://accounts.firefox.com",
        "description": "Mozilla 账号状态公开接口",
        "request": {
            "method": "POST",
            "url": "https://api.accounts.firefox.com/v1/account/status",
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_matches": "^true$"}, "detail": "账号存在"},
            {"not_registered_if": {"body_matches": "^false$"}, "detail": "账号不存在"},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "flickr",
        "title": "Flickr",
        "category": "media",
        "homepage": "https://flickr.com",
        "description": "登录迁移接口按邮箱查询账号状态",
        "request": {
            "method": "GET",
            "url": "https://identity-api.flickr.com/migration",
            "params": {"email": "{email}"},
            "headers": {"Origin": "https://identity.flickr.com"},
        },
        "rules": [
            {"registered_if": {"json_path_equals": {"path": "state_code", "value": 5}}, "detail": "账号存在"},
            {"not_registered_if": {"status_in": [200, 404]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "imgur",
        "title": "Imgur",
        "category": "social",
        "homepage": "https://imgur.com",
        "description": "注册页邮箱可用性 ajax 接口",
        "prepare": [{"method": "GET", "url": "https://imgur.com/register?redirect=%2Fuser"}],
        "request": {
            "method": "POST",
            "url": "https://imgur.com/signin/ajax_email_available",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://imgur.com",
            },
            "data": {"email": "{email}"},
        },
        "rules": [
            {
                "registered_if": {
                    "status_in": [200],
                    "json_path_equals": {"path": "data.available", "value": False},
                },
                "detail": "邮箱已被占用",
            },
            {
                "not_registered_if": {
                    "json_path_equals": {"path": "data.available", "value": True},
                },
            },
            {"rate_limited_if": {"status_in": [429, 403, 412]}},
        ],
    },
    {
        "name": "strava",
        "title": "Strava",
        "category": "sport",
        "homepage": "https://www.strava.com",
        "description": "注册页 athletes/email_unique 接口",
        "prepare": [
            {
                "method": "GET",
                "url": "https://www.strava.com/register/free?cta=sign-up&element=button&source=website_show",
                "save": {
                    "csrf": {
                        "from": "body_regex",
                        "pattern": '<meta name="csrf-token" content="([^"]+)"',
                        "group": "1",
                    }
                },
            }
        ],
        "request": {
            "method": "GET",
            "url": "https://www.strava.com/athletes/email_unique",
            "params": {"email": "{email}"},
            "headers": {
                "X-CSRF-Token": "{csrf}",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.strava.com/register/free",
            },
        },
        "rules": [
            {"registered_if": {"body_matches": "^false$"}, "detail": "邮箱已注册（email_unique=false）"},
            {"not_registered_if": {"body_matches": "^true$"}, "detail": "邮箱可用"},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "wattpad",
        "title": "Wattpad",
        "category": "social",
        "homepage": "https://www.wattpad.com",
        "description": "用户校验 API v3/users/validate",
        "prepare": [{"method": "GET", "url": "https://www.wattpad.com"}],
        "request": {
            "method": "GET",
            "url": "https://www.wattpad.com/api/v3/users/validate",
            "params": {"email": "{email}"},
            "headers": {"X-Requested-With": "XMLHttpRequest"},
        },
        "rules": [
            {
                "registered_if": {"body_contains": ["already", "Cette adresse", "already in use"]},
                "detail": "邮箱已被占用",
            },
            {
                "not_registered_if": {
                    "status_in": [200, 400],
                    "body_matches": '"message":"OK"',
                },
            },
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "patreon",
        "title": "Patreon",
        "category": "social",
        "homepage": "https://www.patreon.com",
        "description": "注册邮箱可用性 JSON API",
        "request": {
            "method": "POST",
            "url": "https://www.patreon.com/api/email/available",
            "params": {"json-api-version": "1.0", "include": "[]"},
            "headers": {
                "Content-Type": "application/vnd.api+json",
                "Origin": "https://www.patreon.com",
            },
            "data": '{"data":{"attributes":{"email":"{email}"},"relationships":{}}}',
        },
        "rules": [
            {
                "registered_if": {
                    "json_path_equals": {"path": "data.is_available", "value": False},
                },
                "detail": "邮箱已注册",
            },
            {
                "not_registered_if": {
                    "json_path_equals": {"path": "data.is_available", "value": True},
                },
            },
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "devrant",
        "title": "DevRant",
        "category": "dev",
        "homepage": "https://devrant.com",
        "description": "注册 API 返回邮箱占用错误信息",
        "request": {
            "method": "POST",
            "url": "https://devrant.com/api/users",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            },
            "data": {
                "app": "3",
                "type": "1",
                "email": "{email}",
                "username": "",
                "password": "",
                "guid": "",
                "plat": "3",
                "sid": "",
                "seid": "",
            },
        },
        "rules": [
            {
                "registered_if": {
                    "body_contains": ["already registered to an account"],
                },
                "detail": "邮箱已注册",
            },
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "codecademy",
        "title": "Codecademy",
        "category": "edu",
        "homepage": "https://www.codecademy.com",
        "description": "注册校验接口 /register/validate",
        "prepare": [
            {
                "method": "GET",
                "url": "https://www.codecademy.com/register?redirect=%2F",
                "save": {
                    "csrf": {
                        "from": "body_regex",
                        "pattern": 'name="csrf-token" content="([^"]+)"',
                        "group": "1",
                    }
                },
            }
        ],
        "request": {
            "method": "POST",
            "url": "https://www.codecademy.com/register/validate",
            "headers": {
                "Content-Type": "application/json",
                "X-CSRF-Token": "{csrf}",
                "Origin": "https://www.codecademy.com",
            },
            "data": '{"user":{"email":"{email}"}}',
        },
        "rules": [
            {"registered_if": {"body_contains": ["is already taken"]}, "detail": "邮箱已被占用"},
            {"not_registered_if": {"status_in": [200, 422]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "lastfm",
        "title": "Last.fm",
        "category": "music",
        "homepage": "https://www.last.fm",
        "description": "注册页 partial/validate 邮箱校验",
        "prepare": [
            {
                "method": "GET",
                "url": "https://www.last.fm/join",
                "save": {"csrf": {"from": "cookie", "name": "csrftoken"}},
            }
        ],
        "request": {
            "method": "POST",
            "url": "https://www.last.fm/join/partial/validate",
            "headers": {
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.last.fm/join",
                "Cookie": "csrftoken={csrf}",
            },
            "data": {
                "csrfmiddlewaretoken": "{csrf}",
                "userName": "",
                "email": "{email}",
            },
        },
        "rules": [
            {
                "registered_if": {
                    "body_contains": ["already registered to another account"],
                },
                "detail": "邮箱已注册",
            },
            {"not_registered_if": {"status_in": [200]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "protonmail",
        "title": "Proton Mail",
        "category": "mail",
        "homepage": "https://proton.me",
        "description": "Proton 公开 PKS 索引查询（info:1:1=存在）",
        "request": {
            "method": "GET",
            "url": "https://api.protonmail.ch/pks/lookup",
            "params": {"op": "index", "search": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["info:1:1"]}, "detail": "该邮箱在 Proton 有密钥记录"},
            {"not_registered_if": {"body_contains": ["info:1:0"]}, "detail": "未找到 Proton 密钥"},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "tellonym",
        "title": "Tellonym",
        "category": "social",
        "homepage": "https://tellonym.me",
        "description": "账号检查接口 accounts/check",
        "request": {
            "method": "GET",
            "url": "https://api.tellonym.me/accounts/check",
            "params": {"email": "{email}"},
            "headers": {"Accept": "application/json"},
        },
        "rules": [
            {"registered_if": {"json_path_truthy": "exists"}, "detail": "账号存在"},
            {"not_registered_if": {"json_path_equals": {"path": "exists", "value": False}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "vsco",
        "title": "VSCO",
        "category": "social",
        "homepage": "https://vsco.co",
        "description": "用户邮箱查询 API",
        "request": {
            "method": "GET",
            "url": "https://api.vsco.co/2.0/users/email",
            "params": {"email": "{email}"},
            "headers": {"Accept": "application/json"},
        },
        "rules": [
            {"registered_if": {"status_in": [200], "json_path_exists": "user"}, "detail": "用户存在"},
            {"not_registered_if": {"status_in": [404]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "plurk",
        "title": "Plurk",
        "category": "social",
        "homepage": "https://www.plurk.com",
        "description": "邮箱是否已注册 isEmailFound",
        "request": {
            "method": "POST",
            "url": "https://www.plurk.com/Users/isEmailFound",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            },
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["true", "found"]}, "detail": "邮箱已找到"},
            {"not_registered_if": {"body_contains": ["false", "not found"]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "xing",
        "title": "Xing",
        "category": "social",
        "homepage": "https://www.xing.com",
        "description": "注册校验 API signup/validate",
        "prepare": [{"method": "GET", "url": "https://www.xing.com/start/signup?registration=1"}],
        "request": {
            "method": "POST",
            "url": "https://www.xing.com/welcome/api/signup/validate",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "wordpress",
        "title": "WordPress.com",
        "category": "dev",
        "homepage": "https://wordpress.com",
        "description": "注册邮箱校验接口",
        "request": {
            "method": "POST",
            "url": "https://public-api.wordpress.com/rest/v1.1/users/validate",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "archive",
        "title": "Archive.org",
        "category": "media",
        "homepage": "https://archive.org",
        "description": "账号服务邮箱检查",
        "request": {
            "method": "POST",
            "url": "https://archive.org/account/signup",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"input_mail": "{email}", "input_password": "{random_password}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "in use", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "envato",
        "title": "Envato",
        "category": "shop",
        "homepage": "https://envato.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://account.envato.com/api/public/sign_up",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}", "password": "{random_password}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400, 422]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "eventbrite",
        "title": "Eventbrite",
        "category": "other",
        "homepage": "https://www.eventbrite.com",
        "description": "注册邮箱可用性",
        "request": {
            "method": "GET",
            "url": "https://www.eventbrite.com/api/v3/users/email_available/",
            "params": {"email": "{email}"},
            "headers": {"Accept": "application/json"},
        },
        "rules": [
            {"registered_if": {"json_path_equals": {"path": "available", "value": False}}},
            {"not_registered_if": {"json_path_equals": {"path": "available", "value": True}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "komoot",
        "title": "Komoot",
        "category": "sport",
        "homepage": "https://www.komoot.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://account.komoot.com/v1/signup",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}", "password": "{random_password}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "smule",
        "title": "Smule",
        "category": "music",
        "homepage": "https://www.smule.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://www.smule.com/a/account/email/check",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "teamtreehouse",
        "title": "Team Treehouse",
        "category": "edu",
        "homepage": "https://teamtreehouse.com",
        "description": "注册邮箱校验",
        "prepare": [{"method": "GET", "url": "https://teamtreehouse.com/subscribe/new"}],
        "request": {
            "method": "POST",
            "url": "https://teamtreehouse.com/subscribe/new.json",
            "headers": {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "trello",
        "title": "Trello",
        "category": "dev",
        "homepage": "https://trello.com",
        "description": "Atlassian 账号邮箱校验（Trello 注册页）",
        "request": {
            "method": "GET",
            "url": "https://trello.com/1/account/exists",
            "params": {"email": "{email}"},
            "headers": {"Accept": "application/json"},
        },
        "rules": [
            {"registered_if": {"json_path_equals": {"path": "exists", "value": True}}},
            {"not_registered_if": {"json_path_equals": {"path": "exists", "value": False}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "venmo",
        "title": "Venmo",
        "category": "payment",
        "homepage": "https://venmo.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://venmo.com/api/v5/users",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}", "password": "{random_password}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400, 422]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "vivino",
        "title": "Vivino",
        "category": "shop",
        "homepage": "https://www.vivino.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://www.vivino.com/api/users/check_email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "zoho",
        "title": "Zoho",
        "category": "crm",
        "homepage": "https://www.zoho.com",
        "description": "账号邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://accounts.zoho.com/signup/validate/email",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "hubspot",
        "title": "HubSpot",
        "category": "crm",
        "homepage": "https://www.hubspot.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://api.hubspot.com/signup/v1/signup/email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "pipedrive",
        "title": "Pipedrive",
        "category": "crm",
        "homepage": "https://www.pipedrive.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://www.pipedrive.com/api/v1/users/validate_email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "freelancer",
        "title": "Freelancer",
        "category": "jobs",
        "homepage": "https://www.freelancer.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://www.freelancer.com/api/users/0.1/users/email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "issuu",
        "title": "Issuu",
        "category": "media",
        "homepage": "https://issuu.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://issuu.com/signup/check_email",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "nike",
        "title": "Nike",
        "category": "shop",
        "homepage": "https://www.nike.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://api.nike.com/identity/user/v1/validation/email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "garmin",
        "title": "Garmin",
        "category": "shop",
        "homepage": "https://www.garmin.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://www.garmin.com/api/customer/email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "anydo",
        "title": "Any.do",
        "category": "dev",
        "homepage": "https://www.any.do",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://sm-prod2.any.do/check_email",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "diigo",
        "title": "Diigo",
        "category": "social",
        "homepage": "https://www.diigo.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://www.diigo.com/sign_in/check_email",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "ello",
        "title": "Ello",
        "category": "social",
        "homepage": "https://ello.co",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://ello.co/api/v2/email_available",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"json_path_equals": {"path": "available", "value": False}}},
            {"not_registered_if": {"json_path_equals": {"path": "available", "value": True}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "fanpop",
        "title": "Fanpop",
        "category": "social",
        "homepage": "https://www.fanpop.com",
        "description": "登录 superlogin 探测账号",
        "request": {
            "method": "POST",
            "url": "https://www.fanpop.com/login/superlogin",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}", "password": "{random_password}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["password", "incorrect", "wrong"]}, "detail": "账号存在（密码错误）"},
            {"not_registered_if": {"body_contains": ["not found", "no account", "invalid"]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "myspace",
        "title": "Myspace",
        "category": "social",
        "homepage": "https://myspace.com",
        "description": "注册邮箱 validateemail",
        "prepare": [{"method": "GET", "url": "https://myspace.com/signup/email"}],
        "request": {
            "method": "POST",
            "url": "https://myspace.com/ajax/account/validateemail",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Origin": "https://myspace.com",
            },
            "data": {"email": "{email}"},
        },
        "rules": [
            {
                "registered_if": {
                    "body_contains": ["already used to create an account"],
                },
                "detail": "邮箱已注册",
            },
            {"not_registered_if": {"status_in": [200]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "snapchat",
        "title": "Snapchat",
        "category": "social",
        "homepage": "https://www.snapchat.com",
        "description": "账号注册邮箱校验（accounts.snapchat.com）",
        "prepare": [{"method": "GET", "url": "https://accounts.snapchat.com"}],
        "request": {
            "method": "POST",
            "url": "https://accounts.snapchat.com/accounts/check_email",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "tumblr",
        "title": "Tumblr",
        "category": "social",
        "homepage": "https://www.tumblr.com",
        "description": "注册 account/validate 邮箱校验",
        "prepare": [{"method": "GET", "url": "https://www.tumblr.com/"}],
        "request": {
            "method": "POST",
            "url": "https://www.tumblr.com/api/v2/register/account/validate",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "yahoo",
        "title": "Yahoo Mail",
        "category": "mail",
        "homepage": "https://mail.yahoo.com",
        "description": "登录页用户名探测（登录流程第一步）",
        "prepare": [{"method": "GET", "url": "https://login.yahoo.com"}],
        "request": {
            "method": "POST",
            "url": "https://login.yahoo.com/",
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
            },
            "data": {"username": "{email}", "passwd": "", "signin": "Next", "persistent": "y"},
        },
        "rules": [
            {
                "registered_if": {
                    "body_matches": '"error":\\s*false',
                },
                "detail": "账号存在（进入密码/验证步骤）",
            },
            {
                "not_registered_if": {
                    "body_contains": ["ERROR_INVALID_USERNAME", "not found"],
                },
            },
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "google",
        "title": "Google",
        "category": "mail",
        "homepage": "https://accounts.google.com",
        "description": "注册用户名可用性（gf.wuar 标记）",
        "notes": "Google 风控极强，常返回无法判定；接口随改版变化快",
        "prepare": [
            {
                "method": "GET",
                "url": "https://accounts.google.com/signup/v2/webcreateaccount?flowName=GlifWebSignIn&flowEntry=SignUp",
            }
        ],
        "request": {
            "method": "POST",
            "url": "https://accounts.google.com/_/signup/webusernameavailability",
            "params": {"hl": "en", "rt": "j"},
            "headers": {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://accounts.google.com",
            },
            "data": {
                "continue": "https://accounts.google.com/",
                "f.req": '["","","","{email}",false]',
            },
        },
        "rules": [
            {"registered_if": {"body_matches": '"gf.wuar",2'}, "detail": "邮箱已占用"},
            {"not_registered_if": {"body_matches": '"gf.wuar",1', "body_contains": ["EmailInvalid"]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "adobe",
        "title": "Adobe",
        "category": "dev",
        "homepage": "https://www.adobe.com",
        "description": "找回密码流程探测（存在则返回挑战信息）",
        "request": {
            "method": "POST",
            "url": "https://auth.services.adobe.com/signin/v1/authenticationstate",
            "headers": {
                "Content-Type": "application/json",
                "X-IMS-CLIENTID": "adobedotcom2",
                "Origin": "https://auth.services.adobe.com",
            },
            "json": {"username": "{email}", "accountType": "individual"},
        },
        "rules": [
            {"registered_if": {"json_path_exists": "id"}, "detail": "账号存在（进入验证流程）"},
            {"not_registered_if": {"body_contains": ["errorCode", "not found"]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "evernote",
        "title": "Evernote",
        "category": "dev",
        "homepage": "https://evernote.com",
        "description": "登录页用户名探测",
        "prepare": [{"method": "GET", "url": "https://www.evernote.com/Login.action"}],
        "request": {
            "method": "POST",
            "url": "https://www.evernote.com/Login.action",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"username": "{email}", "evaluateUsername": ""},
        },
        "rules": [
            {"registered_if": {"body_contains": ["usePasswordAuth"]}, "detail": "账号存在"},
            {"not_registered_if": {"body_contains": ["displayMessage", "not found"]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "amazon",
        "title": "Amazon",
        "category": "shop",
        "homepage": "https://www.amazon.com",
        "description": "登录页邮箱探测（auth-password-missing-alert）",
        "notes": "需跟随登录页表单字段，改版频繁",
        "prepare": [
            {
                "method": "GET",
                "url": "https://www.amazon.com/ap/signin?openid.mode=checkid_setup",
            }
        ],
        "request": {
            "method": "POST",
            "url": "https://www.amazon.com/ap/signin/",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {
                "registered_if": {"body_contains": ["auth-password-missing-alert", "password"]},
                "detail": "账号存在（要求输入密码）",
            },
            {"not_registered_if": {"body_contains": ["cannot find an account", "not found"]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "ebay",
        "title": "eBay",
        "category": "shop",
        "homepage": "https://www.ebay.com",
        "description": "注册邮箱校验",
        "request": {
            "method": "POST",
            "url": "https://signup.ebay.com/ajax/user",
            "headers": {"Content-Type": "application/json"},
            "json": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"body_contains": ["already", "taken", "exists"]}, "detail": "邮箱已占用"},
            {"not_registered_if": {"status_in": [200, 400]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "quora",
        "title": "Quora",
        "category": "edu",
        "homepage": "https://www.quora.com",
        "description": "注册邮箱 validate server_call",
        "prepare": [{"method": "GET", "url": "https://www.quora.com"}],
        "request": {
            "method": "POST",
            "url": "https://www.quora.com/webnode2/server_call_POST",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {
                "json": '{"args":[],"kwargs":{"value":"{email}"}}',
                "__method": "validate",
            },
        },
        "rules": [
            {
                "registered_if": {
                    "body_contains": ["already", "account", "taken", "compte"],
                },
                "detail": "邮箱已占用",
            },
            {"not_registered_if": {"status_in": [200]}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
    {
        "name": "reddit",
        "title": "Reddit",
        "category": "social",
        "homepage": "https://www.reddit.com",
        "description": "注册邮箱可用性",
        "request": {
            "method": "POST",
            "url": "https://www.reddit.com/api/check_email.json",
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": {"email": "{email}"},
        },
        "rules": [
            {"registered_if": {"json_path_equals": {"path": "valid", "value": False}}},
            {"not_registered_if": {"json_path_equals": {"path": "valid", "value": True}}},
            {"rate_limited_if": {"status_in": [429, 403]}},
        ],
    },
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="覆盖已存在的 yaml")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    created, skipped = 0, 0
    for site in SITES:
        name = site["name"]
        if name in SKIP:
            skipped += 1
            continue
        path = OUT / f"{name}.yaml"
        if path.exists() and not args.force:
            skipped += 1
            continue
        path.write_text(yaml_block(site), encoding="utf-8")
        created += 1
    print(f"写入 {created} 个规则，跳过 {skipped} 个（已存在或在 SKIP 列表）")


if __name__ == "__main__":
    main()
