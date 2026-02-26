# -*- coding: utf-8 -*-
"""
Gateway Filter 单元测试
"""

import pytest
from app.gateway.filter import GatewayFilter


class TestGatewayFilter:
    """GatewayFilter 测试类"""
    
    def test_default_allows(self):
        """测试默认配置允许所有事件"""
        filter = GatewayFilter()
        event = {
            "type": "message",
            "user_id": "user1",
            "content": "Hello"
        }
        
        assert filter.should_process(event) is True
    
    def test_ignore_event_type(self):
        """测试忽略事件类型"""
        filter = GatewayFilter(ignore_event_types={"heartbeat", "typing"})
        
        # 被忽略的事件
        assert filter.should_process({"type": "heartbeat"}) is False
        assert filter.should_process({"type": "typing"}) is False
        
        # 正常事件（类型不在忽略列表中）
        assert filter.should_process({"type": "message"}) is True
    
    def test_ignore_event_type_default(self):
        """测试默认事件类型过滤"""
        filter = GatewayFilter()
        
        # 默认忽略 heartbeat
        assert filter.should_process({"type": "heartbeat"}) is False
        # 默认忽略 typing
        assert filter.should_process({"type": "typing"}) is False
        
        # 正常事件
        assert filter.should_process({"type": "message"}) is True
    
    def test_ignore_user(self):
        """测试忽略用户"""
        filter = GatewayFilter(ignore_user_ids={"bad_user"})
        
        assert filter.should_process({
            "type": "message",
            "user_id": "bad_user",
            "content": "Hello"
        }) is False
        
        assert filter.should_process({
            "type": "message",
            "user_id": "good_user",
            "content": "Hello"
        }) is True
    
    def test_ignore_keyword(self):
        """测试忽略关键词"""
        filter = GatewayFilter(ignore_keywords=["spam", "广告"])
        
        assert filter.should_process({
            "type": "message",
            "user_id": "user1",
            "content": "This is spam message"
        }) is False
        
        assert filter.should_process({
            "type": "message",
            "user_id": "user1",
            "content": "This is a good message"
        }) is True
    
    def test_ignore_chinese_keyword(self):
        """测试中文关键词"""
        filter = GatewayFilter(ignore_keywords=["广告", "垃圾"])
        
        assert filter.should_process({
            "type": "message",
            "content": "加微信xxxx广告"
        }) is False
    
    def test_empty_content_filtered(self):
        """测试空消息被过滤"""
        filter = GatewayFilter(min_content_length=1)
        
        assert filter.should_process({
            "type": "message",
            "content": ""
        }) is False
        
        assert filter.should_process({
            "type": "message",
            "content": "a"
        }) is True
    
    def test_content_length_min(self):
        """测试最小长度限制"""
        filter = GatewayFilter(min_content_length=5)
        
        assert filter.should_process({
            "type": "message",
            "content": "Hi"  # 太短
        }) is False
        
        assert filter.should_process({
            "type": "message",
            "content": "Hello"  # 刚好
        }) is True
    
    def test_content_length_max(self):
        """测试最大长度限制"""
        filter = GatewayFilter(max_content_length=10)
        
        assert filter.should_process({
            "type": "message",
            "content": "Hello World"  # 11 字符
        }) is False
        
        assert filter.should_process({
            "type": "message",
            "content": "Hello"  # 5 字符
        }) is True
    
    def test_add_ignore_user(self):
        """测试动态添加忽略用户"""
        filter = GatewayFilter()
        
        filter.add_ignore_user("user1")
        assert "user1" in filter.ignore_user_ids
        
        assert filter.should_process({
            "type": "message",
            "user_id": "user1",
            "content": "Hello"
        }) is False
    
    def test_remove_ignore_user(self):
        """测试移除忽略用户"""
        filter = GatewayFilter(ignore_user_ids={"user1"})
        
        filter.remove_ignore_user("user1")
        assert "user1" not in filter.ignore_user_ids
    
    def test_add_ignore_keyword(self):
        """测试动态添加关键词"""
        filter = GatewayFilter()
        
        filter.add_ignore_keyword("test")
        assert "test" in filter.ignore_keywords
    
    def test_multiple_filters(self):
        """测试多重过滤"""
        filter = GatewayFilter(
            ignore_event_types={"heartbeat"},
            ignore_user_ids={"bad_user"},
            ignore_keywords=["spam"],
            min_content_length=1,
            max_content_length=100
        )
        
        # 所有条件都不满足 - 通过
        assert filter.should_process({
            "type": "message",
            "user_id": "good_user",
            "content": "Hello World"
        }) is True
    
    def test_event_missing_fields(self):
        """测试事件缺少字段"""
        filter = GatewayFilter()
        
        # 缺少 type 字段 - 默认为 message，允许通过
        assert filter.should_process({}) is True
        
        # 缺少 content - 允许通过（空内容）
        assert filter.should_process({
            "type": "message",
            "user_id": "user1"
        }) is True
        
        # 有内容则正常
        assert filter.should_process({
            "type": "message",
            "content": "Hello"
        }) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
