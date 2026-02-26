# -*- coding: utf-8 -*-
"""
Thalamus - 丘脑模块

功能:
- 意图识别
- 消息路由
- 记忆索引
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("brain.thalamus")


class IntentType(Enum):
    """意图类型"""
    SEARCH = "search"           # 搜索
    CODE = "code"               # 编程
    CREATE = "create"           # 创作
    QUERY = "query"             # 询问
    MANAGE = "manage"           # 管理
    STATS = "stats"             # 统计
    UNKNOWN = "unknown"         # 未知


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: IntentType          # 意图类型
    confidence: float           # 置信度 0-1
    entities: Dict[str, Any]   # 实体
    next_action: str           # 下一步动作
    raw_response: str = ""      # 原始响应


@dataclass
class MemoryItem:
    """记忆项"""
    content: str
    timestamp: float
    agent_id: str
    session_id: str
    relevance: float = 0.0


class Thalamus:
    """丘脑 - 意图识别、路由、记忆"""
    
    # 关键词到意图的映射
    KEYWORD_TO_INTENT = {
        IntentType.SEARCH: ["搜索", "论文", "调研", "找", "google", "search"],
        IntentType.CODE: ["代码", "编程", "开发", "bug", "报错", "github"],
        IntentType.CREATE: ["创作", "写", "文案", "画", "视频", "小红书"],
        IntentType.QUERY: ["什么是", "怎么", "如何", "为什么", "?", "?"],
        IntentType.MANAGE: ["创建", "配置", "管理", "系统", "agent"],
        IntentType.STATS: ["统计", "报表", "成本", "复盘", "总结"],
    }
    
    # 意图到 Agent 的映射
    INTENT_TO_AGENT = {
        IntentType.SEARCH: "01",
        IntentType.CODE: "02",
        IntentType.CREATE: "03",
        IntentType.MANAGE: "00",
        IntentType.STATS: "04",
        IntentType.QUERY: "00",  # 默认问 00
    }
    
    def __init__(
        self,
        model_path: str = None,
        device: str = "cuda",
        max_length: int = 2048,
        temperature: float = 0.7,
    ):
        """
        初始化丘脑。
        
        Args:
            model_path: Qwen3 模型路径
            device: 设备 (cuda/cpu)
            max_length: 最大生成长度
            temperature: 温度参数
        """
        self.model_path = model_path
        self.device = device
        self.max_length = max_length
        self.temperature = temperature
        
        # 模型（延迟加载）
        self._model = None
        self._tokenizer = None
        
        # 记忆存储
        self._memory_store: List[MemoryItem] = []
        
        logger.info(f"[Thalamus] 初始化完成 (device={device})")
    
    def _load_model(self):
        """加载模型"""
        if self._model is not None:
            return
        
        if not self.model_path:
            logger.warning("[Thalamus] 未配置模型路径，使用关键词匹配模式")
            return
        
        try:
            # TODO: 实际加载 Qwen3 模型
            # from transformers import AutoModelForCausalLM, AutoTokenizer
            # self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            # self._model = AutoModelForCausalLM.from_pretrained(
            #     self.model_path,
            #     device_map=self.device,
            #     load_in_8bit=True
            # )
            logger.info(f"[Thalamus] 模型已加载: {self.model_path}")
        except Exception as e:
            logger.error(f"[Thalamus] 模型加载失败: {e}")
    
    def understand_intent(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> IntentResult:
        """
        理解用户意图。
        
        Args:
            message: 用户消息
            context: 上下文信息
        
        Returns:
            IntentResult 意图结果
        """
        # 如果有模型，使用模型识别
        if self._model is not None:
            return self._understand_intent_with_model(message, context)
        
        # 否则使用关键词匹配
        return self._understand_intent_with_keywords(message, context)
    
    def _understand_intent_with_model(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> IntentResult:
        """使用模型识别意图"""
        # TODO: 实现基于模型的意图识别
        prompt = f"""分析用户消息的意图。
消息: {message}

可选意图: search, code, create, query, manage, stats

