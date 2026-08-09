from __future__ import annotations

import hashlib
import re
import secrets
import string
from typing import Any
from urllib.parse import quote

from email_validator import EmailNotValidError, validate_email

_VAR_RE = re.compile(r"\{([A-Za-z0-9_.]+)\}")


class TemplateError(KeyError):
    """规则里引用了上下文中不存在的变量。"""


class InvalidEmail(ValueError):
    pass


def normalize_email(raw: str) -> str:
    """校验语法并返回归一化后的邮箱（不做投递性检测，避免额外网络请求）。"""
    try:
        info = validate_email(raw.strip(), check_deliverability=False)
    except EmailNotValidError as exc:
        raise InvalidEmail(str(exc)) from exc
    return info.normalized


def split_email(email: str) -> tuple[str, str]:
    local, _, domain = email.rpartition("@")
    return local, domain


def _digest(algo: str, value: str) -> str:
    return hashlib.new(algo, value.strip().lower().encode("utf-8")).hexdigest()


def build_context(email: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    """构造模板上下文。规则中可用 {email}、{email_sha256}、{domain}、{env.KEY} 等。"""
    local, domain = split_email(email)
    ctx: dict[str, Any] = {
        "email": email,
        "email_lower": email.lower(),
        "email_urlenc": quote(email, safe=""),
        "email_md5": _digest("md5", email),
        "email_sha1": _digest("sha1", email),
        "email_sha256": _digest("sha256", email),
        "local": local,
        "local_urlenc": quote(local, safe=""),
        "domain": domain,
        "nonce": secrets.token_hex(8),
        "random_password": random_password(),
    }
    if extra:
        ctx.update(extra)
    return ctx


def random_password(length: int = 16) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length)) + "!aA1"


def render(template: str, ctx: dict[str, Any]) -> str:
    """把 `{var}` 占位符替换为上下文值，缺失即抛错（便于提前发现规则问题）。"""

    def _sub(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in ctx:
            return str(ctx[key])
        raise TemplateError(key)

    return _VAR_RE.sub(_sub, template)


def render_mapping(mapping: dict[str, str], ctx: dict[str, Any]) -> dict[str, str]:
    return {render(k, ctx): render(v, ctx) for k, v in mapping.items()}


def render_any(value: Any, ctx: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return render(value, ctx)
    if isinstance(value, dict):
        return {render_any(k, ctx): render_any(v, ctx) for k, v in value.items()}
    if isinstance(value, list):
        return [render_any(v, ctx) for v in value]
    return value


def json_path(data: Any, path: str) -> Any:
    """点号路径取值，支持数字下标与 `[]` 通配（对列表逐项收集）。

    例：`data.0.name`、`[].Name`、`items[].id`
    """
    current: Any = data
    for token in [t for t in path.replace("[]", ".[].").split(".") if t]:
        if token == "[]":
            if not isinstance(current, list):
                return None
            current = list(current)
            continue
        if isinstance(current, list) and not token.isdigit():
            collected = [_get_key(item, token) for item in current]
            current = [c for c in collected if c is not None]
            continue
        current = _get_key(current, token)
        if current is None:
            return None
    return current


def _get_key(container: Any, token: str) -> Any:
    if isinstance(container, dict):
        return container.get(token)
    if isinstance(container, list) and token.isdigit():
        index = int(token)
        return container[index] if index < len(container) else None
    return None


def mask_email(email: str) -> str:
    local, domain = split_email(email)
    if len(local) <= 2:
        hidden = local[0] + "*" if local else "*"
    else:
        hidden = f"{local[0]}{'*' * (len(local) - 2)}{local[-1]}"
    return f"{hidden}@{domain}"
