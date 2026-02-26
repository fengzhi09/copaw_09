# -*- coding: utf-8 -*-
"""
Gateway Auth - 身份认证

支持多种认证方式：
- 用户白名单 (allowFrom)
- API Key 验证
- Channel 特定认证
"""

import hashlib
import hmac
import time
from typing import Dict, Any, Optional, Set, List
from dataclasses import dataclass, field
from enum import Enum


class AuthResult(Enum):
    """认证结果"""
    PASS = "pass"           # 通过
    REJECT = "reject"       # 拒绝
    RATE_LIMIT = "rate_limit"  # 限流


@dataclass
class UserPermission:
    """用户权限配置"""
    user_id: str
    allowed: bool = True
    agent_whitelist: Set[str] = field(default_factory=set)  # 允许访问的 Agent
    daily_credit_limit: float = 100.0  # 每日 Credit 限制


@dataclass
class AuthResponse:
    """认证响应"""
    result: AuthResult
    message: str = ""
    user_permission: Optional[UserPermission] = None


class GatewayAuth:
    """Gateway 身份认证"""
    
    def __init__(
        self,
        allow_from: List[str] = None,
        api_keys: Dict[str, str] = None,
        enable_rate_limit: bool = True,
        rate_limit_count: int = 60,
        rate_limit_window: int = 60,
    ):
        """
        初始化认证器。
        
        Args:
            allow_from: 允许的用户 ID 白名单
            api_keys: API Key 映射 {key: user_id}
            enable_rate_limit: 是否启用限流
            rate_limit_count: 时间窗口内最大请求数
            rate_limit_window: 时间窗口(秒)
        """
        self.allow_from = set(allow_from or [])
        self.api_keys = api_keys or {}
        self.enable_rate_limit = enable_rate_limit
        self.rate_limit_count = rate_limit_count
        self.rate_limit_window = rate_limit_window
        
        # 用户权限缓存
        self._user_permissions: Dict[str, UserPermission] = {}
        
        # 限流计数器: {user_id: [timestamp1, timestamp2, ...]}
        self._rate_limit_cache: Dict[str, List[float]] = {}
    
    def authenticate(self, user_id: str, channel: str = "unknown") -> AuthResponse:
        """
        验证用户身份。
        
        Args:
            user_id: 用户 ID
            channel: 渠道名称
        
        Returns:
            AuthResponse 认证结果
        """
        # 1. 白名单检查
        if self.allow_from and user_id not in self.allow_from:
            return AuthResponse(
                result=AuthResult.REJECT,
                message=f"用户 {user_id} 不在白名单中"
            )
        
        # 2. 限流检查
        if self.enable_rate_limit:
            rate_result = self._check_rate_limit(user_id)
            if rate_result:
                return rate_result
        
        # 3. 获取用户权限
        permission = self._get_user_permission(user_id)
        
        return AuthResponse(
            result=AuthResult.PASS,
            message="认证通过",
            user_permission=permission
        )
    
    def authenticate_api_key(self, api_key: str) -> Optional[AuthResponse]:
        """
        使用 API Key 验证。
        
        Args:
            api_key: API Key
        
        Returns:
            AuthResponse 或 None (key 无效)
        """
        user_id = self.api_keys.get(api_key)
        if not user_id:
            return AuthResponse(
                result=AuthResult.REJECT,
                message="无效的 API Key"
            )
        
        return self.authenticate(user_id, channel="api")
    
    def _check_rate_limit(self, user_id: str) -> Optional[AuthResponse]:
        """检查限流"""
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # 获取或初始化用户的时间戳列表
        if user_id not in self._rate_limit_cache:
            self._rate_limit_cache[user_id] = []
        
        # 清理过期时间戳
        timestamps = [
            ts for ts in self._rate_limit_cache[user_id]
            if ts > window_start
        ]
        
        # 检查是否超限
        if len(timestamps) >= self.rate_limit_count:
            return AuthResponse(
                result=AuthResult.RATE_LIMIT,
                message=f"请求过于频繁，请在 {self.rate_limit_window} 秒后重试"
            )
        
        # 记录新请求
        timestamps.append(now)
        self._rate_limit_cache[user_id] = timestamps
        
        return None
    
    def _get_user_permission(self, user_id: str) -> UserPermission:
        """获取用户权限"""
        if user_id not in self._user_permissions:
            # 默认权限
            self._user_permissions[user_id] = UserPermission(
                user_id=user_id,
                allowed=True,
                agent_whitelist=set(),  # 空表示无限制
                daily_credit_limit=100.0
            )
        return self._user_permissions[user_id]
    
    def set_user_permission(self, permission: UserPermission):
        """设置用户权限"""
        self._user_permissions[permission.user_id] = permission
    
    def add_allow_user(self, user_id: str):
        """添加白名单用户"""
        self.allow_from.add(user_id)
    
    def remove_allow_user(self, user_id: str):
        """移除白名单用户"""
        self.allow_from.discard(user_id)
    
    def is_allowed(self, user_id: str) -> bool:
        """检查用户是否在白名单"""
        if not self.allow_from:  # 空白名单表示允许所有
            return True
        # 移除后变空，也允许所有
        return user_id in self.allow_from


# 全局认证器
_auth: Optional[GatewayAuth] = None


def get_gateway_auth() -> GatewayAuth:
    """获取全局认证器"""
    global _auth
    if _auth is None:
        _auth = GatewayAuth()
    return _auth


def init_gateway_auth(config: Dict[str, Any]) -> GatewayAuth:
    """从配置初始化认证器"""
    global _auth
    _auth = GatewayAuth(
        allow_from=config.get("allow_from"),
        api_keys=config.get("api_keys"),
        enable_rate_limit=config.get("enable_rate_limit", True),
        rate_limit_count=config.get("rate_limit_count", 60),
        rate_limit_window=config.get("rate_limit_window", 60),
    )
    return _auth


__all__ = [
    "GatewayAuth",
    "AuthResult",
    "AuthResponse",
    "UserPermission",
    "get_gateway_auth",
    "init_gateway_auth",
]
