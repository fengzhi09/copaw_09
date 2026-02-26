# -*- coding: utf-8 -*-
"""
01 号学霸 - Agent 配置

职责：
- 学术搜索
- 论文调研
- 文献综述
- 事实核查
"""

from pydantic import BaseModel, Field
from typing import List


class Agent01Meta(BaseModel):
    """01 号学霸元数据"""
    id: str = "01"
    name: str = "学霸"
    role: str = "academic"
    status: str = "active"
    description: str = "学术调研专家，擅长论文检索和文献综述"
    
    # 数据源（按优先级排序）
    data_sources: List[str] = Field(default_factory=lambda: [
        "谷歌学术",
        "百度学术", 
        "PubMed",
        "SciHub",
        "ArXiv",
        "GitHub",
        "ModelScope",
        "知乎",
        "B站",
        "YouTube",
        "X (Twitter)"
    ])


class Agent01Config(BaseModel):
    """01 号配置"""
    meta: Agent01Meta = Field(default_factory=Agent01Meta)
    
    # 技能配置
    skills: dict = Field(default_factory=lambda: {
        "required": [
            "academic_search",
            "paper_review", 
            "citation_manager",
            "fact_check"
        ],
        "optional": [
            "translate",
            "data_analysis",
            "visualization"
        ]
    })


default_config = Agent01Config()
