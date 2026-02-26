# -*- coding: utf-8 -*-
"""
Gateway Filter - 事件过滤

负责过滤不需要处理的消息事件。
"""

from typing import Dict, Any, List, Set
from dataclasses import dataclass, field


@dataclass
class GatewayFilter:
    """Gateway 事件过滤器"""
    
    # 忽略的事件类型
    ignore_event_types: Set[str] = field(default_factory=lambda: {
        "heartbeat", "typing", "read_receipt", "ack"
    })
    
    # 忽略的用户 ID
    ignore_user_ids: Set[str] = field(default_factory=set)
    
    # 忽略的关键词
    ignore_keywords: List[str] = field(default_factory=list)
    
    # 最小消息长度
    min_content_length: int = 0
    
    # 最大消息长度
    max_content_length: int = 10000
    
    def should_process(self, event: Dict[str, Any]) -> bool:
        """
        判断事件是否需要处理。
        
        Args:
            event: 事件字典，包含 type, user_id, content 等
        
        Returns:
            True = 处理, False = 忽略
        """
        # 1. 检查事件类型
        event_type = event.get("type", "")
        if event_type in self.ignore_event_types:
            return False
        
        # 2. 检查用户
        user_id = event.get("user_id", "")
        if user_id in self.ignore_user_ids:
            return False
        
        # 3. 检查关键词
        content = str(event.get("content", ""))
        if content.strip() == "":
            return False
        
        # 4. 检查关键词过滤
        for keyword in self.ignore_keywords:
            if keyword in content:
                return False
        
        # 5. 检查消息长度
        content_len = len(content)
        if content_len < self.min_content_length:
            return False
        if content_len > self.max_content_length:
            return False
        
        return True
    
    def add_ignore_user(self, user_id: str):
        """添加忽略用户"""
        self.ignore_user_ids.add(user_id)
    
    def remove_ignore_user(self, user_id: str):
        """移除忽略用户"""
        self.ignore_user_ids.discard(user_id)
    
    def add_ignore_keyword(self, keyword: str):
        """添加忽略关键词"""
        self.ignore_keywords.append(keyword)


# 全局过滤器
_filter: "GatewayFilter" = None


def get_gateway_filter() -> GatewayFilter:
    """获取全局过滤器"""
    global _filter
    if _filter is None:
        _filter = GatewayFilter()
    return _filter


def init_gateway_filter(config: Dict[str, Any]) -> GatewayFilter:
    """从配置初始化过滤器"""
    global _filter
    _filter = GatewayFilter(
        ignore_event_types=set(config.get("ignore_event_types", [])),
        ignore_user_ids=set(config.get("ignore_user_ids", [])),
        ignore_keywords=config.get("ignore_keywords", []),
        min_content_length=config.get("min_content_length", 0),
        max_content_length=config.get("max_content_length", 10000),
    )
    return _filter


__all__ = [
    "GatewayFilter",
    "get_gateway_filter",
    "init_gateway_filter",
]
