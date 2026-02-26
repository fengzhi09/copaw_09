# -*- coding: utf-8 -*-
"""
Agent Router 单元测试
"""

import pytest
from app.router import AgentRouter, get_router


class TestAgentRouter:
    """AgentRouter 测试类"""
    
    def test_route_default(self):
        """测试默认路由到 00"""
        router = AgentRouter()
        
        # 空消息返回默认 00
        assert router.route("") == "00"
    
    def test_route_00_keywords(self):
        """测试 00 号管理高手关键词"""
        router = AgentRouter()
        
        assert router.route("创建新Agent") == "00"
        assert router.route("系统配置") == "00"
        assert router.route("管理一下") == "00"
    
    def test_route_01_keywords(self):
        """测试 01 号学霸关键词"""
        router = AgentRouter()
        
        assert router.route("搜索论文") == "01"
        assert router.route("学术调研") == "01"
        assert router.route("找一下google") == "01"
    
    def test_route_02_keywords(self):
        """测试 02 号编程高手关键词"""
        router = AgentRouter()
        
        assert router.route("代码开发") == "02"
        assert router.route("修复bug") == "02"
        assert router.route("github项目") == "02"
    
    def test_route_03_keywords(self):
        """测试 03 号创意青年关键词"""
        router = AgentRouter()
        
        assert router.route("写一段文案") == "03"
        assert router.route("创意灵感") == "03"
        assert router.route("小红书内容") == "03"
    
    def test_route_04_keywords(self):
        """测试 04 号统计学长关键词"""
        router = AgentRouter()
        
        assert router.route("统计报表") == "04"
        assert router.route("本月成本") == "04"
        assert router.route("每日复盘") == "04"
    
    def test_route_no_match(self):
        """测试无匹配时返回默认"""
        router = AgentRouter()
        
        # 不匹配的关键词返回 00
        assert router.route("你好") == "00"
        assert router.route("今天天气") == "00"
    
    def test_route_case_insensitive(self):
        """测试大小写不敏感"""
        router = AgentRouter()
        
        assert router.route("搜索论文") == "01"
        assert router.route("SEARCH论文") == "01"
    
    def test_route_with_user_id(self):
        """测试带用户ID的路由"""
        router = AgentRouter()
        
        # user_id 不影响路由结果
        result = router.route("搜索论文", user_id="test_user")
        assert result == "01"
    
    def test_get_agent_config(self):
        """测试获取 Agent 配置"""
        router = AgentRouter()
        
        config = router.get_agent_config("01")
        assert config is not None
    
    def test_get_agent_config_nonexistent(self):
        """测试获取不存在的 Agent"""
        router = AgentRouter()
        
        config = router.get_agent_config("99")
        assert config is None
    
    def test_list_agents(self):
        """测试列出所有 Agent"""
        router = AgentRouter()
        
        agents = router.list_agents()
        assert len(agents) >= 5  # 至少 00-04


class TestGetRouter:
    """全局路由器测试"""
    
    def test_get_router_singleton(self):
        """测试单例模式"""
        router1 = get_router()
        router2 = get_router()
        
        assert router1 is router2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
