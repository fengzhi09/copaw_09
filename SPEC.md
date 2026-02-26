# Copaw 开发规范 - 面向 SPEC 编程

> 版本：v1.0 | 更新：2025-02-26

---

## 一、核心原则

### 1.1 先设计，后编码

**任何功能开发前，必须先编写 SPEC 文档：**

```
需求 → SPEC → 代码 → 验证 → 文档
  ↑__________________________|
```

### 1.2 SPEC 优先

> **代码可以改，但 SPEC 不能随便改**
> 
> - 改代码不需要审批
> - 改 SPEC 需要评审
> - 代码实现必须符合 SPEC

---

## 二、SPEC 文档规范

### 2.1 SPEC 文件位置

```
app/
├── gateway/
│   ├── SPEC.md          ← 模块规格文档
│   ├── __init__.py
│   ├── auth.py
│   ├── filter.py
│   └── dispatcher.py
```

### 2.2 SPEC 模板

```markdown
# {模块名} 规格文档

> 版本：x.x | 状态：开发中 | 负责人：xxx

## 一、概述

- **功能**：一句话描述
- **输入**：什么数据
- **输出**：什么结果
- **依赖**：依赖哪些模块

## 二、接口定义

### 2.1 公开接口

| 接口 | 输入 | 输出 | 说明 |
|------|------|------|------|
| authenticate() | user_id | AuthResponse | 验证用户身份 |
| should_process() | event | bool | 判断是否处理 |

### 2.2 数据结构

```python
@dataclass
class AuthResponse:
    result: AuthResult  # PASS/REJECT/RATE_LIMIT
    message: str
    user_permission: Optional[UserPermission]
```

## 三、核心逻辑

### 3.1 认证流程

```
用户请求 → 白名单检查 → 限流检查 → 权限获取 → 返回结果
```

### 3.2 边界情况

- 白名单为空 = 允许所有
- API Key 无效 = 返回 REJECT
- 超限流 = 返回 RATE_LIMIT

## 四、验收标准

- [ ] 白名单用户能通过认证
- [ ] 非白名单用户被拒绝
- [ ] 限流正确触发
- [ ] 单元测试覆盖 > 80%

## 五、配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| allow_from | List[str] | [] | 白名单用户 |
| rate_limit_count | int | 60 | 窗口内最大请求 |
```

---

## 三、开发流程

### 3.1 标准流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 需求分析                                                  │
│    - 理解要解决什么问题                                      │
│    - 明确输入输出                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 编写 SPEC                                                │
│    - 使用模板创建 SPEC.md                                    │
│    - 定义接口和数据结构                                      │
│    - 明确验收标准                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 评审 SPEC                                                │
│    - 逻辑是否正确                                            │
│    - 边界是否考虑                                            │
│    - 是否符合架构规范                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 实现代码                                                 │
│    - 严格按 SPEC 实现                                        │
│    - 保持代码简洁                                            │
│    - 添加必要的注释                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 验证实现                                                 │
│    - 对照 SPEC 逐项检查                                      │
│    - 编写/运行测试                                          │
│    - 检查边界情况                                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 更新文档                                                 │
│    - 更新 ARCHITECTURE.md                                    │
│    - 更新 check.md                                          │
│    - 更新 ROADMAP.md                                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 快速迭代流程

对于小改动（如修复 bug、优化性能）：

```
需求 → 简化的 SPEC（几句话）→ 代码 → 验证
```

**简化 SPEC 可以：**
- 在 Git commit message 中描述
- 在代码注释中说明

**但必须包含：**
- 输入输出是什么
- 验收标准是什么

---

## 四、代码规范

### 4.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | 小写+下划线 | `gateway/auth.py` |
| 类 | 大驼峰 | `class GatewayAuth` |
| 函数 | 小写下划线 | `def authenticate()` |
| 常量 | 大写下划线 | `MAX_RETRY = 3` |
| 私有 | 前置下划线 | `_internal_method()` |

### 4.2 函数规范

**单函数 < 50 行**

```python
# ✅ 好的写法
def authenticate(user_id: str) -> AuthResponse:
    """验证用户身份"""
    # 1. 白名单检查
    if not is_whitelisted(user_id):
        return AuthResponse(REJECT, "不在白名单")
    
    # 2. 限流检查
    if is_rate_limited(user_id):
        return AuthResponse(RATE_LIMIT, "请求过频")
    
    # 3. 返回结果
    return AuthResponse(PASS, "OK")
```

**避免：**
- 嵌套超过 3 层
- 超过 5 个参数
- 重复代码

