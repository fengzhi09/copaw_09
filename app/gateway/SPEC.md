# Gateway 模块规格文档

> 版本：v1.0 | 状态：开发中 | 负责人：卡泡

## 一、概述

- **功能**：消息入口网关，负责消息接收、分发、身份认证、事件过滤
- **输入**：来自各 Channel 的原始消息事件
- **输出**：处理后的消息，路由到对应 Agent
- **依赖**：router.py, channels/filter.py

## 二、架构

```
Channels (飞书/钉钉/QQ/Discord/电报)
           │
           ▼
    ┌──────────────┐
    │   Gateway    │
    │  ┌────────┐  │
    │  │  Auth  │  │  ← 身份认证
    │  ├────────┤  │
    │  │ Filter │  │  ← 事件过滤
    │  ├────────┤  │
    │  │Dispatch│  │  ← 消息分发
    │  └────────┘  │
    └──────────────┘
           │
           ▼
      Router (Agent 路由)
```

## 三、接口定义

### 3.1 GatewayAuth

| 接口 | 输入 | 输出 | 说明 |
|------|------|------|------|
| authenticate() | user_id, channel | AuthResponse | 验证用户身份 |
| authenticate_api_key() | api_key | AuthResponse | API Key 验证 |
| is_allowed() | user_id | bool | 检查白名单 |
| add_allow_user() | user_id | None | 添加白名单 |
| remove_allow_user() | user_id | None | 移除白名单 |

### 3.2 GatewayFilter

| 接口 | 输入 | 输出 | 说明 |
|------|------|------|------|
| should_process() | event | bool | 判断是否处理 |
| add_ignore_user() | user_id | None | 添加忽略用户 |
| add_ignore_keyword() | keyword | None | 添加关键词过滤 |

### 3.3 MessageDispatcher

| 接口 | 输入 | 输出 | 说明 |
|------|------|------|------|
| dispatch() | message, user_id | agent_id | 分发到 Agent |
| get_agent() | agent_id | AgentConfig | 获取 Agent 配置 |

## 四、数据结构

### 4.1 AuthResult 枚举

```python
class AuthResult(Enum):
    PASS = "pass"           # 通过
    REJECT = "reject"       # 拒绝
    RATE_LIMIT = "rate_limit"  # 限流
```

### 4.2 UserPermission

```python
@dataclass
class UserPermission:
    user_id: str
    allowed: bool = True
    agent_whitelist: Set[str] = field(default_factory=set)
    daily_credit_limit: float = 100.0
```

### 4.3 AuthResponse

```python
@dataclass
class AuthResponse:
    result: AuthResult
    message: str = ""
    user_permission: Optional[UserPermission] = None
```

### 4.4 GatewayFilter 配置

```python
@dataclass
class GatewayFilter:
    ignore_event_types: Set[str] = field(default_factory=lambda: {
        "heartbeat", "typing", "read_receipt", "ack"
    })
    ignore_user_ids: Set[str] = field(default_factory=set)
    ignore_keywords: List[str] = field(default_factory=list)
    min_content_length: int = 0
    max_content_length: int = 10000
```

## 五、核心逻辑

### 5.1 认证流程

```
请求到达
    │
    ▼
检查白名单 ──── 不在 ────→ 返回 REJECT
    │
    在
    ▼
检查限流 ──── 超限 ────→ 返回 RATE_LIMIT
    │
    正常
    ▼
获取权限
    │
    ▼
返回 PASS + 权限
```

### 5.2 事件过滤流程

```
事件到达
    │
    ▼
检查事件类型 ──── 忽略 ────→ 返回 False
    │
    正常
    ▼
检查用户 ──── 忽略 ────→ 返回 False
    │
    正常
    ▼
检查关键词 ──── 包含 ────→ 返回 False
    │
    正常
    ▼
检查消息长度 ── 不在范围 ──→ 返回 False
    │
    正常
    ▼
返回 True
```

### 5.3 消息分发流程

```
消息到达
    │
    ▼
调用 Router.route() ──→ 获取最佳 Agent ID
    │
    ▼
调用 Router.get_agent_config() ──→ 获取 Agent 配置
    │
    ▼
返回 (agent_id, agent_config)
```

## 六、配置项

### 6.1 GatewayAuth 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| allow_from | List[str] | [] | 白名单用户（空=允许所有） |
| api_keys | Dict[str, str] | {} | API Key 映射 |
| enable_rate_limit | bool | True | 是否启用限流 |
| rate_limit_count | int | 60 | 时间窗口内最大请求数 |
| rate_limit_window | int | 60 | 时间窗口(秒) |

### 6.2 GatewayFilter 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| ignore_event_types | Set[str] | {heartbeat,typing,read_receipt,ack} | 忽略的事件类型 |
| ignore_user_ids | Set[str] | set() | 忽略的用户 |
| ignore_keywords | List[str] | [] | 忽略的关键词 |
| min_content_length | int | 0 | 最小消息长度 |
| max_content_length | int | 10000 | 最大消息长度 |

## 七、边界情况

| 场景 | 预期行为 |
|------|----------|
| 白名单为空 | 允许所有用户 |
| 白名单用户 | 通过认证 |
| 非白名单用户 | 返回 REJECT |
| API Key 无效 | 返回 REJECT |
| 超过限流 | 返回 RATE_LIMIT |
| 空消息 | 不处理（返回 False） |
| 消息过长 | 不处理（返回 False） |
| 关键词匹配 | 不处理（返回 False） |

## 八、验收标准

- [ ] 白名单用户能通过认证
- [ ] 非白名单用户被拒绝（当白名单非空时）
- [ ] 限流正确触发
- [ ] 空消息被过滤
- [ ] 消息长度限制生效
- [ ] 关键词过滤生效
- [ ] 消息能正确路由到 Agent
- [ ] 单元测试覆盖 > 80%

## 九、文件结构

```
app/gateway/
├── SPEC.md          ← 本文档
├── __init__.py      ← 导出公开接口
├── auth.py          ← 身份认证
├── filter.py        ← 事件过滤
└── dispatcher.py    ← 消息分发（待开发）
```

## 十、依赖

- `app/router.py` - Agent 路由
- `app/channels/filter.py` - 事件过滤逻辑（复用）

---

*v1.0 | 最后更新：2025-02-26*
