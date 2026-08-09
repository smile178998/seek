from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .config import get_settings
from .engine import Engine
from .models import STATUS_LABEL, Result, Status
from .providers.registry import load_providers
from .utils import InvalidEmail, normalize_email, split_email

app = typer.Typer(
    add_completion=False,
    help="seek —— 邮箱注册痕迹反查工具。仅限用于本人邮箱或已获授权的目标。",
)
console = Console()

STATUS_STYLE = {
    Status.REGISTERED: "bold green",
    Status.INFO: "cyan",
    Status.NOT_REGISTERED: "dim",
    Status.UNKNOWN: "yellow",
    Status.RATE_LIMITED: "yellow",
    Status.ERROR: "red",
    Status.SKIPPED: "bright_black",
}


@app.command("providers")
def cmd_providers() -> None:
    """列出所有检测模块。"""
    table = Table(title="检测模块", header_style="bold")
    table.add_column("标识")
    table.add_column("名称")
    table.add_column("分类")
    table.add_column("类型")
    table.add_column("状态")
    for provider in load_providers():
        info = provider.info
        table.add_row(
            info.name,
            info.title,
            info.category,
            "内置" if info.kind == "builtin" else "规则",
            "[green]就绪[/]" if info.ready else f"[yellow]{info.unready_reason}[/]",
        )
    console.print(table)