### 4.3 文件规范

**单文件 < 1000 行**

如果超过 1000 行，考虑拆分：
- 按功能拆分
- 按类拆分
- 按数据拆分

### 4.4 自注释命名

```python
# ✅ 好的命名
def calculate_monthly_cost(agent_id: str, month: str) -> float:
    """计算指定 Agent 月度成本"""
    
def is_valid_user(user_id: str) -> bool:
    """检查用户是否有效"""

# ❌ 不好的命名
def calc(a, b):  # 不知道算什么
def check(x):    # 检查什么
```

### 4.5 类型注解

**必须使用类型注解：**

```python
def authenticate(user_id: str) -> AuthResponse:
    ...

def get_user_permission(user_id: str) -> Optional[UserPermission]:
    ...
```

### 4.6 错误处理

```python
def process_event(event: dict) -> Result:
    try:
        # 业务逻辑
        return Result(success=True, data=...)
    except ValueError as e:
        logger.warning(f"参数错误: {e}")
        return Result(success=False, error="参数错误")
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return Result(success=False, error="系统错误")
```

---

## 五、数据结构规范

### 5.1 使用 dataclass

```python
from dataclasses import dataclass
from enum import Enum

class AuthResult(Enum):
    PASS = "pass"
    REJECT = "reject"
    RATE_LIMIT = "rate_limit"

@dataclass
class AuthResponse:
    result: AuthResult
    message: str
    user_permission: Optional[UserPermission] = None
```

### 5.2 枚举代替魔法数字

```python
# ✅ 好
class AgentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"

# ❌ 不好
status = 1  # 1 是什么意思？
```

---

## 六、测试规范

### 6.1 单元测试

每个公开接口必须有测试：

```python
# tests/test_gateway_auth.py
class TestGatewayAuth:
    def test_whitelist_pass(self):
        auth = GatewayAuth(allow_from=["user1", "user2"])
        result = auth.authenticate("user1")
        assert result.result == AuthResult.PASS
    
    def test_whitelist_reject(self):
        auth = GatewayAuth(allow_from=["user1"])
        result = auth.authenticate("user2")
        assert result.result == AuthResult.REJECT
```

### 6.2 覆盖率要求

| 模块 | 最低覆盖率 |
|------|-----------|
| 核心模块 (gateway/auth) | 90% |
| 业务模块 (router) | 80% |
| 工具模块 | 70% |

---

## 七、Git 提交规范

### 7.1 提交信息格式

```
<类型>: <简短描述>

<详细说明（可选）>

<关联的 SPEC 或 Issue>
```

**类型：**
- `feat`: 新功能
- `fix`: 修复
- `refactor`: 重构
- `docs`: 文档
- `spec`: SPEC 文档

**示例：**

```
feat(gateway): 添加身份认证模块

- 实现白名单验证
- 实现限流控制
- 添加单元测试

关联 SPEC: app/gateway/SPEC.md
```

### 7.2 提交前检查

- [ ] 代码符合规范
- [ ] 单元测试通过
- [ ] 无新增警告
- [ ] SPEC 已更新（如有必要）

---

## 八、文档规范

### 8.1 必须更新的文档

| 场景 | 更新文档 |
|------|----------|
| 新增模块 | ARCHITECTURE.md |
| 功能变更 | check.md |
| 计划调整 | ROADMAP.md |
| 新增规范 | SPEC.md |

### 8.2 文档审核

- SPEC 变更 → 需要评审
- 架构变更 → 需要评审
- 规范变更 → 需要评审

---

## 九、违规处理

### 9.1 轻微违规

- 命名不规范
- 注释不足
- 轻微违反规范

**处理：** 代码审查时指出，作者修改

### 9.2 严重违规

- 未写 SPEC 直接开发
- 实现与 SPEC 不一致
- 破坏性变更未通知

**处理：**
- 回滚代码
- 补充 SPEC
- 重新评审

---

## 十、附录

### 10.1 检查清单

开发前检查：

- [ ] 需求理解清楚
- [ ] SPEC 已编写
- [ ] 接口定义明确
- [ ] 验收标准清晰

开发后检查：

- [ ] 实现符合 SPEC
- [ ] 单元测试通过
- [ ] 边界情况处理
- [ ] 文档已更新

### 10.2 参考资源

- Python 类型注解：https://docs.python.org/3/library/typing.html
- dataclass 用法：https://docs.python.org/3/library/dataclasses.html
- Enum 用法：https://docs.python.org/3/library/enum.html

---

*v1.0 | 最后更新：2025-02-26*
