# -*- coding: utf-8 -*-
"""
Message Dispatcher - 消息分发器

负责将消息分发到合适的 Agent。
"""

import logging
import sys
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

# 添加项目根目录到路径
if '/home/ace09/bots' not in sys.path:
    sys.path.insert(0, '/home/ace09/bots')

from cp9.app.router import AgentRouter, get_router


logger = logging.getLogger("gateway.dispatcher")


class DispatchResult(Enum):
    """分发结果"""
    SUCCESS = "success"
    NO_AGENT = "no_agent"
    AGENT_ERROR = "agent_error"
    ROUTE_FAILED = "route_failed"


@dataclass
class DispatchResponse:
    """分发响应"""
    result: DispatchResult
    agent_id: str
    message: str = ""
    response: Optional[Dict[str, Any]] = None


class MessageDispatcher:
    """消息分发器"""
    
    def __init__(self, router: AgentRouter = None):
        """
        初始化分发器。
        
        Args:
            router: Agent 路由器，默认使用全局路由器
        """
        self.router = router or get_router()
    
    def get_agent_id(self, message: str, user_id: str = None) -> str:
        """
        根据消息内容获取合适的 Agent ID。
        
        Args:
            message: 用户消息
            user_id: 用户 ID
        
        Returns:
            Agent ID (默认 "00")
        """
        return self.router.route(message, user_id)
    
    async def dispatch(self, event: Dict[str, Any]) -> DispatchResponse:
        """
        分发消息事件到合适的 Agent。
        
        Args:
            event: 消息事件，包含 user_id, content, channel 等
        
        Returns:
            DispatchResponse 分发结果
        """
        user_id = event.get("user_id", "")
        message = event.get("content", "")
        channel = event.get("channel", "unknown")
        
        if not message:
            return DispatchResponse(
                result=DispatchResult.ROUTE_FAILED,
                agent_id="00",
                message="消息内容为空"
            )
        
        # 1. 路由到 Agent
        agent_id = self.get_agent_id(message, user_id)
        logger.info(f"[Gateway] 用户 {user_id} 的消息路由到 Agent {agent_id}")
        
        # 2. 获取 Agent 配置
        agent_config = self.router.get_agent_config(agent_id)
        if not agent_config:
            return DispatchResponse(
                result=DispatchResult.NO_AGENT,
                agent_id=agent_id,
                message=f"Agent {agent_id} 不存在"
            )
        
        # 3. 调用 Agent 处理消息
        try:
            response = await self._call_agent(
                agent_id=agent_id,
                message=message,
                user_id=user_id,
                channel=channel,
                context=event
            )
            
            return DispatchResponse(
                result=DispatchResult.SUCCESS,
                agent_id=agent_id,
                message="处理成功",
                response=response
            )
            
        except Exception as e:
            logger.error(f"[Gateway] Agent {agent_id} 处理失败: {e}")
            return DispatchResponse(
                result=DispatchResult.AGENT_ERROR,
                agent_id=agent_id,
                message=f"Agent 处理失败: {str(e)}"
            )
    
    async def _call_agent(
        self,
        agent_id: str,
        message: str,
        user_id: str,
        channel: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        调用 Agent 处理消息。
        
        这里应该调用 Agent 的执行逻辑。
        后续会与 agents 模块集成。
        
        Args:
            agent_id: Agent ID
            message: 用户消息
            user_id: 用户 ID
            channel: 渠道
            context: 上下文信息
        
        Returns:
            Agent 响应
        """
        # TODO: 后续与 Agent 执行模块集成
        # 目前返回模拟响应
        
        logger.info(f"[Dispatcher] 调用 Agent {agent_id} 处理消息: {message[:50]}...")
        
        # 模拟响应
        return {
            "agent_id": agent_id,
            "user_id": user_id,
            "channel": channel,
            "message": message,
            "status": "processed",
            # TODO: 实际 Agent 的响应
            "response_text": f"[Agent {agent_id}] 已收到消息"
        }
    
    async def process_message(
        self,
        message: str,
        user_id: str,
        channel: str
    ) -> str:
        """
        简化版消息处理，直接返回文本响应。
        
        Args:
            message: 用户消息
            user_id: 用户 ID
            channel: 渠道名称
        
        Returns:
            Agent 响应文本
        """
        event = {
            "user_id": user_id,
            "content": message,
            "channel": channel
        }
        
        result = await self.dispatch(event)
        
        if result.result == DispatchResult.SUCCESS:
            return result.response.get("response_text", "")
        else:
            return f"处理失败: {result.message}"


# 全局分发器
_dispatcher: Optional[MessageDispatcher] = None


def get_dispatcher() -> MessageDispatcher:
    """获取全局分发器"""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = MessageDispatcher()
    return _dispatcher


def init_dispatcher(router: AgentRouter = None) -> MessageDispatcher:
    """初始化分发器"""
    global _dispatcher
    _dispatcher = MessageDispatcher(router)
    return _dispatcher


__all__ = [
    "MessageDispatcher",
    "DispatchResult",
    "DispatchResponse",
    "get_dispatcher",
    "init_dispatcher",
]
