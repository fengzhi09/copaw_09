# -*- coding: utf-8 -*-
"""
Gateway Auth 单元测试
"""

import pytest
from app.gateway.auth import (
    GatewayAuth,
    AuthResult,
    AuthResponse,
    UserPermission,
)


class TestGatewayAuth:
    """GatewayAuth 测试类"""
    
    def test_whitelist_pass(self):
        """测试白名单用户通过"""
        auth = GatewayAuth(allow_from=["user1", "user2"])
        result = auth.authenticate("user1")
        
        assert result.result == AuthResult.PASS
        assert result.user_permission is not None
        assert result.user_permission.user_id == "user1"
    
    def test_whitelist_reject(self):
        """测试非白名单用户被拒绝"""
        auth = GatewayAuth(allow_from=["user1"])
        result = auth.authenticate("user2")
        
        assert result.result == AuthResult.REJECT
        assert "不在白名单" in result.message
    
    def test_empty_whitelist_allows_all(self):
        """测试空白名单允许所有用户"""
        auth = GatewayAuth(allow_from=[])
        result = auth.authenticate("any_user")
        
        assert result.result == AuthResult.PASS
    
    def test_no_whitelist_allows_all(self):
        """测试无白名单配置允许所有用户"""
        auth = GatewayAuth()
        result = auth.authenticate("any_user")
        
        assert result.result == AuthResult.PASS
    
    def test_rate_limit_triggered(self):
        """测试限流触发"""
        auth = GatewayAuth(
            enable_rate_limit=True,
            rate_limit_count=2,
            rate_limit_window=60
        )
        
        # 第一次请求
        result1 = auth.authenticate("user1")
        assert result1.result == AuthResult.PASS
        
        # 第二次请求
        result2 = auth.authenticate("user1")
        assert result2.result == AuthResult.PASS
        
        # 第三次请求 - 触发限流
        result3 = auth.authenticate("user1")
        assert result3.result == AuthResult.RATE_LIMIT
    
    def test_api_key_valid(self):
        """测试有效 API Key"""
        auth = GatewayAuth(api_keys={"test_key": "user1"})
        result = auth.authenticate_api_key("test_key")
        
        assert result.result == AuthResult.PASS
        assert result.user_permission.user_id == "user1"
    
    def test_api_key_invalid(self):
        """测试无效 API Key"""
        auth = GatewayAuth(api_keys={"test_key": "user1"})
        result = auth.authenticate_api_key("invalid_key")
        
        assert result.result == AuthResult.REJECT
        assert "无效" in result.message
    
    def test_add_remove_user(self):
        """测试添加/移除白名单用户"""
        # 初始化有白名单
        auth = GatewayAuth(allow_from=[])
        
        # 添加用户
        auth.add_allow_user("user1")
        assert auth.is_allowed("user1")
        
        # 移除用户后，集合变空，按设计允许所有
        auth.remove_allow_user("user1")
        # 空集合 = 允许所有，这是预期行为
        assert auth.is_allowed("user1")
        assert auth.is_allowed("any_user")
    
    def test_user_permission_default(self):
        """测试默认用户权限"""
        auth = GatewayAuth()
        permission = auth._get_user_permission("user1")
        
        assert permission.user_id == "user1"
        assert permission.allowed is True
        assert permission.daily_credit_limit == 100.0
    
    def test_set_user_permission(self):
        """测试设置用户权限"""
        auth = GatewayAuth()
        
        permission = UserPermission(
            user_id="user1",
            allowed=True,
            agent_whitelist={"01", "02"},
            daily_credit_limit=50.0
        )
        
        auth.set_user_permission(permission)
        result = auth.authenticate("user1")
        
        assert result.user_permission.daily_credit_limit == 50.0
        assert result.user_permission.agent_whitelist == {"01", "02"}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