输出 JSON 格式:
{{"intent": "...", "confidence": 0.0-1.0, "entities": {{}}}}"""
        
        # 调用模型
        # response = self._generate(prompt)
        
        # 解析结果
        return self._understand_intent_with_keywords(message, context)
    
    def _understand_intent_with_keywords(
        self,
        message: str,
        context: Dict[str, Any] = None
    ) -> IntentResult:
        """使用关键词识别意图"""
        message_lower = message.lower()
        scores = {intent: 0 for intent in IntentType}
        
        # 关键词计分
        for intent, keywords in self.KEYWORD_TO_INTENT.items():
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    scores[intent] += 1
        
        # 找出最高分
        best_intent = max(scores, key=scores.get)
        confidence = min(scores[best_intent] / 3.0, 1.0) if scores[best_intent] > 0 else 0.0
        
        # 如果没有匹配，返回 UNKNOWN
        if scores[best_intent] == 0:
            best_intent = IntentType.UNKNOWN
            confidence = 0.5
        
        # 提取实体
        entities = self._extract_entities(message)
        
        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            entities=entities,
            next_action=self._decide_next_action(best_intent)
        )
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """提取实体"""
        entities = {}
        
        # 提取 Agent 编号
        import re
        agent_match = re.search(r'(?:agent|号|00|01|02|03|04)[：:\s]*(\d{2})', message)
        if agent_match:
            entities["agent_id"] = agent_match.group(1)
        
        # 提取关键词
        keywords = []
        for keywords_list in self.KEYWORD_TO_INTENT.values():
            for kw in keywords_list:
                if kw in message.lower():
                    keywords.append(kw)
        if keywords:
            entities["keywords"] = keywords
        
        return entities
    
    def _decide_next_action(self, intent: IntentType) -> str:
        """决定下一步动作"""
        action_map = {
            IntentType.SEARCH: "route_to_agent",
            IntentType.CODE: "route_to_agent",
            IntentType.CREATE: "route_to_agent",
            IntentType.MANAGE: "process_manage",
            IntentType.STATS: "route_to_agent",
            IntentType.QUERY: "route_to_agent",
            IntentType.UNKNOWN: "route_to_default",
        }
        return action_map.get(intent, "route_to_default")
    
    def route_message(
        self,
        message: str,
        intent: IntentResult = None
    ) -> str:
        """
        路由消息到合适的 Agent。
        
        Args:
            message: 用户消息
            intent: 意图结果（可选）
        
        Returns:
            Agent ID
        """
        # 如果没有意图，先识别
        if intent is None:
            intent = self.understand_intent(message)
        
        # 从意图获取 Agent
        agent_id = self.INTENT_TO_AGENT.get(intent.intent, "00")
        
        # 如果有实体中的 agent_id，使用它
        if intent.entities.get("agent_id"):
            agent_id = intent.entities["agent_id"]
        
        logger.info(f"[Thalamus] 消息路由: {message[:30]}... -> Agent {agent_id}")
        
        return agent_id
    
    def retrieve_memory(
        self,
        query: str,
        user_id: str = None,
        limit: int = 5
    ) -> List[MemoryItem]:
        """
        检索记忆。
        
        Args:
            query: 查询内容
        user_id: 用户 ID
            limit: 返回数量
        
        Returns:
            相关记忆列表
        """
        # TODO: 实现向量检索
        # 目前返回空列表
        results = []
        
        # 过滤用户
        if user_id:
            results = [m for m in self._memory_store if m.session_id == user_id]
        
        # 按相关性排序
        results.sort(key=lambda x: x.relevance, reverse=True)
        
        return results[:limit]
    
    def add_memory(self, item: MemoryItem):
        """添加记忆"""
        self._memory_store.append(item)
        
        # 限制记忆数量
        if len(self._memory_store) > 1000:
            self._memory_store = self._memory_store[-1000:]
    
    def _generate(self, prompt: str) -> str:
        """生成文本（待实现）"""
        # TODO: 实现模型生成
        return ""


# 全局丘脑
_thalamus: Optional[Thalamus] = None


def get_thalamus() -> Thalamus:
    """获取全局丘脑实例"""
    global _thalamus
    if _thalamus is None:
        _thalamus = Thalamus()
    return _thalamus


def init_thalamus(
    model_path: str = None,
    device: str = "cuda",
    **kwargs
) -> Thalamus:
    """初始化丘脑"""
    global _thalamus
    _thalamus = Thalamus(
        model_path=model_path,
        device=device,
        **kwargs
    )
    return _thalamus


__all__ = [
    "Thalamus",
    "IntentResult",
    "IntentType",
    "MemoryItem",
    "get_thalamus",
    "init_thalamus",
]
