# -*- coding: utf-8 -*-
"""
00 号管理高手 Agent 模块

职责：
- 创建新 Agent
- 执行 Agent 初始化流程
- 汇报各 Agent 状态和问题
- 反问确认需求细节
- 协调多 Agent 协作
"""

from .config import Agent00Config, default_config
from .manager import AgentCreator, AgentManager, RequirementClarifier

__all__ = [
    "Agent00Config",
    "default_config",
    "AgentCreator",
    "AgentManager",
    "RequirementClarifier",
]
