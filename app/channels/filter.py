# -*- coding: utf-8 -*-
"""
Channel Event Filter - 事件过滤器

用于过滤不需要处理的事件，避免报错。
"""

from typing import Dict, Any, Optional


class ChannelEventFilter:
    """Channel 事件过滤器"""
    
    def __init__(
        self,
        ignore_events: list = None,
        ignore_users: list = None,
        ignore_keywords: list = None
    ):
        self.ignore_events = set(ignore_events or [])
        self.ignore_users = set(ignore_users or [])
        self.ignore_keywords = ignore_keywords or []
    
    def should_process(self, event: Dict[str, Any]) -> bool:
        """
        判断事件是否需要处理。
        
        Args:
            event: 事件字典，需要包含 type, user_id, content 等字段
        
        Returns:
            True = 处理事件
            False = 忽略事件
        """
        # 1. 检查事件类型
        event_type = event.get("type", "")
        if event_type in self.ignore_events:
            return False
        
        # 2. 检查用户
        user_id = event.get("user_id", "")
        if user_id in self.ignore_users:
            return False
        
        # 3. 检查关键词
        content = str(event.get("content", ""))
        for keyword in self.ignore_keywords:
            if keyword in content:
                return False
        
        return True
    
    def filter_events(self, events: list) -> list:
        """过滤事件列表"""
        return [e for e in events if self.should_process(e)]


def create_filter_from_config(config: Any) -> ChannelEventFilter:
    """
    从配置创建过滤器。
    
    Args:
        config: Channel 配置对象
    
    Returns:
        ChannelEventFilter 实例
    """
    filters = getattr(config, "filters", None)
    
    if filters is None:
        return ChannelEventFilter()
    
    return ChannelEventFilter(
        ignore_events=getattr(filters, "ignore_events", []) or [],
        ignore_users=getattr(filters, "ignore_users", []) or [],
        ignore_keywords=getattr(filters, "ignore_keywords", []) or []
    )


__all__ = [
    "ChannelEventFilter",
    "create_filter_from_config",
]
