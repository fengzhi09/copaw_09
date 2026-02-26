# -*- coding: utf-8 -*-
"""
04 号统计学长 - Agent 配置

职责：
- 每日复盘
- 知识收藏
- 总结归纳
- 经验萃取
"""

from pydantic import BaseModel, Field
from typing import List


class Agent04Meta(BaseModel):
    """04 号统计学长元数据"""
    id: str = "04"
    name: str = "统计学长"
    role: str = "collector"
    status: str = "active"
    description: str = "知识管理专家，擅长每日复盘和知识收藏"
    
    # 数据源
    data_sources: List[str] = Field(default_factory=lambda: [
        "喜马拉雅",
        "得物",
        "知乎"
    ])


class Agent04Config(BaseModel):
    """04 号配置"""
    meta: Agent04Meta = Field(default_factory=Agent04Meta)
    
    # 每日复盘配置
    daily_routine: dict = Field(default_factory=lambda: {
        "trigger": "每天 18:00",
        "steps": [
            "query_agents_work",
            "collect_summaries",
            "extract_insights",
            "save_to_memory",
            "generate_report"
        ]
    })
    
    # 晚餐交流会配置
    dinner_meeting: dict = Field(default_factory=lambda: {
        "schedule": "0 21 * * */3",  # 每3天晚上9点
        "duration": 3600,  # 1小时
        "participants": ["00", "01", "02", "03", "04"]
    })
    
    # 技能配置
    skills: dict = Field(default_factory=lambda: {
        "required": [
            "summary",
            "knowledge_org",
            "daily_report",
            "insight_extract"
        ],
        "optional": [
            "knowledge_graph",
            "trend_report",
            "recommendation"
        ]
    })


default_config = Agent04Config()
