# -*- coding: utf-8 -*-
"""
Agent Router - Agent 路由选择

根据消息内容选择合适的 Agent 处理。
"""

from typing import Optional, Dict, Any
from agents.agent_00_管理高手.manager import AgentManager
from agents.agent_registry import get_registry


class AgentRouter:
    """Agent 路由器"""
    
    # 关键词到 Agent ID 映射
    KEYWORD_MAP = {
        "00": ["创建", "新建", "agent", "管理", "系统", "配置"],
        "01": ["搜索", "论文", "学术", "调研", "研究", "google"],
        "02": ["代码", "编程", "开发", "bug", "报错", "github"],
        "03": ["创意", "写作", "文案", "画", "视频", "小红书"],
        "04": ["统计", "报表", "成本", "复盘", "总结", "每日"],
    }
    
    def __init__(self):
        self.registry = get_registry()
    
    def route(self, message: str, user_id: str = None) -> str:
        """
        根据消息内容路由到合适的 Agent。
        
        Args:
            message: 用户消息
            user_id: 用户 ID
        
        Returns:
            Agent ID (默认 "00")
        """
        if not message:
            return "00"
        
        message_lower = message.lower()
        scores = {agent_id: 0 for agent_id in self.KEYWORD_MAP}
        
        # 关键词匹配计分
        for agent_id, keywords in self.KEYWORD_MAP.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    scores[agent_id] += 1
        
        # 找出最高分
        best_agent = max(scores, key=scores.get)
        
        # 如果没有匹配，返回默认 Agent 00
        if scores[best_agent] == 0:
            return "00"
        
        return best_agent
    
    def get_agent_config(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 配置"""
        return self.registry.get_agent(agent_id)
    
    def list_agents(self) -> list:
        """列出所有可用 Agent"""
        return self.registry.list_agents()


# 全局路由器
_router = None


def get_router() -> AgentRouter:
    """获取全局路由器"""
    global _router
    if _router is None:
        _router = AgentRouter()
    return _router


__all__ = ["AgentRouter", "get_router"]
