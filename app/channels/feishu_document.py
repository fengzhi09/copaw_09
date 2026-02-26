# -*- coding: utf-8 -*-
"""
Feishu Document - 飞书文档管理

支持：
- 上传/下载文档
- 读写飞书文档
- 多维表格操作
- 知识库管理
"""

import json
import base64
import hashlib
import time
import asyncio
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import logger


class FeishuDocument:
    """飞书文档管理"""
    
    def __init__(self, channel):
        """
        初始化文档管理。
        
        Args:
            channel: FeishuChannel 实例
        """
        self._channel = channel
    
    async def _get_token(self) -> str:
        """获取 tenant_access_token"""
        return await self._channel._get_tenant_access_token()
    
    # ==================== 文件操作 ====================
    
    async def upload_file(self, file_path: str, file_type: str = "stream") -> Optional[str]:
        """
        上传文件到飞书云空间。
        
        Args:
            file_path: 本地文件路径
            file_type: 文件类型 (stream/doc/image/audio/video/pdf)
        
        Returns:
            file_token 或 None
        """
        token = await self._get_token()
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.warning(f"[Feishu] 文件不存在: {file_path}")
            return None
        
        # 读取文件内容
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # 构建请求
        url = "https://open.feishu.cn/open-apis/drive/v1/files/upload_all"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        files = {
            "file_name": (None, file_path.name),
            "file_type": (None, file_type),
            "file_size": (None, str(len(file_content))),
            "file": (file_path.name, file_content, "application/octet-stream"),
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, files=files, timeout=60)
            data = response.json()
            
            if data.get("code") == 0:
                return data["data"]["file_token"]
            else:
                logger.error(f"[Feishu] 上传文件失败: {data}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 上传文件异常: {e}")
            return None
    
    async def download_file(self, file_token: str, save_path: str) -> bool:
        """
        下载飞书云空间文件到本地。
        
        Args:
            file_token: 飞书文件 token
            save_path: 保存路径
        
        Returns:
            是否成功
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/drive/v1/files/{file_token}/download"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                logger.error(f"[Feishu] 下载文件失败: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"[Feishu] 下载文件异常: {e}")
            return False
    
    # ==================== 文档操作 ====================
    
    async def create_document(self, doc_type: str = "doc", title: str = "新文档") -> Optional[str]:
        """
        创建飞书文档。
        
        Args:
            doc_type: 文档类型 (doc/sheet/bitable)
            title: 文档标题
        
        Returns:
            document_id 或 None
        """
        token = await self._get_token()
        
        if doc_type == "doc":
            url = "https://open.feishu.cn/open-apis/doc/v1/documents"
            data = {
                "document": {
                    "title": title,
                    "document_type": "docx"
                }
            }
        elif doc_type == "sheet":
            url = "https://open.feishu.cn/open-apis/sheets/v3/spreadsheets"
            data = {
                "spreadsheet": {
                    "title": title
                }
            }
        elif doc_type == "bitable":
            url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
            data = {
                "name": title
            }
        else:
            logger.error(f"[Feishu] 不支持的文档类型: {doc_type}")
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                if doc_type == "doc":
                    return result["data"]["document"]["document_id"]
                elif doc_type == "sheet":
                    return result["data"]["spreadsheet"]["spreadsheet_id"]
                elif doc_type == "bitable":
                    return result["data"]["app"]["app_token"]
            else:
                logger.error(f"[Feishu] 创建文档失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 创建文档异常: {e}")
            return None
    
    async def get_document(self, document_id: str) -> Optional[Dict]:
        """
        获取飞书文档内容。
        
        Args:
            document_id: 文档 ID
        
        Returns:
            文档内容 dict 或 None
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/doc/v1/documents/{document_id}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["document"]
            else:
                logger.error(f"[Feishu] 获取文档失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 获取文档异常: {e}")
            return None
    
    async def update_document(self, document_id: str, blocks: List[Dict]) -> bool:
        """
        更新飞书文档内容。
        
        Args:
            document_id: 文档 ID
            blocks: 文档块列表
        
        Returns:
            是否成功
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/doc/v1/documents/{document_id}/blocks"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "requests": [
                {
                    "method": "insert",
                    "body": {
                        "location": {"index": 1},
                        "children": blocks
                    }
                }
            ]
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return True
            else:
                logger.error(f"[Feishu] 更新文档失败: {result}")
                return False
        except Exception as e:
            logger.error(f"[Feishu] 更新文档异常: {e}")
            return False
    
    # ==================== 多维表格 ====================
    
    async def create_bitable(self, space_id: str, name: str) -> Optional[str]:
        """
        创建多维表格。
        
        Args:
            space_id: 知识库空间 ID
            name: 表格名称
        
        Returns:
            bitable_id 或 None
        """
        token = await self._get_token()
        
        url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {
            "name": name,
            "folder_token": space_id
        }
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["app"]["app_token"]
            else:
                logger.error(f"[Feishu] 创建多维表格失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 创建多维表格异常: {e}")
            return None
    
    async def get_bitable_tables(self, bitable_id: str) -> Optional[List[Dict]]:
        """
        获取多维表格的所有表。
        
        Args:
            bitable_id: 多维表格 ID
        
        Returns:
            表列表或 None
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_id}/tables"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["items"]
            else:
                logger.error(f"[Feishu] 获取多维表格失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 获取多维表格异常: {e}")
            return None
    
    async def get_bitable_records(
        self,
        bitable_id: str,
        table_id: str,
        filter: str = "",
        limit: int = 100
    ) -> Optional[List[Dict]]:
        """
        获取多维表格记录。
        
        Args:
            bitable_id: 多维表格 ID
            table_id: 表 ID
            filter: 过滤条件
            limit: 返回数量限制
        
        Returns:
            记录列表或 None
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_id}/tables/{table_id}/records"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        params = {"limit": limit}
        if filter:
            params["filter"] = filter
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=params, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["items"]
            else:
                logger.error(f"[Feishu] 获取记录失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 获取记录异常: {e}")
            return None
    
    async def create_bitable_record(
        self,
        bitable_id: str,
        table_id: str,
        fields: Dict[str, Any]
    ) -> Optional[str]:
        """
        创建多维表格记录。
        
        Args:
            bitable_id: 多维表格 ID
            table_id: 表 ID
            fields: 字段值
        
        Returns:
            record_id 或 None
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_id}/tables/{table_id}/records"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {"fields": fields}
        
        try:
            import requests
            response = requests.post(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["record"]["record_id"]
            else:
                logger.error(f"[Feishu] 创建记录失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 创建记录异常: {e}")
            return None
    
    async def update_bitable_record(
        self,
        bitable_id: str,
        table_id: str,
        record_id: str,
        fields: Dict[str, Any]
    ) -> bool:
        """
        更新多维表格记录。
        
        Args:
            bitable_id: 多维表格 ID
            table_id: 表 ID
            record_id: 记录 ID
            fields: 字段值
        
        Returns:
            是否成功
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{bitable_id}/tables/{table_id}/records/{record_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        data = {"fields": fields}
        
        try:
            import requests
            response = requests.put(url, headers=headers, json=data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return True
            else:
                logger.error(f"[Feishu] 更新记录失败: {result}")
                return False
        except Exception as e:
            logger.error(f"[Feishu] 更新记录异常: {e}")
            return False
    
    # ==================== 知识库 ====================
    
    async def list_spaces(self) -> Optional[List[Dict]]:
        """
        获取知识库空间列表。
        
        Returns:
            知识库列表或 None
        """
        token = await self._get_token()
        
        url = "https://open.feishu.cn/open-apis/knowledge/v1/spaces"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["items"]
            else:
                logger.error(f"[Feishu] 获取知识库失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 获取知识库异常: {e}")
            return None
    
    async def list_space_nodes(
        self,
        space_id: str,
        parent_node_id: str = "",
        limit: int = 50
    ) -> Optional[List[Dict]]:
        """
        获取知识库目录结构。
        
        Args:
            space_id: 知识库空间 ID
            parent_node_id: 父节点 ID（空则为根目录）
            limit: 返回数量限制
        
        Returns:
            节点列表或 None
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/knowledge/v1/spaces/{space_id}/nodes"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        params = {"parent_node_token": parent_node_id} if parent_node_id else {}
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=params, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["items"]
            else:
                logger.error(f"[Feishu] 获取目录失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 获取目录异常: {e}")
            return None
    
    async def get_knowledge_doc(self, document_id: str) -> Optional[Dict]:
        """
        获取知识库文档内容。
        
        Args:
            document_id: 文档 ID
        
        Returns:
            文档内容或 None
        """
        token = await self._get_token()
        
        url = f"https://open.feishu.cn/open-apis/knowledge/v1/documents/{document_id}"
        headers = {
            "Authorization": f"Bearer {token}",
        }
        
        try:
            import requests
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return result["data"]["document"]
            else:
                logger.error(f"[Feishu] 获取知识库文档失败: {result}")
                return None
        except Exception as e:
            logger.error(f"[Feishu] 获取知识库文档异常: {e}")
            return None
    
    async def create_knowledge_doc(
        self,
        space_id: str,
        parent_node_id: str,
        title: str,
        doc_type: str = "doc"
    ) -> Optional[str]:
        """
        在知识库中创建文档。
        
        Args:
            space_id: 知识库空间 ID
            parent_node_id: 父目录节点 ID
            title: 文档标题
            doc_type: 文档类型 (doc/sheet/bitable)
        
        Returns:
            document_id 或 None
        """
        token = await self._get_token()
        
        url = "https://open.feishu.cn/open-apis/knowledge/v1/documents"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        # 先创建文档
        if doc_type == "doc":
            create_url = "https://open.feishu.cn/open-apis/doc/v1/documents"
            create_data = {
                "document": {
                    "title": title,
                    "document_type": "docx"
                }
            }
        else:
            logger.warning(f"[Feishu] 知识库暂不支持类型: {doc_type}")
            return None
        
        try:
            import requests
            # 创建文档
            response = requests.post(create_url, headers=headers, json=create_data, timeout=30)
            result = response.json()
            
            if result.get("code") != 0:
                logger.error(f"[Feishu] 创建文档失败: {result}")
                return None
            
            document_id = result["data"]["document"]["document_id"]
            
            # 添加到知识库
            add_url = f"https://open.feishu.cn/open-apis/knowledge/v1/spaces/{space_id}/nodes"
            add_data = {
                "obj_type": "doc",
                "obj_token": document_id,
                "parent_node_token": parent_node_id
            }
            
            response = requests.post(add_url, headers=headers, json=add_data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                return document_id
            else:
                logger.error(f"[Feishu] 添加到知识库失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"[Feishu] 创建知识库文档异常: {e}")
            return None


__all__ = ["FeishuDocument"]
