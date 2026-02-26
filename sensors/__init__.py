# -*- coding: utf-8 -*-
"""
Sensors Module for cp9

Sensors:
- print: Image generation (nano-banana-pro)
- dispatch: Intent distribution (Qwen3-0.6B)
- recorder: Video generation (veo_3_1) - not implemented yet
"""

from typing import Optional, Dict, Any
import json
import os
import requests
from pathlib import Path

# ==================== Print (Image Generation) ====================

class PrintSensor:
    """Image generation sensor using nano-banana-pro"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ.get("NANO_BANANA_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "NANO_BANANA_URL", 
            "https://api.nanobanana.com/v1"
        )
    
    def generate(
        self, 
        prompt: str, 
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate images from text prompt."""
        if not self.api_key:
            raise ValueError("API key not configured")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_images": num_images,
            **kwargs
        }
        
        response = requests.post(
            f"{self.base_url}/images/generations",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            raise Exception(f"Image generation failed: {response.text}")
        
        result = response.json()
        return {
            "images": result.get("data", []),
            "model": result.get("model", "nano-banana-pro")
        }
    
    def generate_url(self, prompt: str, **kwargs) -> str:
        """Generate image and return URL."""
        result = self.generate(prompt, **kwargs)
        if result["images"]:
            return result["images"][0].get("url", "")
        return ""


# ==================== Dispatch (Intent Distribution) ====================

class DispatchSensor:
    """Intent distribution using local Qwen model"""
    
    def __init__(self, model_path: str = None):
        # 使用本地 Qwen3-0.6B 模型
        self.model_path = model_path or os.environ.get(
            "DISPATCH_MODEL_PATH",
            "Qwen/Qwen3-0.6B-FP8"
        )
        self.model = None
    
    def load_model(self):
        """Load the dispatch model."""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path, 
                trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
        except ImportError:
            print("Warning: transformers not installed for dispatch sensor")
    
    def classify_intent(self, message: str, agents: list = None) -> Dict[str, Any]:
        """Classify user intent and route to appropriate agent."""
        # Simple keyword-based routing
        # TODO: Use local model for better classification
        
        message_lower = message.lower()
        agents = agents or ["00", "01", "02", "03", "04"]
        
        # Keyword mapping
        keywords = {
            "00": ["创建", "新建", "agent", "管理", "系统"],
            "01": ["搜索", "论文", "学术", "调研", "研究"],
            "02": ["代码", "编程", "开发", "bug", "报错"],
            "03": ["创意", "写作", "文案", "画", "视频"],
            "04": ["统计", "报表", "成本", "复盘", "总结"]
        }
        
        scores = {agent: 0 for agent in agents}
        
        for agent, words in keywords.items():
            for word in words:
                if word in message_lower:
                    scores[agent] += 1
        
        # Find best match
        best_agent = max(scores, key=scores.get)
        confidence = scores[best_agent] / max(len(keywords.get(best_agent, [])), 1)
        
        return {
            "agent_id": best_agent if scores[best_agent] > 0 else "00",
            "confidence": min(confidence, 1.0),
            "scores": scores,
            "reason": "keyword matching"
        }


# ==================== Recorder (Video Generation) ====================

class RecorderSensor:
    """Video generation sensor - not implemented yet"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ.get("VEOS_API_KEY", "")
        self.base_url = base_url or os.environ.get(
            "VEOS_URL",
            "https://api.lingyaai.cn/v1"
        )
        self.enabled = False
    
    def generate(
        self,
        prompt: str,
        first_frame: str = None,
        last_frame: str = None,
        duration: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate video from prompt (not implemented)."""
        raise NotImplementedError("Video generation not implemented yet")


# ==================== Sensor Factory ====================

class SensorFactory:
    """Factory for creating sensors"""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_print(cls, **kwargs) -> PrintSensor:
        """Get or create print sensor"""
        if "print" not in cls._instances:
            cls._instances["print"] = PrintSensor(**kwargs)
        return cls._instances["print"]
    
    @classmethod
    def get_dispatch(cls, **kwargs) -> DispatchSensor:
        """Get or create dispatch sensor"""
        if "dispatch" not in cls._instances:
            cls._instances["dispatch"] = DispatchSensor(**kwargs)
        return cls._instances["dispatch"]
    
    @classmethod
    def get_recorder(cls, **kwargs) -> RecorderSensor:
        """Get or create recorder sensor"""
        if "recorder" not in cls._instances:
            cls._instances["recorder"] = RecorderSensor(**kwargs)
        return cls._instances["recorder"]


# ==================== Exports ====================

__all__ = [
    "PrintSensor",
    "DispatchSensor", 
    "RecorderSensor",
    "SensorFactory",
]
