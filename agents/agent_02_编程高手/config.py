# -*- coding: utf-8 -*-
"""
02 号编程高手 - Agent 配置

职责：
- 代码开发
- 调试辅助
- 架构设计
- 技术调研
"""

from pydantic import BaseModel, Field
from typing import List


class Agent02Meta(BaseModel):
    """02 号编程高手元数据"""
    id: str = "02"
    name: str = "编程高手"
    role: str = "developer"
    status: str = "active"
    description: str = "软件开发专家，擅长代码开发和架构设计"
    
    # 数据源
    data_sources: List[str] = Field(default_factory=lambda: [
        "GitHub",
        "CSDN",
        "知乎",
        "B站",
        "OpenCode"
    ])


class Agent02Config(BaseModel):
    """02 号配置"""
    meta: Agent02Meta = Field(default_factory=Agent02Meta)
    
    # 启动检查
    startup_check: List[str] = Field(default_factory=lambda: [
        "python_version",
        "node_version", 
        "git_config",
        "docker_status",
        "venv_status"
    ])
    
    # 技能配置
    skills: dict = Field(default_factory=lambda: {
        "required": [
            "code_analysis",
            "code_generation",
            "debug_assist",
            "git_assist"
        ],
        "optional": [
            "code_review",
            "architecture",
            "security_scan"
        ]
    })


default_config = Agent02Config()
