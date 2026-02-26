# Gateway 模块规范

> 版本：v1.0 | 更新：2025-02-26

---

## 一、模块概述

Gateway 是系统的消息入口，负责接收各渠道的消息，进行认证、过滤后分发给合适的 Agent。

### 1.1 核心职责

| 职责 | 说明 |
|------|------|
| 消息接收 | 统一接收各渠道（飞书/钉钉/QQ/Discord/Telegram）的消息 |
| 身份认证 | 白名单用户验证、API Key 验证 |
| 事件过滤 | 过滤心跳、已读回执、敏感词等 |
| 限流控制 | 防止恶意请求 |
| 消息分发 | 根据意图识别路由到合适的 Agent |

### 1.2 数据流

```
用户消息 (Channel)
    │
    ▼
┌─────────────────────────────────────────────┐
│ Gateway                                     │
│  ├─ 身份认证 (auth.py)                     │
│  ├─ 事件过滤 (filter.py)                   │
│  └─ 消息分发 (dispatcher.py)               │
└─────────────────────────────────────────────┘
    │
    ▼
Agent (01-04) / 00 管理高手
```

---

## 二、模块结构

```
app/gateway/
├── __init__.py       # 模块导出
├── auth.py           # 身份认证
├── filter.py         # 事件过滤
├── dispatcher.py     # 消息分发
└── gateway.py        # 统一入口
```

---

## 三、API 规范

### 3.1 GatewayAuth (auth.py)

```python
class GatewayAuth:
    def __init__(
        self,
        allow_from: List[str] = None,      # 用户白名单
        api_keys: Dict[str, str] = None,   # API Key 映射
        enable_rate_limit: bool = True,    # 启用限流
        rate_limit_count: int = 60,        # 时间窗口最大请求数
        rate_limit_window: int = 60,       # 时间窗口(秒)
    )
    
    def authenticate(self, user_id: str, channel: str = "unknown") -> AuthResponse
    def authenticate_api_key(self, api_key: str) -> Optional[AuthResponse]
    def add_allow_user(self, user_id: str)
    def remove_allow_user(self, user_id: str)
```

### 3.2 GatewayFilter (filter.py)

```python
class GatewayFilter:
    def __init__(
        self,
        ignore_event_types: Set[str] = None,   # 忽略的事件类型
        ignore_user_ids: Set[str] = None,      # 忽略的用户 ID
        ignore_keywords: List[str] = None,     # 忽略的关键词
        min_content_length: int = 0,           # 最小消息长度
        max_content_length: int = 10000,       # 最大消息长度
    )
    
    def should_process(self, event: Dict[str, Any]) -> bool
    def add_ignore_user(self, user_id: str)
    def remove_ignore_user(self, user_id: str)
    def add_ignore_keyword(self, keyword: str)
```

### 3.3 MessageDispatcher (dispatcher.py)

```python
class MessageDispatcher:
    def __init__(self, router: AgentRouter = None)
    
    async def dispatch(self, event: Dict[str, Any]) -> Dict[str, Any]
    def get_agent_id(self, message: str, user_id: str = None) -> str
    async def process_message(self, message: str, user_id: str, channel: str) -> str
```

---

## 四、配置示例

### 4.1 YAML 配置

```yaml
gateway:
  auth:
    allow_from:
      - "user_001"
      - "user_002"
    api_keys:
      "sk-test-xxx": "user_001"
    enable_rate_limit: true
    rate_limit_count: 60
    rate_limit_window: 60
  
  filter:
    ignore_event_types:
      - "heartbeat"
      - "typing"
      - "read_receipt"
    ignore_user_ids: []
    ignore_keywords:
      - "测试"
      - "test"
    min_content_length: 1
    max_content_length: 5000
```

### 4.2 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `COPAW_ALLOW_USERS` | 白名单用户（逗号分隔） | - |
| `COPAW_RATE_LIMIT` | 启用限流 | true |
| `COPAW_RATE_COUNT` | 时间窗口最大请求 | 60 |
| `COPAW_RATE_WINDOW` | 时间窗口(秒) | 60 |

---

## 五、使用示例

### 5.1 初始化 Gateway

```python
from app.gateway import (
    init_gateway_auth,
    init_gateway_filter,
    get_dispatcher,
)

# 初始化认证
auth = init_gateway_auth({
    "allow_from": ["user_001", "user_002"],
    "enable_rate_limit": True,
    "rate_limit_count": 60,
})

# 初始化过滤器
filter_ = init_gateway_filter({
    "ignore_keywords": ["test"],
})

# 获取分发器
dispatcher = get_dispatcher()
```

### 5.2 处理消息

```python
# 接收消息事件
event = {
    "type": "message",
    "user_id": "user_001",
    "content": "帮我搜索最新的 AI 论文",
    "channel": "feishu"
}

# 1. 认证
auth_response = auth.authenticate(event["user_id"], event["channel"])
if auth_response.result != AuthResult.PASS:
    return {"error": auth_response.message}

# 2. 过滤
if not filter_.should_process(event):
    return {"status": "ignored"}

# 3. 分发
result = await dispatcher.dispatch(event)
```

---

## 六、错误码

| 错误码 | 说明 |
|--------|------|
| `AUTH_REJECT` | 用户不在白名单 |
| `AUTH_RATE_LIMIT` | 请求过于频繁 |
| `FILTER_IGNORED` | 事件被过滤 |
| `DISPATCH_ERROR` | 分发失败 |
| `AGENT_NOT_FOUND` | Agent 不存在 |

---

## 七、限流策略

### 7.1 滑动窗口算法

使用滑动窗口算法实现限流：

```
时间轴: |----60秒----|
请求:   ↑  ↑  ↑  ↑  ↑
        1  2  3  4  5  (最多 60 个请求)

超过限制 → 返回 429 Too Many Requests
```

### 7.2 降级处理

| 触发条件 | 处理方式 |
|----------|----------|
| 限流触发 | 返回友好提示，等待后重试 |
| 白名单拒绝 | 返回"无权限"提示 |
| 连续异常 | 拉入临时黑名单 |

---

*v1.0 | 最后更新：2025-02-26*
