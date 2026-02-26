# -*- coding: utf-8 -*-
"""
Gateway 模块 - 消息入口

负责：
- 消息接收和分发
- 身份认证
- 事件过滤
- 限流控制

模块结构：
├── __init__.py       # 模块导出
├── auth.py           # 身份认证
├── filter.py         # 事件过滤
├── dispatcher.py     # 消息分发
└── gateway.py        # 统一入口
"""

from .auth import (
    GatewayAuth,
    AuthResult,
    AuthResponse,
    UserPermission,
    get_gateway_auth,
    init_gateway_auth,
)
from .filter import (
    GatewayFilter,
    get_gateway_filter,
    init_gateway_filter,
)
from .dispatcher import (
    MessageDispatcher,
    DispatchResult,
    DispatchResponse,
    get_dispatcher,
    init_dispatcher,
)
from .gateway import (
    Gateway,
    GatewayConfig,
    GatewayResponse,
    get_gateway,
    init_gateway,
)

__all__ = [
    # Auth
    "GatewayAuth",
    "AuthResult",
    "AuthResponse",
    "UserPermission",
    "get_gateway_auth",
    "init_gateway_auth",
    # Filter
    "GatewayFilter",
    "get_gateway_filter",
    "init_gateway_filter",
    # Dispatcher
    "MessageDispatcher",
    "DispatchResult",
    "DispatchResponse",
    "get_dispatcher",
    "init_dispatcher",
    # Gateway
    "Gateway",
    "GatewayConfig",
    "GatewayResponse",
    "get_gateway",
    "init_gateway",
]
