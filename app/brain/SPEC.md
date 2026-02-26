# Brain 模块规格文档

> 版本：v1.0 | 状态：开发中 | 负责人：卡泡

## 一、概述

脑部模块包含丘脑和前额叶，负责 AI 思考和决策。

### 1.1 丘脑 (Thalamus)

- **功能**：意图识别、消息路由、记忆索引
- **模型**：Qwen3-0.6B-FP8
- **部署**：本地 GPU
- **作用**：路由决策 + 记忆检索 + 意图理解

### 1.2 前额叶 (Prefrontal)

- **功能**：深度思考、推理、规划
- **默认模型**：GLM-5 (智谱)
- **fallback**：MiniMax-M2.5-highspeed
- **部署**：API 调用
- **作用**：Agent 的"大脑"，负责复杂推理和决策

## 二、架构

```
Gateway
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Thalamus (丘脑)                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 意图识别    │  │ 消息路由    │  │ 记忆索引    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Prefrontal (前额叶)                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 深度推理    │  │ 规划决策    │  │ 生成回复    │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Cerebellum (小脑) - 任务执行                              │
└─────────────────────────────────────────────────────────────┘
```

## 三、接口定义

### 3.1 Thalamus

| 接口 | 输入 | 输出 | 说明 |
|------|------|------|------|
| understand_intent() | message, context | IntentResult | 理解用户意图 |
| route_message() | message, intent | AgentID | 路由到 Agent |
| retrieve_memory() | query, user_id | List[Memory] | 检索记忆 |

### 3.2 Prefrontal

| 接口 | 输入 | 输出 | 说明 |
|------|------|------|------|
| think() | prompt, context | Response | 深度思考 |
| reason() | problem, context | ReasoningResult | 推理分析 |
| plan() | goal, context | PlanResult | 规划决策 |
| generate() | prompt, context | GeneratedText | 生成内容 |

## 四、数据结构

### 4.1 IntentResult

```python
@dataclass
class IntentResult:
    intent: str              # 意图类型
    confidence: float        # 置信度 0-1
    entities: Dict[str, Any] # 实体
    next_action: str         # 下一步动作
```

### 4.2 ReasoningResult

```python
@dataclass
class ReasoningResult:
    reasoning: str          # 推理过程
    conclusion: str          # 结论
    confidence: float        # 置信度
    evidence: List[str]      # 证据
```

### 4.3 PlanResult

```python
@dataclass
class PlanResult:
    steps: List[PlanStep]   # 步骤列表
    estimated_time: int      # 预计时间(秒)
    resources: List[str]     # 所需资源
```

### 4.4 PlanStep

```python
@dataclass
class PlanStep:
    step_id: int
    description: str
    agent_id: str
    dependencies: List[int]
```

## 五、核心逻辑

### 5.1 意图识别流程

```
用户消息
    │
    ▼
分词/ embedding
    │
    ▼
调用 Qwen3-0.6B
    │
    ▼
解析意图 + 实体提取
    │
    ▼
返回 IntentResult
```

### 5.2 路由决策流程

```
IntentResult
    │
    ▼
检查关键词映射
    │
    ▼
检查 Agent 可用性
    │
    ▼
返回最佳 Agent ID
```

### 5.3 深度思考流程

```
任务 + 上下文
    │
    ▼
构建 prompt (few-shot)
    │
    ▼
调用 GLM-5 API
    │
    ▼
解析响应
    │
    ▼
返回结果
```

## 六、配置项

### 6.1 Thalamus 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| model_path | str | - | Qwen3 模型路径 |
| device | str | cuda | 设备 (cuda/cpu) |
| max_length | int | 2048 | 最大生成长度 |
| temperature | float | 0.7 | 温度参数 |

### 6.2 Prefrontal 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| primary_model | str | glm-5 | 主模型 |
| fallback_model | str | MiniMax-M2.5 | 备用模型 |
| api_key | str | - | API Key |
| api_base | str | - | API 地址 |
| max_tokens | int | 4096 | 最大 token 数 |
| temperature | float | 0.7 | 温度参数 |

## 七、模型支持

### 7.1 本地模型 (Thalamus)

| 模型 | 大小 | 精度 | 最低显存 |
|------|------|------|----------|
| Qwen3-0.6B | 0.6B | FP8 | 1GB |
| Qwen3-1.8B | 1.8B | FP8 | 2GB |

### 7.2 API 模型 (Prefrontal)

| 模型 | 提供商 | 输入价格 | 输出价格 |
|------|--------|----------|----------|
| GLM-5 | 智谱 | ¥1/1K | ¥1/1K |
| MiniMax-M2.5 | MiniMax | ¥0.5/1K | ¥1.5/1K |

## 八、验收标准

- [ ] Thalamus 能识别用户意图
- [ ] Thalamus 能路由到正确 Agent
- [ ] Thalamus 能检索记忆
- [ ] Prefrontal 能进行深度推理
- [ ] Prefrontal 能生成合理回复
- [ ] 支持模型降级
- [ ] 单元测试覆盖 > 80%

## 九、文件结构

```
app/brain/
├── SPEC.md              ← 本文档
├── __init__.py
├── thalamus.py          ← 丘脑模块
├── prefrontal.py         ← 前额叶模块
└── models/              ← 模型管理
    ├── __init__.py
    └── registry.py       ← 模型注册表
```

---

*v1.0 | 最后更新：2025-02-26*
