# -*- coding: utf-8 -*-
"""
Cost calculation for cp9 models
"""

from typing import Dict

# Cost per 1K tokens (in yuan/人民币)
COST_PER_1K_TOKENS: Dict[str, Dict[str, float]] = {
    # 智谱 GLM
    "glm-5": {"input": 0.01, "output": 0.01},
    "glm-4-plus": {"input": 0.05, "output": 0.05},
    "glm-4-flash": {"input": 0.001, "output": 0.001},
    "glm-4": {"input": 0.02, "output": 0.02},
    "glm-3-turbo": {"input": 0.001, "output": 0.001},
    
    # MiniMax
    "MiniMax-M2.5-long": {"input": 0.015, "output": 0.015},
    "MiniMax-M2.5-highspeed": {"input": 0.005, "output": 0.015},
    "MiniMax-M2.1": {"input": 0.01, "output": 0.01},
    
    # Qwen (DashScope)
    "qwen3-max": {"input": 0.04, "output": 0.12},
    "qwen-plus": {"input": 0.02, "output": 0.06},
    "qwen-turbo": {"input": 0.008, "output": 0.008},
    
    # OpenAI
    "gpt-4o": {"input": 0.025, "output": 0.075},
    "gpt-4o-mini": {"input": 0.001, "output": 0.003},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
    
    # Claude (OpenRouter)
    "anthropic/claude-3.5-sonnet": {"input": 0.015, "output": 0.075},
    
    # DeepSeek
    "deepseek-chat": {"input": 0.001, "output": 0.002},
    "deepseek-v3.2": {"input": 0.001, "output": 0.001},
}

# Cost per image (for image generation)
COST_PER_IMAGE: Dict[str, float] = {
    "nano-banana-pro": 0.05,
    "dall-e-3": 0.08,
    "stable-diffusion": 0.02,
}

# Cost per video second (for video generation)
COST_PER_VIDEO_SECOND: Dict[str, float] = {
    "veo_3_1": 0.50,
}


def calculate_token_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for token usage."""
    if model not in COST_PER_1K_TOKENS:
        return 0.0
    
    rates = COST_PER_1K_TOKENS[model]
    input_cost = (input_tokens / 1000) * rates["input"]
    output_cost = (output_tokens / 1000) * rates["output"]
    
    return input_cost + output_cost


def calculate_image_cost(model: str, count: int = 1) -> float:
    """Calculate cost for image generation."""
    if model not in COST_PER_IMAGE:
        return 0.0
    return COST_PER_IMAGE[model] * count


def calculate_video_cost(model: str, seconds: int) -> float:
    """Calculate cost for video generation."""
    if model not in COST_PER_VIDEO_SECOND:
        return 0.0
    return COST_PER_VIDEO_SECOND[model] * seconds


def get_model_cost_rate(model: str) -> Dict[str, float]:
    """Get cost rate for a model."""
    return COST_PER_1K_TOKENS.get(model, {"input": 0, "output": 0})
