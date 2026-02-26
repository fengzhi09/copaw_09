# -*- coding: utf-8 -*-
"""
00 号管理高手 - Agent 配置

职责：
- 创建新 Agent
- 执行 Agent 初始化流程
- 汇报各 Agent 状态和问题
- 反问确认需求细节
- 协调多 Agent 协作
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Agent00Meta(BaseModel):
    """00 号管理高手元数据"""
    id: str = "00"
    name: str = "管理高手"
    role: str = "master"
    status: str = "active"
    description: str = "负责创建新 Agent、初始化流程、汇报状态、反问确认需求"
    
    # 管理的 Agent 列表
    managed_agents: List[str] = ["01", "02", "03", "04"]
    
    # 权限
    permissions: List[str] = [
        "create_agent",
        "init_agent", 
        "view_status",
        "view_credit",
        "coordinate_agents"
    ]


class Agent00Config(BaseModel):
    """00 号配置"""
    meta: Agent00Meta = Field(default_factory=Agent00Meta)
    
    # 创建 Agent 流程配置
    create_flow: Dict[str, Any] = {
        "confirm_required": True,  # 需要用户确认
        "auto_init": True,        # 自动初始化
    }
    
    # 汇报配置
    report: Dict[str, Any] = {
        "daily": True,           # 每日汇报
        "on_change": True,       # 变更时汇报
    }
    
    # 协作配置
    collaboration: Dict[str, Any] = {
        "chain": True,           # 串联
        "parallel": True,        # 并联
        "gather": True,          # 汇聚
    }


# 默认配置
default_config = Agent00Config()
