# -*- coding: utf-8 -*-
"""
Gateway - 统一入口

Gateway 模块的统一入口，整合认证、过滤、分发功能。
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .auth import (
    GatewayAuth,
    AuthResult,
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
    get_dispatcher,
    init_dispatcher,
)


logger = logging.getLogger("gateway")


@dataclass
class GatewayConfig:
    """Gateway 配置"""
    # 认证配置
    allow_from: list = None
    api_keys: dict = None
    enable_rate_limit: bool = True
    rate_limit_count: int = 60
    rate_limit_window: int = 60
    
    # 过滤配置
    ignore_event_types: list = None
    ignore_user_ids: list = None
    ignore_keywords: list = None
    min_content_length: int = 1
    max_content_length: int = 10000


@dataclass
class GatewayResponse:
    """Gateway 响应"""
    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error_code: str = ""


class Gateway:
    """Gateway 统一入口"""
    
    def __init__(self, config: GatewayConfig = None):
        """
        初始化 Gateway。
        
        Args:
            config: Gateway 配置
        """
        self.config = config or GatewayConfig()
        
        # 初始化各组件
        self.auth = init_gateway_auth({
            "allow_from": self.config.allow_from,
            "api_keys": self.config.api_keys,
            "enable_rate_limit": self.config.enable_rate_limit,
            "rate_limit_count": self.config.rate_limit_count,
            "rate_limit_window": self.config.rate_limit_window,
        })
        
        self.filter = init_gateway_filter({
            "ignore_event_types": self.config.ignore_event_types,
            "ignore_user_ids": self.config.ignore_user_ids,
            "ignore_keywords": self.config.ignore_keywords,
            "min_content_length": self.config.min_content_length,
            "max_content_length": self.config.max_content_length,
        })
        
        self.dispatcher = get_dispatcher()
        
        logger.info("[Gateway] Gateway 初始化完成")
    
    async def handle(self, event: Dict[str, Any]) -> GatewayResponse:
        """
        处理消息事件。
        
        完整流程：
        1. 身份认证
        2. 事件过滤
        3. 消息分发
        
        Args:
            event: 消息事件
        
        Returns:
            GatewayResponse 处理结果
        """
        user_id = event.get("user_id", "unknown")
        channel = event.get("channel", "unknown")
        content = event.get("content", "")
        
        logger.info(f"[Gateway] 收到消息: user={user_id}, channel={channel}")
        
        # 1. 身份认证
        auth_response = self.auth.authenticate(user_id, channel)
        
        if auth_response.result == AuthResult.REJECT:
            logger.warning(f"[Gateway] 用户 {user_id} 认证拒绝")
            return GatewayResponse(
                success=False,
                message=auth_response.message,
                error_code="AUTH_REJECT"
            )
        
        if auth_response.result == AuthResult.RATE_LIMIT:
            logger.warning(f"[Gateway] 用户 {user_id} 触发限流")
            return GatewayResponse(
                success=False,
                message=auth_response.message,
                error_code="AUTH_RATE_LIMIT"
            )
        
        # 2. 事件过滤
        if not self.filter.should_process(event):
            logger.info(f"[Gateway] 事件被过滤: user={user_id}")
            return GatewayResponse(
                success=False,
                message="事件被过滤",
                error_code="FILTER_IGNORED"
            )
        
        # 3. 消息分发
        try:
            dispatch_result = await self.dispatcher.dispatch(event)
            
            if dispatch_result.result == DispatchResult.SUCCESS:
                return GatewayResponse(
                    success=True,
                    message="处理成功",
                    data=dispatch_result.response
                )
            else:
                return GatewayResponse(
                    success=False,
                    message=dispatch_result.message,
                    error_code=dispatch_result.result.value
                )
                
        except Exception as e:
            logger.error(f"[Gateway] 处理异常: {e}")
            return GatewayResponse(
                success=False,
                message=f"处理异常: {str(e)}",
                error_code="INTERNAL_ERROR"
            )
    
    async def handle_text(
        self,
        message: str,
        user_id: str,
        channel: str = "unknown"
    ) -> str:
        """
        简化版消息处理。
        
        Args:
            message: 用户消息
            user_id: 用户 ID
            channel: 渠道名称
        
        Returns:
            响应文本
        """
        event = {
            "user_id": user_id,
            "content": message,
            "channel": channel
        }
        
        response = await self.handle(event)
        
        if response.success:
            return response.data.get("response_text", "") if response.data else ""
        else:
            return f"处理失败: {response.message}"


# 全局 Gateway
_gateway: Optional[Gateway] = None


def get_gateway() -> Gateway:
    """获取全局 Gateway"""
    global _gateway
    if _gateway is None:
        _gateway = Gateway()
    return _gateway


def init_gateway(config: Dict[str, Any]) -> Gateway:
    """从配置初始化 Gateway"""
    global _gateway
    
    gateway_config = GatewayConfig(
        allow_from=config.get("allow_from"),
        api_keys=config.get("api_keys"),
        enable_rate_limit=config.get("enable_rate_limit", True),
        rate_limit_count=config.get("rate_limit_count", 60),
        rate_limit_window=config.get("rate_limit_window", 60),
        ignore_event_types=config.get("ignore_event_types", []),
        ignore_user_ids=config.get("ignore_user_ids", []),
        ignore_keywords=config.get("ignore_keywords", []),
        min_content_length=config.get("min_content_length", 1),
        max_content_length=config.get("max_content_length", 10000),
    )
    
    _gateway = Gateway(gateway_config)
    return _gateway


__all__ = [
    "Gateway",
    "GatewayConfig",
    "GatewayResponse",
    "get_gateway",
    "init_gateway",
]
