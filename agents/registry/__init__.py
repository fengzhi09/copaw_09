# -*- coding: utf-8 -*-
"""
Agent Registry - Agent 注册和管理中心
"""

from typing import Dict, Optional, List, Any
from pathlib import Path


class AgentRegistry:
    """Agent 注册表"""
    
    # 预定义 Agent
    PREDEFINED_AGENTS = {
        "00": {
            "name": "管理高手",
            "role": "master",
            "module": "agent_00_管理高手",
            "description": "创建Agent、初始化、汇报状态"
        },
        "01": {
            "name": "学霸",
            "role": "academic",
            "module": "agent_01_学霸",
            "description": "学术搜索、论文调研"
        },
        "02": {
            "name": "编程高手",
            "role": "developer",
            "module": "agent_02_编程高手",
            "description": "代码开发、工具链检查"
        },
        "03": {
            "name": "创意青年",
            "role": "creative",
            "module": "agent_03_创意青年",
            "description": "文字创作、绘画提示词"
        },
        "04": {
            "name": "统计学长",
            "role": "collector",
            "module": "agent_04_统计学长",
            "description": "每日复盘、知识收藏"
        }
    }
    
    def __init__(self, agents_dir: str = None):
        self.agents_dir = Path(agents_dir or "~/.copaw/agents")
        self.agents_dir = self.agents_dir.expanduser()
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取 Agent 信息"""
        # 先检查预定义
        if agent_id in self.PREDEFINED_AGENTS:
            return self.PREDEFINED_AGENTS[agent_id]
        
        # 再检查自定义
        return self._get_custom_agent(agent_id)
    
    def _get_custom_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取自定义 Agent"""
        for agent_dir in self.agents_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name.startswith(f"agent_{agent_id}_"):
                meta_file = agent_dir / ".meta.json"
                if meta_file.exists():
                    import json
                    with open(meta_file, "r", encoding="utf-8") as f:
                        return json.load(f)
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有 Agent"""
        agents = []
        
        # 预定义 Agent
        for agent_id, info in self.PREDEFINED_AGENTS.items():
            agents.append({
                "id": agent_id,
                **info,
                "status": "active",
                "type": "predefined"
            })
        
        # 自定义 Agent
        if self.agents_dir.exists():
            for agent_dir in self.agents_dir.iterdir():
                if agent_dir.is_dir() and agent_dir.name.startswith("agent_"):
                    # 检查是否是预定义
                    parts = agent_dir.name.split("_")
                    if len(parts) >= 2 and parts[1] not in self.PREDEFINED_AGENTS:
                        meta_file = agent_dir / ".meta.json"
                        if meta_file.exists():
                            import json
                            with open(meta_file, "r", encoding="utf-8") as f:
                                agents.append({
                                    **json.load(f),
                                    "type": "custom"
                                })
        
        return sorted(agents, key=lambda x: x["id"])
    
    def get_agent_by_role(self, role: str) -> Optional[Dict[str, Any]]:
        """根据角色获取 Agent"""
        for agent_id, info in self.PREDEFINED_AGENTS.items():
            if info["role"] == role:
                return {"id": agent_id, **info}
        return None
    
    def is_predefined(self, agent_id: str) -> bool:
        """是否是预定义 Agent"""
        return agent_id in self.PREDEFINED_AGENTS


# 全局注册表
_registry = None


def get_registry() -> AgentRegistry:
    """获取全局 Agent 注册表"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


__all__ = [
    "AgentRegistry",
    "get_registry",
]
