"""快捷启动入口：python run.py 即可拉起 Web 服务。"""

from __future__ import annotations

import uvicorn

from seek.config import get_settings


def main() -> None:
    settings = get_settings()
    print(f"seek 已启动 -> http://{settings.host}:{settings.port}")
    uvicorn.run(
        "seek.api:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        server_header=False,
        proxy_headers=settings.trust_proxy_headers,
        forwarded_allow_ips=(
            settings.trusted_proxies if settings.trust_proxy_headers else ""
        ),
    )


if __name__ == "__main__":
    main()
