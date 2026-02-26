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
from .manager import (
    AgentSpec,
    CreateResult,
    AgentCreator,
    AgentManager,
    RequirementClarifier,
    Agent00Service,
)
from .requirement import RequirementAnalyzer
from .collaborator import TaskCollaborator
from .reporter import StatusReporter

__all__ = [
    "Agent00Config",
    "default_config",
    "AgentSpec",
    "CreateResult",
    "AgentCreator",
    "AgentManager",
    "RequirementClarifier",
    "RequirementAnalyzer",
    "TaskCollaborator",
    "StatusReporter",
    "Agent00Service",
]
