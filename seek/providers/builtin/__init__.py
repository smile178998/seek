"""内置 Python 检测模块。

想新增一个用 Python 实现的模块：继承 Provider、实现 check()，
然后用 @register 装饰器注册即可被引擎自动发现。
"""

from __future__ import annotations

from typing import Callable, TypeVar

from ..base import Provider

BUILTIN_FACTORIES: list[Callable[[], Provider]] = []

F = TypeVar("F", bound=Callable[[], Provider])


def register(factory: F) -> F:
    BUILTIN_FACTORIES.append(factory)
    return factory


from . import dns_checks  # noqa: E402,F401  触发注册

__all__ = ["BUILTIN_FACTORIES", "register"]
