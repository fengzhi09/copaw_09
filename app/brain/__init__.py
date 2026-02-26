# -*- coding: utf-8 -*-
"""
Brain Module - 脑部模块

包含:
- Thalamus (丘脑): 意图识别、消息路由、记忆索引
- Prefrontal (前额叶): 深度思考、推理、规划
"""

from .thalamus import Thalamus, IntentResult, get_thalamus
from .prefrontal import Prefrontal, ReasoningResult, get_prefrontal

__all__ = [
    "Thalamus",
    "IntentResult", 
    "get_thalamus",
    "Prefrontal",
    "ReasoningResult",
    "get_prefrontal",
]
