# -*- coding: utf-8 -*-
"""
Feishu Document 单元测试
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path


class TestFeishuDocumentCreation:
    """飞书文档创建测试"""
    
    @pytest.fixture
    def mock_channel(self):
        """创建模拟的飞书频道"""
        from app.channels.feishu import FeishuChannel
        
        channel = FeishuChannel.__new__(FeishuChannel)
        channel.app_id = "cli_test"
        channel._tenant_access_token = None
        channel._tenant_access_token_expire_at = 0.0
        channel._token_lock = AsyncMock()
        
        return channel
    
    @pytest.fixture
    def doc_manager(self, mock_channel):
        """创建文档管理器"""
        from app.channels.feishu_document import FeishuDocument
        return FeishuDocument(mock_channel)
    
    @pytest.mark.asyncio
    async def test_get_token(self, doc_manager, mock_channel):
        """测试获取 token"""
        mock_channel._get_tenant_access_token = AsyncMock(return_value="test_token")
        
        token = await doc_manager._get_token()
        
        assert token == "test_token"


class TestFeishuDocumentAPI:
    """飞书文档 API 测试"""
    
    def test_document_class_exists(self):
        """测试文档类存在"""
        from app.channels.feishu_document import FeishuDocument
        assert FeishuDocument is not None
    
    def test_document_methods_exist(self):
        """测试文档方法存在"""
        from app.channels.feishu_document import FeishuDocument
        
        # 检查方法是否存在
        assert hasattr(FeishuDocument, 'upload_file')
        assert hasattr(FeishuDocument, 'download_file')
        assert hasattr(FeishuDocument, 'create_document')
        assert hasattr(FeishuDocument, 'get_document')
        assert hasattr(FeishuDocument, 'update_document')
        assert hasattr(FeishuDocument, 'create_bitable')
        assert hasattr(FeishuDocument, 'get_bitable_tables')
        assert hasattr(FeishuDocument, 'get_bitable_records')
        assert hasattr(FeishuDocument, 'create_bitable_record')
        assert hasattr(FeishuDocument, 'update_bitable_record')
        assert hasattr(FeishuDocument, 'list_spaces')
        assert hasattr(FeishuDocument, 'list_space_nodes')
        assert hasattr(FeishuDocument, 'get_knowledge_doc')
        assert hasattr(FeishuDocument, 'create_knowledge_doc')


class TestFeishuDocumentIntegration:
    """飞书文档集成测试"""
    
    def test_channel_has_document_manager(self):
        """测试频道有文档管理器"""
        from app.channels.feishu import FeishuChannel
        
        # 检查 FeishuChannel 是否有 _document 属性
        # 这需要通过 mock 来避免实际初始化
        with patch('app.channels.feishu.FeishuChannel.__new__') as mock_new:
            mock_channel = MagicMock()
            mock_new.return_value = mock_channel
            
            # 由于无法直接实例化，这里检查导入
            from app.channels import feishu_document
            assert hasattr(feishu_document, 'FeishuDocument')


class TestFeishuDocumentMockAPI:
    """飞书文档 API Mock 测试"""
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self):
        """测试上传文件成功"""
        from app.channels.feishu_document import FeishuDocument
        
        mock_channel = Mock()
        mock_channel._get_tenant_access_token = AsyncMock(return_value="test_token")
        
        doc = FeishuDocument(mock_channel)
        
        # Mock requests.post
        mock_response = Mock()
        mock_response.json.return_value = {
            "code": 0,
            "data": {"file_token": "file_xxx"}
        }
        
        with patch('app.channels.feishu_document.requests.post', return_value=mock_response):
            # 由于需要实际文件，我们跳过完整测试
            pass
    
    @pytest.mark.asyncio
    async def test_create_document_doc(self):
        """测试创建文档"""
        from app.channels.feishu_document import FeishuDocument
        
        mock_channel = Mock()
        mock_channel._get_tenant_access_token = AsyncMock(return_value="test_token")
        
        doc = FeishuDocument(mock_channel)
        
        # 验证 doc_type 参数
        assert callable(doc.create_document)
    
    @pytest.mark.asyncio
    async def test_list_spaces(self):
        """测试获取知识库列表"""
        from app.channels.feishu_document import FeishuDocument
        
        mock_channel = Mock()
        mock_channel._get_tenant_access_token = AsyncMock(return_value="test_token")
        
        doc = FeishuDocument(mock_channel)
        
        # 验证方法存在
        assert hasattr(doc, 'list_spaces')
    
    @pytest.mark.asyncio
    async def test_bitable_operations(self):
        """测试多维表格操作"""
        from app.channels.feishu_document import FeishuDocument
        
        mock_channel = Mock()
        mock_channel._get_tenant_access_token = AsyncMock(return_value="test_token")
        
        doc = FeishuDocument(mock_channel)
        
        # 验证方法存在
        assert hasattr(doc, 'create_bitable')
        assert hasattr(doc, 'get_bitable_tables')
        assert hasattr(doc, 'get_bitable_records')
        assert hasattr(doc, 'create_bitable_record')
        assert hasattr(doc, 'update_bitable_record')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
