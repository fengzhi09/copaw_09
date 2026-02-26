# -*- coding: utf-8 -*-
"""
03 号创意青年 - Agent 配置

职责：
- 文字创作
- 绘画提示词
- 视频脚本
- 创意生成
"""

from pydantic import BaseModel, Field
from typing import List


class Agent03Meta(BaseModel):
    """03 号创意青年元数据"""
    id: str = "03"
    name: str = "创意青年"
    role: str = "creative"
    status: str = "active"
    description: str = "创意内容专家，擅长文字创作和视觉设计"
    
    # 工具
    tools: dict = Field(default_factory=lambda: {
        "print": "nano-banana-pro"
    })
    
    # 数据源
    data_sources: List[str] = Field(default_factory=lambda: [
        "小红书",
        "抖音",
        "B站",
        "微博"
    ])


class Agent03Config(BaseModel):
    """03 号配置"""
    meta: Agent03Meta = Field(default_factory=Agent03Meta)
    
    # 技能配置
    skills: dict = Field(default_factory=lambda: {
        "required": [
            "text_creative",
            "image_prompt",
            "video_script",
            "copywriter"
        ],
        "optional": [
            "video_edit",
            "social_media",
            "trend_analysis"
        ]
    })


default_config = Agent03Config()
