# Feishu Channel 模块规格文档

> 版本：v2.0 | 状态：规划中 | 负责人：卡泡

## 一、概述

- **功能**：飞书/ Lark 消息通道，支持消息收发、文档管理、知识库
- **输入**：飞书 WebSocket 事件、HTTP API
- **输出**：消息、文档、知识库操作
- **依赖**：BaseChannel, ChannelEventFilter

## 二、功能清单

### 2.1 消息功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 收发单聊消息 | ✅ 已实现 | 私聊消息 |
| 群里@消息 | ✅ 已实现 | 群聊 @机器人 |
| 消息引用回复 | ✅ 已实现 | 回复指定消息 |
| 消息反应 | ✅ 已实现 | 点赞等 reaction |

### 2.2 文档功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 上传文档 | ⏳ 待开发 | 上传文件到云空间 |
| 下载文档 | ⏳ 待开发 | 下载云空间文件到本地 |
| 阅读飞书文档 | ⏳ 待开发 | 读取文档内容 |
| 创建飞书文档 | ⏳ 待开发 | 创建新文档 |
| 编辑飞书文档 | ⏳ 待开发 | 修改文档内容 |

### 2.3 多维表格

| 功能 | 状态 | 说明 |
|------|------|------|
| 读取多维表格 | ⏳ 待开发 | 读取表格数据 |
| 写入多维表格 | ⏳ 待开发 | 写入数据 |
| 创建多维表格 | ⏳ 待开发 | 创建新表格 |

### 2.4 知识库

| 功能 | 状态 | 说明 |
|------|------|------|
| 获取知识库目录 | ⏳ 待开发 | 列出知识库空间 |
| 读取知识库文档 | ⏳ 待开发 | 读取知识库内容 |
| 创建知识库文档 | ⏳ 待开发 | 在知识库中创建 |

## 三、API 接口

### 3.1 消息相关

```python
# 发送文本消息
async def send_text(receive_id: str, receive_id_type: str, text: str) -> str:
    """发送文本消息，返回 message_id"""

# 发送富文本消息
async def send_post(receive_id: str, receive_id_type: str, content: dict) -> str:
    """发送富文本消息"""

# 发送图片消息
async def send_image(receive_id: str, receive_id_type: str, image_key: str) -> str:
    """发送图片消息"""

# 回复消息
async def reply_message(message_id: str, content: dict) -> str:
    """回复指定消息"""

# 添加反应
async def add_reaction(message_id: str, emoji_type: str) -> bool:
    """添加消息反应"""
```

### 3.2 文档相关

```python
# 上传文件
async def upload_file(file_path: str, file_type: str = "docx") -> str:
    """上传文件到飞书云空间，返回 file_token"""

# 下载文件
async def download_file(file_token: str, save_path: str) -> bool:
    """下载飞书云空间文件到本地"""

# 创建文档
async def create_document(doc_type: str, title: str, content: str = "") -> str:
    """创建文档，返回 document_id"""

# 读取文档
async def get_document(document_id: str) -> dict:
    """读取文档内容"""

# 更新文档
async def update_document(document_id: str, blocks: list) -> bool:
    """更新文档内容"""
```

### 3.3 多维表格

```python
# 创建多维表格
async def create_bitable(token: str, name: str) -> str:
    """创建多维表格，返回 bitable_id"""

# 读取多维表格
async def get_bitable_records(bitable_id: str, table_id: str, 
                               filter: str = "", limit: int = 100) -> list:
    """读取多维表格记录"""

# 写入多维表格
async def create_bitable_record(bitable_id: str, table_id: str, 
                                 fields: dict) -> str:
    """创建多维表格记录"""

# 更新多维表格记录
async def update_bitable_record(bitable_id: str, table_id: str,
                                 record_id: str, fields: dict) -> bool:
    """更新多维表格记录"""
```

### 3.4 知识库

```python
# 获取知识库列表
async def list_spaces() -> list:
    """获取知识库空间列表"""

# 获取知识库目录
async def list_space_nodes(space_id: str, parent_node_id: str = "") -> list:
    """获取知识库目录结构"""

# 读取知识库文档
async def get_knowledge_doc(document_id: str) -> dict:
    """读取知识库文档内容"""

# 创建知识库文档
async def create_knowledge_doc(space_id: str, parent_node_id: str,
                               title: str, content: str) -> str:
    """创建知识库文档"""
```

## 四、数据结构

### 4.1 消息类型

| 类型 | 说明 | content 格式 |
|------|------|-------------|
| text | 文本消息 | `{"text": "内容"}` |
| post | 富文本消息 | `{"post": {"zh_cn": {"title": "", "content": []}}}` |
| image | 图片消息 | `{"image_key": "xxx"}` |
| file | 文件消息 | `{"file_key": "xxx"}` |
| interactive | 卡片消息 | `{"card": {}}` |

### 4.2 文档类型

| 类型 | doc_type | 说明 |
|------|----------|------|
| doc | doc | 文档 |
| sheet | sheet | 电子表格 |
| bitable | bitable | 多维表格 |
| mindnote | mindnote | 思维导图 |

### 4.3 反应类型

| 类型 | emoji_type |
|------|------------|
| 点赞 | THUMBS_UP |
| 踩 | THUMBS_DOWN |
| 鼓掌 | CLAP |
| 笑脸 | LAUGH |
| 惊讶 | WOW |
| 赞 | HEART |

## 五、配置项

| 配置项 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| enabled | bool | 是 | 是否启用 |
| app_id | str | 是 | 飞书应用 ID |
| app_secret | str | 是 | 飞书应用密钥 |
| bot_prefix | str | 是 | Bot 前缀 |
| encrypt_key | str | 否 | 加密密钥 |
| verification_token | str | 否 | 验证 Token |
| media_dir | str | 否 | 媒体文件目录 |

## 六、验收标准

### 6.1 消息功能

- [x] 支持发送/接收单聊消息
- [x] 支持群里 @消息
- [x] 支持消息引用回复
- [x] 支持添加反应

### 6.2 文档功能

- [ ] 支持上传文档到云空间
- [ ] 支持下载云空间文档
- [ ] 支持读取文档内容
- [ ] 支持创建新文档
- [ ] 支持编辑文档

### 6.3 多维表格

- [ ] 支持读取多维表格
- [ ] 支持写入多维表格
- [ ] 支持创建多维表格

### 6.4 知识库

- [ ] 支持获取知识库目录
- [ ] 支持读取知识库文档
- [ ] 支持创建知识库文档

---

*v2.0 | 最后更新：2025-02-26*
