# -*- coding: utf-8 -*-
"""
Tests for Copaw providers module
"""

import pytest
from providers.cost import (
    calculate_token_cost,
    calculate_image_cost,
    calculate_video_cost,
    get_model_cost_rate,
    COST_PER_1K_TOKENS,
    COST_PER_IMAGE,
    COST_PER_VIDEO_SECOND,
)


class TestCostCalculation:
    """Test cost calculation"""
    
    def test_calculate_token_cost_glm5(self):
        cost = calculate_token_cost("glm-5", 1000, 1000)
        assert cost == 0.02  # 0.01 * 1 + 0.01 * 1
    
    def test_calculate_token_cost_minimax(self):
        cost = calculate_token_cost("MiniMax-M2.5-highspeed", 1000, 1000)
        assert cost == 0.02  # 0.005 * 1 + 0.015 * 1
    
    def test_calculate_token_cost_unknown(self):
        cost = calculate_token_cost("unknown-model", 1000, 1000)
        assert cost == 0.0
    
    def test_calculate_image_cost(self):
        cost = calculate_image_cost("nano-banana-pro", 5)
        assert cost == 0.25  # 0.05 * 5
    
    def test_calculate_video_cost(self):
        cost = calculate_video_cost("veo_3_1", 10)
        assert cost == 5.0  # 0.50 * 10
    
    def test_get_model_cost_rate(self):
        rate = get_model_cost_rate("glm-5")
        assert rate == {"input": 0.01, "output": 0.01}
    
    def test_get_model_cost_rate_unknown(self):
        rate = get_model_cost_rate("unknown")
        assert rate == {"input": 0, "output": 0}


class TestCostRates:
    """Test cost rates configuration"""
    
    def test_glm5_rates(self):
        assert "glm-5" in COST_PER_1K_TOKENS
        assert COST_PER_1K_TOKENS["glm-5"]["input"] == 0.01
    
    def test_nano_banana_pro(self):
        assert "nano-banana-pro" in COST_PER_IMAGE
        assert COST_PER_IMAGE["nano-banana-pro"] == 0.05
    
    def test_veo_3_1(self):
        assert "veo_3_1" in COST_PER_VIDEO_SECOND
        assert COST_PER_VIDEO_SECOND["veo_3_1"] == 0.50
