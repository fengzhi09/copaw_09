# -*- coding: utf-8 -*-
"""
Prefrontal - 前额叶模块

功能:
- 深度思考
- 推理分析
- 规划决策
- 生成回复
"""

import logging
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("brain.prefrontal")


class ModelProvider(Enum):
    """模型提供商"""
    ZHIPU = "zhipu"      # 智谱
    MINIMAX = "minimax"  # MiniMax
    OPENAI = "openai"    # OpenAI


@dataclass
class ReasoningStep:
    """推理步骤"""
    step: int
    thought: str
    action: str = ""
    observation: str = ""


@dataclass
class ReasoningResult:
    """推理结果"""
    reasoning: str          # 推理过程
    conclusion: str         # 结论
    confidence: float       # 置信度 0-1
    evidence: List[str]    # 证据
    steps: List[ReasoningStep] = field(default_factory=list)


@dataclass
class PlanStep:
    """规划步骤"""
    step_id: int
    description: str
    agent_id: str
    dependencies: List[int] = field(default_factory=list)
    estimated_time: int = 60


@dataclass
class PlanResult:
    """规划结果"""
    steps: List[PlanStep]
    estimated_time: int     # 总预计时间(秒)
    resources: List[str]     # 所需资源
    success_rate: float     # 成功率预估


@dataclass
class GenerationResult:
    """生成结果"""
    text: str               # 生成的文本
    model: str              # 使用的模型
    tokens_used: int        # 使用的 token 数
    finish_reason: str      # 结束原因