@app.command("scan")
def cmd_scan(
    email: str = typer.Argument(..., help="要查询的邮箱"),
    only: Optional[str] = typer.Option(None, "--only", "-o", help="仅运行这些模块/分类，逗号分隔"),
    exclude: Optional[str] = typer.Option(None, "--exclude", "-x", help="排除这些模块/分类"),
    output: Optional[Path] = typer.Option(None, "--output", help="把完整结果写入 JSON 文件"),
    as_json: bool = typer.Option(False, "--json", help="直接把 JSON 打印到 stdout"),
    show_all: bool = typer.Option(False, "--all", "-a", help="同时显示未注册/跳过的条目"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过授权确认"),
) -> None:
    """对单个邮箱执行全部检测。"""
    try:
        normalized = normalize_email(email)
    except InvalidEmail as exc:
        console.print(f"[red]邮箱格式不正确：{exc}[/]")
        raise typer.Exit(2)

    settings = get_settings()
    _local, domain = split_email(normalized)
    if not settings.is_domain_allowed(domain):
        console.print(f"[red]域名 {domain} 不在 SEEK_ALLOWED_DOMAINS 允许列表内[/]")
        raise typer.Exit(3)

    if not yes and not as_json:
        console.print(
            "[yellow]请确认：仅对本人邮箱或已获得书面授权的目标进行查询。[/]"
        )
        if not typer.confirm("继续？", default=False):
            raise typer.Exit(1)

    def parse(value: Optional[str]) -> list[str]:
        return [p.strip() for p in (value or "").split(",") if p.strip()]

    response = asyncio.run(_run(normalized, parse(only), parse(exclude)))

    if as_json:
        console.print_json(response.model_dump_json())
    else:
        _print_table(response.results, show_all)
        s = response.summary
        console.print(
            f"\n共 {s.total} 项 · [bold green]已注册 {s.registered}[/] · "
            f"[cyan]情报 {s.info}[/] · [yellow]无法判定 {s.unknown}[/] · "
            f"未注册 {s.not_registered} · [red]失败 {s.error + s.rate_limited}[/] · "
            f"跳过 {s.skipped} · 耗时 {s.elapsed_ms / 1000:.1f}s"
        )

    if output:
        output.write_text(
            json.dumps(response.model_dump(mode="json"), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        console.print(f"[green]结果已写入 {output}[/]")


async def _run(email: str, only: list[str], exclude: list[str]):
    async with Engine() as engine:
        return await engine.scan(email, only, exclude)


def _print_table(results: list[Result], show_all: bool) -> None:
    hidden = {Status.NOT_REGISTERED, Status.SKIPPED}
    rows = results if show_all else [r for r in results if r.status not in hidden]

    table = Table(header_style="bold", show_lines=False)
    table.add_column("状态", width=8)
    table.add_column("站点", width=22)
    table.add_column("说明", overflow="fold")
    table.add_column("附加信息", overflow="fold")
    table.add_column("耗时", justify="right", width=7)

    for r in rows:
        style = STATUS_STYLE.get(r.status, "")
        extras = " ".join(
            f"{k}={', '.join(map(str, v)) if isinstance(v, list) else v}"
            for k, v in (r.data or {}).items()
        )
        table.add_row(
            f"[{style}]{STATUS_LABEL[r.status]}[/]",
            r.title,
            r.detail or "",
            extras,
            f"{r.elapsed_ms}ms",
        )
    console.print(table)
    if not show_all and len(rows) < len(results):
        console.print(f"[dim]已隐藏 {len(results) - len(rows)} 条未注册/跳过结果，加 --all 查看[/]")


@app.command("prune-holehe")
def cmd_prune_holehe(
    email: str = typer.Argument(..., help="用于探测各模块是否有效的邮箱（建议用本人邮箱）"),
    include_rate_limited: bool = typer.Option(
        False, "--include-rate-limited", help="连同「被限流/被拦截」的模块一起禁用"
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="只打印结果，不写入禁用清单"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过授权确认"),
) -> None:
    """跑一次全量扫描，把失效的 holehe 模块写入禁用清单（按你的网络环境自我校准）。

    判定规则：返回「已注册/未注册/情报」视为有效；「无法判定/失败」视为失效。
    「被限流」默认保留（可能是暂时性的），加 --include-rate-limited 一并禁用。
    """
    try:
        normalized = normalize_email(email)
    except InvalidEmail as exc:
        console.print(f"[red]邮箱格式不正确：{exc}[/]")
        raise typer.Exit(2)

    if not yes:
        console.print("[yellow]将对该邮箱发起一次全量探测以评估各模块有效性。[/]")
        if not typer.confirm("继续？", default=False):
            raise typer.Exit(1)

    settings = get_settings()
    response = asyncio.run(_run(normalized, [], []))

    working = {Status.REGISTERED, Status.NOT_REGISTERED, Status.INFO}
    dead = {Status.UNKNOWN, Status.ERROR}
    if include_rate_limited:
        dead = dead | {Status.RATE_LIMITED}

    to_disable: list[str] = []
    kept = 0
    for r in response.results:
        if not r.provider.startswith("holehe_"):
            continue
        short = r.provider[len("holehe_") :]
        if r.status in working:
            kept += 1
        elif r.status in dead:
            to_disable.append(short)

    console.print(
        f"\n有效模块 [green]{kept}[/] 个 · 将禁用 [red]{len(to_disable)}[/] 个失效模块"
    )
    if dry_run:
        console.print("[dim]--dry-run：以下模块会被禁用，但未写入文件[/]")
        console.print(", ".join(sorted(to_disable)))
        return

    path = settings.holehe_disabled_file
    header = (
        "# 由 `seek prune-holehe` 自动生成\n"
        f"# 依据邮箱 {normalized} 的一次扫描结果，禁用无法给出有效判定的模块。\n"
        "# 删掉某一行即可重新启用对应站点。\n\n"
    )
    path.write_text(header + "\n".join(sorted(to_disable)) + "\n", encoding="utf-8")
    console.print(f"[green]已写入禁用清单 {path}[/]")
    console.print("[dim]重启服务后生效：python run.py[/]")


@app.command("ai")
def cmd_ai(
    email: str = typer.Argument(..., help="要调查的邮箱"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过授权确认"),
) -> None:
    """用 AI API Key 调度工具，汇总可能注册过的站点。"""
    from .ai_agent import AIInvestigator, ai_configured
    from .providers.registry import load_providers

    if not ai_configured():
        console.print("[red]未配置 SEEK_AI_API_KEY（或 OPENAI_API_KEY）[/]")
        raise typer.Exit(2)
    try:
        normalized = normalize_email(email)
    except InvalidEmail as exc:
        console.print(f"[red]邮箱格式不正确：{exc}[/]")
        raise typer.Exit(2)
    if not yes:
        console.print("[yellow]请确认：仅对本人邮箱或已获得书面授权的目标进行查询。[/]")
        if not typer.confirm("继续？", default=False):
            raise typer.Exit(1)

    async def go():
        agent = AIInvestigator(normalized, load_providers(), get_settings())
        return await agent.run()

    report = asyncio.run(go())
    console.print_json(json.dumps(report, ensure_ascii=False))


@app.command("serve")
def cmd_serve(
    host: Optional[str] = typer.Option(None, help="监听地址"),
    port: Optional[int] = typer.Option(None, help="监听端口"),
    reload: bool = typer.Option(False, "--reload", help="开发模式热重载"),
) -> None:
    """启动 Web 服务。"""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "seek.api:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
    )


@app.command("version")
def cmd_version() -> None:
    """显示版本号。"""
    console.print(f"seek {__version__}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