class Prefrontal:
    """前额叶 - 深度思考、推理、规划"""
    
    # 模型配置
    MODEL_CONFIG = {
        "glm-5": {
            "provider": ModelProvider.ZHIPU,
            "api_key_env": "ZHIPU_API_KEY",
            "api_base": "https://open.bigmodel.cn/api/paas/v4",
            "max_tokens": 4096,
        },
        "glm-4": {
            "provider": ModelProvider.ZHIPU,
            "api_key_env": "ZHIPU_API_KEY",
            "api_base": "https://open.bigmodel.cn/api/paas/v4",
            "max_tokens": 4096,
        },
        "MiniMax-M2.5": {
            "provider": ModelProvider.MINIMAX,
            "api_key_env": "MINIMAX_API_KEY",
            "api_base": "https://api.minimaxi.com/v1",
            "max_tokens": 8192,
        },
    }
    
    def __init__(
        self,
        primary_model: str = "glm-5",
        fallback_model: str = "MiniMax-M2.5",
        api_key: str = None,
        api_base: str = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        """
        初始化前额叶。
        
        Args:
            primary_model: 主模型
            fallback_model: 备用模型
            api_key: API Key
            api_base: API 地址
            max_tokens: 最大 token 数
            temperature: 温度参数
        """
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.api_key = api_key
        self.api_base = api_base
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # 加载配置
        self._load_config()
        
        logger.info(f"[Prefrontal] 初始化完成 (primary={primary_model})")
    
    def _load_config(self):
        """加载配置"""
        import os
        
        # 获取模型配置
        config = self.MODEL_CONFIG.get(self.primary_model, {})
        
        # 从环境变量获取 API Key
        if not self.api_key:
            api_key_env = config.get("api_key_env", "ZHIPU_API_KEY")
            self.api_key = os.getenv(api_key_env, "")
        
        # API 地址
        if not self.api_base:
            self.api_base = config.get("api_base", "")
    
    async def think(
        self,
        prompt: str,
        context: Dict[str, Any] = None,
        model: str = None
    ) -> GenerationResult:
        """
        深度思考。
        
        Args:
            prompt: 提示词
            context: 上下文
            model: 指定模型
        
        Returns:
            GenerationResult 生成结果
        """
        model = model or self.primary_model
        
        # 构建消息
        messages = self._build_messages(prompt, context)
        
        # 调用 API
        try:
            result = await self._call_api(model, messages)
            return result
        except Exception as e:
            logger.error(f"[Prefrontal] 调用失败: {e}")
            # 尝试降级
            if model != self.fallback_model:
                logger.info(f"[Prefrontal] 尝试降级到 {self.fallback_model}")
                return await self.think(prompt, context, self.fallback_model)
            raise
    
    async def reason(
        self,
        problem: str,
        context: Dict[str, Any] = None
    ) -> ReasoningResult:
        """
        推理分析。
        
        Args:
            problem: 问题描述
            context: 上下文
        
        Returns:
            ReasoningResult 推理结果
        """
        prompt = f"""请分析并解决以下问题：

问题: {problem}

请进行详细推理，给出推理过程和结论。"""
        
        result = await self.think(prompt, context)
        
        # 解析推理结果
        return self._parse_reasoning_result(result.text)
    
    async def plan(
        self,
        goal: str,
        context: Dict[str, Any] = None
    ) -> PlanResult:
        """
        规划决策。
        
        Args:
            goal: 目标
            context: 上下文
        
        Returns:
            PlanResult 规划结果
        """
        prompt = f"""请为以下目标制定执行计划：

目标: {goal}

请列出具体步骤，包括：
1. 步骤描述
2. 负责 Agent
3. 依赖关系
4. 预计时间

请以 JSON 格式输出。"""
        
        result = await self.think(prompt, context)
        
        # 解析计划
        return self._parse_plan_result(result.text)
    
    async def generate(
        self,
        prompt: str,
        context: Dict[str, Any] = None,
        system_prompt: str = None
    ) -> str:
        """
        生成内容。
        
        Args:
            prompt: 用户提示
            context: 上下文
            system_prompt: 系统提示
        
        Returns:
            生成的文本
        """
        messages = []
        
        # 系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # 上下文
        if context and context.get("history"):
            for msg in context["history"][-5:]:  # 最近5条
                messages.append(msg)
        
        # 用户提示
        messages.append({"role": "user", "content": prompt})
        
        result = await self._call_api(self.primary_model, messages)
        return result.text
    
    def _build_messages(
        self,
        prompt: str,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """构建消息列表"""
        messages = []
        
        # 上下文
        if context and context.get("history"):
            for msg in context["history"][-5:]:
                messages.append(msg)
        
        # 当前提示
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    async def _call_api(
        self,
        model: str,
        messages: List[Dict[str, str]]
    ) -> GenerationResult:
        """调用 API"""
        import requests
        
        config = self.MODEL_CONFIG.get(model, {})
        provider = config.get("provider", ModelProvider.ZHIPU)
        
        if provider == ModelProvider.ZHIPU:
            return await self._call_zhipu(model, messages)
        elif provider == ModelProvider.MINIMAX:
            return await self._call_minimax(model, messages)
        else:
            raise ValueError(f"不支持的模型提供商: {provider}")
    
    async def _call_zhipu(
        self,
        model: str,
        messages: List[Dict[str, str]]
    ) -> GenerationResult:
        """调用智谱 API"""
        import requests
        
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        return GenerationResult(
            text=result["choices"][0]["message"]["content"],
            model=model,
            tokens_used=result.get("usage", {}).get("total_tokens", 0),
            finish_reason=result["choices"][0].get("finish_reason", "stop")
        )
    
    async def _call_minimax(
        self,
        model: str,
        messages: List[Dict[str, str]]
    ) -> GenerationResult:
        """调用 MiniMax API"""
        import requests
        
        url = f"{self.api_base}/text/chatcompletion_v2"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        return GenerationResult(
            text=result["choices"][0]["message"]["content"],
            model=model,
            tokens_used=result.get("usage", {}).get("total_tokens", 0),
            finish_reason=result["choices"][0].get("finish_reason", "stop")
        )
    
    def _parse_reasoning_result(self, text: str) -> ReasoningResult:
        """解析推理结果"""
        # 简单解析
        return ReasoningResult(
            reasoning=text,
            conclusion=text.split("\n")[-1] if "\n" in text else text,
            confidence=0.8,
            evidence=[]
        )
    
    def _parse_plan_result(self, text: str) -> PlanResult:
        """解析计划结果"""
        # 尝试解析 JSON
        try:
            # 提取 JSON
            import re
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                steps_data = json.loads(json_match.group())
                steps = [
                    PlanStep(
                        step_id=i,
                        description=s.get("description", ""),
                        agent_id=s.get("agent_id", "00"),
                        dependencies=s.get("dependencies", [])
                    )
                    for i, s in enumerate(steps_data)
                ]
                return PlanResult(
                    steps=steps,
                    estimated_time=len(steps) * 60,
                    resources=[],
                    success_rate=0.8
                )
        except Exception:
            pass
        
        # 简单解析
        return PlanResult(
            steps=[],
            estimated_time=0,
            resources=[],
            success_rate=0.0
        )


# 全局前额叶
_prefrontal: Optional[Prefrontal] = None


def get_prefrontal() -> Prefrontal:
    """获取全局前额叶实例"""
    global _prefrontal
    if _prefrontal is None:
        _prefrontal = Prefrontal()
    return _prefrontal


def init_prefrontal(
    primary_model: str = "glm-5",
    fallback_model: str = "MiniMax-M2.5",
    api_key: str = None,
    **kwargs
) -> Prefrontal:
    """初始化前额叶"""
    global _prefrontal
    _prefrontal = Prefrontal(
        primary_model=primary_model,
        fallback_model=fallback_model,
        api_key=api_key,
        **kwargs
    )
    return _prefrontal


__all__ = [
    "Prefrontal",
    "ReasoningResult",
    "ReasoningStep",
    "PlanResult",
    "PlanStep",
    "GenerationResult",
    "ModelProvider",
    "get_prefrontal",
    "init_prefrontal",
]
