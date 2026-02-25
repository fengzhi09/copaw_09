# Copaw 09 详细设计文档

---

## 一、项目概述

### 1.1 项目定位

Copaw 09 是一个基于多 Agent 认知架构的个人 AI 助理系统，模拟人类大脑的工作方式，通过分工协作完成复杂任务。

### 1.2 与现有 Copaw 的关系

| 项目 | 仓库 | 命令 | 说明 |
|------|------|------|------|
| Copaw | (现有) | `copaw` | 基础版本，保持不变 |
| Copaw 09 | copaw_09 | `cp9` | 多 Agent 认知架构版本 |

### 1.3 核心特点

- **多 Agent 协作**：支持 0-8 号共 9 个独立 Agent
- **认知分工**：模拟大脑不同区域的功能
- **Credit 预算**：任务消耗可控
- **本地优先**：关键模块本地运行

---

## 二、架构设计

### 2.1 大脑认知架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Copaw 09 认知架构                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ╔═════════════════════════════════════════════════════════════════╗ │
│   ║                        丘脑 (Thalamus)                          ║ │
│   ║  • 任务分类 → 分发给对应 Agent (0-8)                          ║ │
│   ║  • 难度评估 → 查历史 + 联想                                   ║ │
│   ║  • 生成/完善 agent.md / soul.md                               ║ │
│   ║  • 检索相关记忆                                                ║ │
│   ║  • 本地运行，使用 Qwen3-0.6B-FP8                              ║ │
│   ╚═════════════════════════════════════════════════════════════════╝ │
│                                    │                                   │
│                                    ▼                                   │
│   ╔═════════════════════════════════════════════════════════════════╗ │
│   ║                     前额叶 (Prefrontal Cortex)                  ║ │
│   ║                                                                  ║ │
│   ║      👈 CLI in (左手/左脑) ← 用户输入                          ║ │
│   ║           │                                                     ║ │
│   ║           ▼                                                     ║ │
│   ║    ╔═══════════════════════════════════╗                        ║ │
│   ║    ║  ✋ 握住生产工具:                ║                        ║ │
│   ║    ║     • Python / MCP Servers      ║                        ║ │
│   ║    ║     • Shell / 命令行           ║                        ║ │
│   ║    ║     • 专用控制脚本              ║                        ║ │
│   ║    ║     • API 调用                  ║                        ║ │
│   ║    ╚═══════════════════════════════════╝                        ║ │
│   ║           │                                                     ║ │
│   ║           ▼                                                     ║ │
│   ║      CLI out (右手/右脑) 👉 → 行动结果                        ║ │
│   ║                                                                  ║ │
│   ║  • 工具筛选                                                    ║ │
│   ║  • 组装上下文                                                   ║ │
│   ║  • 生成方案 + 待办列表                                         ║ │
│   ║  • 执行 + 进度更新                                            ║ │
│   ╚═════════════════════════════════════════════════════════════════╝ │
│                                                                         │
│   ═══════════════════════════════════════════════════════════════════   │
│                                                                         │
│   👁 眼睛 (see)      视觉理解      模型: Reyes-0.6B                │
│   🦻 耳朵 (listen)   语音识别      模型: Qwen3-ASR-0.6B-8bit      │
│   🗣 嘴巴 (speak)    语音合成      模型: OuteTTS-1.0-0.6B-FP8    │
│   🖨 打印机 (print)  图像生成      模型: (待定)                   │
│   📹 摄像机 (monitor) 视频理解      模型: (待定)                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 运行位置 | 职责 |
|------|----------|------|
| **丘脑** | 本地 | 任务分类、难度评估、Agent 分发 |
| **前额叶** | API/本地可配置 | 思考推理、工具筛选、方案生成 |
| **眼睛** | 本地/API | 视觉理解 |
| **耳朵** | 本地/API | 语音识别 |
| **嘴巴** | 本地/API | 语音合成 |

---

## 三、初始化流程

### 3.1 首次初始化

```bash
cp9 init
```

**用户交互**：

```
┌─────────────────────────────────────────┐
│  Copaw 09 初始化                        │
├─────────────────────────────────────────┤
│  请输入 Agent 用途 (1-9个，回车结束):   │
│                                         │
│  1. [编程助手]                          │
│  2. [科研助手]                          │
│  3. [写作助手]                          │
│  ...                                    │
│                                         │
│  选择 Agent 0 的主模型:                 │
│  > custom / minimax / zhipu / ...      │
└─────────────────────────────────────────┘
```

### 3.2 Agent 元数据生成

丘脑调用前额叶生成 agent.md 和 soul.md，用户确认后保存：

```
Agent 目录结构：
agents/
└── agent_0_编程助手/
    ├── .meta.json          # 元数据
    ├── agent.md            # 用户确认/修改
    ├── soul.md            # 用户确认/修改
    ├── skills/
    │   ├── general/       # 通用技能
    │   ├── required/      # 专业必备
    │   └── optional/      # 专业可选
    └── records/          # 月度 Excel
```

### 3.3 agent.md 模板

```markdown
# Agent 0 工作流

## 用途
编程开发、代码调试、技术调研

## 工作流
1. 接收任务
2. 理解需求
3. 制定计划
4. 执行代码
5. 测试验证
6. 反馈结果

## 规则
- 每次行动前先确认
- 复杂任务分步骤执行
- 及时汇报进度
- 代码必须符合规范

## 行动范围
- 文件操作: 读取/写入/执行
- 代码编写: Python/JS/Shell
- 命令执行: git/docker/npm
- 信息查询: 搜索/文档

## 难度标准
- 轻量: 简单问答、代码片段
- 一般: 功能开发、Bug 修复
- 中等: 系统设计、性能优化
- 复杂: 架构设计、多模块开发
- 挑战: 全新系统、核心技术突破
```

### 3.4 soul.md 模板

```markdown
# Agent 0 风格

## 偏好
- 务实直接：先干再说
- 代码优先：用代码表达
- 追求效率：不重复造轮子

## 风格
- 简洁明了：不废话
- 专业严谨：符合规范
- 适度解释：关键点说明

## 准则
- 用户至上：满足需求第一
- 质量第一：代码可维护
- 持续改进：反思优化
```

---

## 四、任务处理流程

### 4.1 完整流程图

```
用户输入任务
     │
     ▼
┌─────────────────┐
│   【丘脑】      │
│  任务分类       │
│  → 分发给       │
│  对应 Agent     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   【丘脑】      │
│  难度评估       │
│  • agent.md 标准│
│  • 历史 SQLite │
│  • 前额叶推测   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Credit 预算   │
│  计算消耗       │
│  向用户确认     │
│  (5档位)       │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 用户确认  │
    │ 或 15分钟 │
    │ 超时通过  │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│   【前额叶】    │
│  • 工具筛选    │
│  • 上下文组装  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  生成方案概述   │
│  + 待办列表     │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 用户确认  │
    │ 或 15分钟 │
    │ 超时通过  │
    └────┬────┘
         │
         ▼
┌─────────────────┐
│   逐项执行      │
│   每项完成后    │
│   询问"继续?"   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  记录到 Excel  │
│  (当月该Agent) │
└─────────────────┘
```

### 4.2 上下文组装

前额叶组装的上下文包含：

```python
context = {
    # 近10句用户输入
    "recent_messages": [...],
    
    # 当前任务进度
    "task_progress": "已完成: 需求分析 | 进行中: 代码编写",
    
    # 可用工具列表
    "available_tools": ["file_io", "shell", "browser_control", ...],
    
    # soul.md 设定
    "soul_settings": "...",
    
    # agent.md 设定
    "agent_settings": "...",
    
    # 相关记忆 (由丘脑判定)
    "related_memory": ["相关项目背景", "类似任务经验", ...]
}
```

### 4.3 空闲行为

当用户没有新任务时：

```
┌─────────────────┐
│   检查未完成    │ ──→ 继续推进或询问用户
│   任务列表      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   检查已完成的  │ ──→ 询问归档/总结经验
│   任务列表      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   总结经验     │ ──→ 写入 Excel
│   (当月记录)   │
└─────────────────┘
```

---

## 五、Credit 消耗系统

### 5.1 档位定义

| 档位 | 消耗上限 | 最大模型调用 | 适用场景 |
|------|----------|--------------|----------|
| 轻量 | < 5 | 3 | 简单问答、文件操作 |
| 一般 | < 20 | 10 | 常规开发、调试 |
| 中等 | < 50 | 30 | 复杂功能、多模块 |
| 复杂 | < 200 | 100 | 系统设计、性能优化 |
| 挑战 | < 500 | 200 | 全新架构、核心技术 |

### 5.2 难度评估算法

```python
def estimate_difficulty(task_description: str) -> int:
    # 1. 基础复杂度 (按长度)
    complexity = len(task_description) // 10
    
    # 2. 关键词加分
    complex_keywords = ["分析", "设计", "开发", "研究", "实现", "优化", "重构", "架构"]
    for kw in complex_keywords:
        if kw in task_description:
            complexity += 15
    
    # 3. 查历史相似任务
    history_complexity = query_similar_history(task_description)
    if history_complexity > 0:
        complexity = (complexity + history_complexity) // 2
    
    return min(500, max(1, complexity))
```

---

## 六、数据记录

### 6.1 Excel 记录结构

```
records/
└── 2025-02/
    ├── agent_0_编程助手.xlsx
    ├── agent_1_科研助手.xlsx
    └── ...
```

**Excel 列定义**：

| 列名 | 类型 | 说明 |
|------|------|------|
| 时间 | datetime | 任务创建时间 |
| 用户画像 | str | 用户特征标签 |
| 用途 | str | 所属 Agent |
| 上下文 | json | 任务上下文 |
| 技能列表 | json | 使用的技能 |
| 方案 | json | 执行的方案 |
| 下一步行动 | str | 要求继续/返工/补充/停止/完善 |
| Credit消耗 | int | 本次消耗点数 |

### 6.2 SQLite 历史记录

```sql
-- 任务历史
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY,
    task_id TEXT,
    agent_id INTEGER,
    description TEXT,
    complexity INTEGER,
    tier TEXT,
    credits_used INTEGER,
    successful BOOLEAN,
    keywords TEXT,
    created_at TEXT
);

-- Agent 定义
CREATE TABLE agent_definitions (
    id INTEGER PRIMARY KEY,
    name TEXT,
    purpose TEXT,
    model TEXT
);
```

---

## 七、Sensors 模块

### 7.1 Sensor 类型

| 类型 | 功能 | 模拟脑区 | 默认模型 |
|------|------|----------|----------|
| dispatch | 任务分拣 | 丘脑 | Qwen/Qwen3-0.6B-FP8 |
| think | 思考推理 | 前额叶 | (使用 LLM) |
| see | 视觉理解 | 视觉皮层 | yujunhuinlp/Reyes-0.6B |
| listen | 语音识别 | 听觉皮层 | mlx-community/Qwen3-ASR-0.6B-8bit |
| speak | 语音合成 | 布洛卡区 | OuteAI/OuteTTS-1.0-0.6B-FP8 |
| print | 图像生成 | 运动皮层 | (待定) |
| monitor | 视频理解 | 顶叶 | (待定) |

### 7.2 启动命令

```bash
# 启动 dispatch sensor (本地)
cp9 sensors start Qwen/Qwen3-0.6B-FP8 dispatch --provider local

# 启动 see sensor (API)
cp9 sensors start yujunhuinlp/Reyes-0.6B see --provider api --endpoint https://api.xxx.com
```

### 7.3 模型来源配置

```json
{
  "sensors": {
    "dispatch": {
      "model_id": "Qwen/Qwen3-0.6B-FP8",
      "provider": "local",  // local / api
      "api_endpoint": ""
    },
    "see": {
      "model_id": "yujunhuinlp/Reyes-0.6B",
      "provider": "api",
      "api_endpoint": "https://api.modelscope.cn/v1"
    }
  }
}
```

---

## 八、CLI 命令

### 8.1 命令列表

| 命令 | 说明 |
|------|------|
| `cp9 init` | 初始化 Agent (0-8号) |
| `cp9 agents` | 列出所有 Agent |
| `cp9 sensors start <model> <type>` | 启动 Sensor |
| `cp9 sensors stop <type>` | 停止 Sensor |
| `cp9 sensors list` | 列出 Sensors 状态 |
| `cp9 credit estimate <task>` | 估算 Credit 消耗 |
| `cp9 credit stats` | 查看使用统计 |

### 8.2 详细命令

```bash
# 初始化 Agent 0
cp9 init 0 --name "编程助手" --purpose "代码开发调试" --model custom

# 查看 Agents
cp9 agents

# 启动 Sensor
cp9 sensors start Qwen/Qwen3-0.6B-FP8 dispatch
cp9 sensors start Reyes-0.6B see

# 停止 Sensor
cp9 sensors stop dispatch

# 列出 Sensors
cp9 sensors list

# 估算 Credit
cp9 credit estimate "帮我写一个排序算法"

# 查看统计
cp9 credit stats --agent-id 0 --month 2
```

---

## 九、配置结构

### 9.1 config.json 完整结构

```json
{
  "channels": { ... },
  "credits": {
    "default_tier": "normal",
    "tiers": {
      "light": { "max_credits": 5, "max_model_calls": 3 },
      "normal": { "max_credits": 20, "max_model_calls": 10 },
      "medium": { "max_credits": 50, "max_model_calls": 30 },
      "complex": { "max_credits": 200, "max_model_calls": 100 },
      "challenge": { "max_credits": 500, "max_model_calls": 200 }
    }
  },
  "sensors": {
    "dispatch": { "model_id": "...", "provider": "local" },
    "see": { "model_id": "...", "provider": "api" },
    "listen": { "model_id": "...", "provider": "local" },
    "speak": { "model_id": "...", "provider": "api" }
  },
  "providers": {
    "active_llm": { "provider_id": "custom", "model": "..." },
    "custom": { "base_url": "...", "api_key": "${CUSTOM_API_KEY}" },
    "minimax": { ... },
    "zhipu": { ... },
    "openrouter": { ... },
    "nvidia": { ... },
    "openai": { ... },
    "deepseek": { ... },
    "dashscope": { ... },
    "modelscope": { ... }
  },
  "mcpServers": {
    "minimax": { "enabled": true, "command": "...", "env": {...} },
    "tavily": { ... },
    "exa": { ... }
  }
}
```

---

## 十、部署与安装

### 10.1 安装方式

```bash
# 方式1: pip install
pip install copaw-09

# 方式2: 从源码安装
cd copaw_09
pip install -e .

# 安装后生成 cp9 命令
```

### 10.2 工作目录

```
~/.copaw09/                    # 默认工作目录
├── config.json               # 配置文件
├── credit.json              # Credit 记录
├── history.db               # SQLite 历史
├── agents/
│   ├── agent_0_xxx/
│   ├── agent_1_yyy/
│   └── ...
├── memory/                  # 记忆存储
├── sensors/                 # Sensor 配置
└── logs/                   # 日志
```

---

## 十一、后续规划

### Phase 1: 基础框架
- [x] Credit 系统
- [x] 9个 Agent 目录结构
- [x] 基础 CLI 命令
- [ ] SQLite 历史记录

### Phase 2: Sensors 集成
- [ ] MCP 集成本地模型
- [ ] 各 Sensor 实现

### Phase 3: 多模型协作
- [ ] 丘脑分发给 Agent
- [ ] 前额叶工具筛选
- [ ] 上下文组装

### Phase 4: 优化扩展
- [ ] Excel 记录导出
- [ ] 经验总结
- [ ] 更多 Sensors

---

## 十二、扩展需求（新增）

### 12.1 统一配置文件

所有配置统一到一个 `config.json` 文件：

```json
{
  // ========== 基础配置 ==========
  "version": "1.0",
  "working_dir": "~/.copaw09",
  
  // ========== 服务配置 ==========
  "server": {
    "host": "0.0.0.0",
    "port": 9090,
    "workers": 4,
    "log_level": "info"
  },
  
  // ========== MCP 配置 ==========
  "mcp": {
    "minimax": {
      "enabled": true,
      "command": "uvx",
      "args": ["minimax-coding-plan-mcp", "-y"],
      "env": {
        "MINIMAX_API_KEY": "${MINIMAX_API_KEY}",
        "MINIMAX_API_HOST": ""
      }
    },
    "tavily": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "tavily-mcp@latest"],
      "env": {
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    },
    "agent-reach": {
      "enabled": true,
      "command": "python",
      "args": ["-m", "agent_reach.cli", "read"],
      "env": {}
    }
  },
  
  // ========== Providers 配置 ==========
  "providers": {
    "active": "custom",
    "custom": {
      "base_url": "https://api.minimaxi.com/v1",
      "api_key": "${MINIMAX_API_KEY}"
    },
    "minimax": { "base_url": "https://api.minimax.io/v1", "api_key": "${MINIMAX_API_KEY}" },
    "zhipu": { "base_url": "https://open.bigmodel.cn/api/paas/v4", "api_key": "${ZHIPU_API_KEY}" },
    "openrouter": { "base_url": "https://openrouter.ai/v1", "api_key": "${OPENROUTER_API_KEY}" },
    "nvidia": { "base_url": "https://integrate.api.nvidia.com/v1", "api_key": "${NVIDIA_API_KEY}" },
    "openai": { "base_url": "https://api.openai.com/v1", "api_key": "${OPENAI_API_KEY}" },
    "deepseek": { "base_url": "https://api.deepseek.com/v1", "api_key": "${DEEPSEEK_API_KEY}" },
    "dashscope": { "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1" },
    "modelscope": { "base_url": "https://api-inference.modelscope.cn/v1" }
  },
  
  // ========== Agents 配置 ==========
  "agents": {
    "0": {
      "name": "编程助手",
      "purpose": "代码开发、调试、技术调研",
      "model": "custom",
      "model_name": "MiniMax-M2.5-highspeed"
    },
    "1": {
      "name": "科研助手", 
      "purpose": "论文调研、学术写作",
      "model": "zhipu",
      "model_name": "glm-4"
    }
    // ... 0-8 号
  },
  
  // ========== Credit 配置 ==========
  "credits": {
    "default_tier": "normal",
    "tiers": {
      "light": { "max_credits": 5, "max_model_calls": 3 },
      "normal": { "max_credits": 20, "max_model_calls": 10 },
      "medium": { "max_credits": 50, "max_model_calls": 30 },
      "complex": { "max_credits": 200, "max_model_calls": 100 },
      "challenge": { "max_credits": 500, "max_model_calls": 200 }
    }
  },
  
  // ========== Sensors 配置 ==========
  "sensors": {
    "dispatch": { "model_id": "Qwen/Qwen3-0.6B-FP8", "provider": "local" },
    "see": { "model_id": "yujunhuinlp/Reyes-0.6B", "provider": "api" },
    "listen": { "model_id": "mlx-community/Qwen3-ASR-0.6B-8bit", "provider": "local" },
    "speak": { "model_id": "OuteAI/OuteTTS-1.0-0.6B-FP8", "provider": "api" }
  },
  
  // ========== Skills 仓库配置 ==========
  "skills_repos": [
    {
      "name": "clawhub",
      "url": "https://github.com/clawhub/skills",
      "enabled": true
    },
    {
      "name": "agent-reach",
      "url": "https://github.com/Panniantong/Agent-Reach",
      "enabled": true
    }
  ],
  
  // ========== 频道配置 ==========
  "channels": {
    "feishu": { "enabled": true, "app_id": "...", "app_secret": "..." },
    "console": { "enabled": true }
  }
}
```

### 12.2 服务控制脚本

```bash
#!/bin/bash
# cp9-service.sh - Copaw 09 服务控制脚本

case "$1" in
  start)
    echo "启动 Copaw 09 服务..."
    cd /opt/ai_works/copaw_09
    nohup python cp9 app --host 0.0.0.0 --port 9090 > logs/cp9.log 2>&1 &
    echo $! > logs/cp9.pid
    ;;
  stop)
    echo "停止 Copaw 09 服务..."
    if [ -f logs/cp9.pid ]; then
      kill $(cat logs/cp9.pid)
      rm logs/cp9.pid
    fi
    ;;
  restart)
    $0 stop
    sleep 2
    $0 start
    ;;
  status)
    if [ -f logs/cp9.pid ] && kill -0 $(cat logs/cp9.pid) 2>/dev/null; then
      echo "运行中 (PID: $(cat logs/cp9.pid))"
    else
      echo "已停止"
    fi
    ;;
  log)
    tail -f logs/cp9.log
    ;;
esac
```

### 12.3 Agent 名字

每个 Agent 需要一个名字，用于：
- 回复时标识身份
- 方便用户指定工作
- 日志和记录中区分

```json
"agents": {
  "0": {
    "name": "码农",
    "purpose": "编程开发",
    "model": "custom",
    "model_name": "MiniMax-M2.5-highspeed"
  },
  "1": {
    "name": "研究员",
    "purpose": "科研调研"
  }
}
```

### 12.4 预装 Skills

#### 12.4.1 内置 Skills

| Skill | 来源 | 说明 |
|-------|------|------|
| pdf | 内置 | PDF 处理 |
| xlsx | 内置 | Excel 处理 |
| docx | 内置 | Word 处理 |
| pptx | 内置 | PPT 处理 |
| news | 内置 | 新闻 |
| himalaya | 内置 | 邮件 |
| cron | 内置 | 定时任务 |
| browser | 内置 | 浏览器控制 |
| file_reader | 内置 | 文件阅读 |

#### 12.4.2 Agent-Reach Skills

预装 Agent-Reach 技能（需安装 agent-reach）：

| Skill | 功能 |
|-------|------|
| agent-reach-read | 读取网页内容 |
| agent-reach-search | 全网搜索 |
| agent-reach-twitter | Twitter 搜索 |
| agent-reach-github | GitHub 操作 |
| agent-reach-youtube | YouTube 内容 |
| agent-reach-bilibili | B站内容 |
| agent-reach-rss | RSS 订阅 |

### 12.5 Skills 仓库

#### 12.5.1 仓库定义

```json
{
  "skills_repos": [
    {
      "name": "clawhub",
      "url": "https://github.com/clawhub/skills",
      "type": "github"
    },
    {
      "name": "agent-reach", 
      "url": "https://github.com/Panniantong/Agent-Reach",
      "type": "github"
    },
    {
      "name": "custom",
      "url": "file:///opt/ai_works/copaw_09/skills",
      "type": "local"
    }
  ]
}
```

#### 12.5.2 Skills 检索

```bash
# 检索 skills
cp9 skills search "pdf"
cp9 skills search "feishu" --repo clawhub

# 添加 skill
cp9 skills add pdf --repo builtin
cp9 skills add feishu-doc --repo clawhub

# 列出可用 skills
cp9 skills list
cp9 skills list --repo all
```

### 12.6 Agent 主力模型

每个 Agent 可以指定自己的主力模型：

```json
"agents": {
  "0": {
    "name": "码农",
    "model": "custom",
    "model_name": "MiniMax-M2.5-highspeed"
  },
  "1": {
    "name": "研究员", 
    "model": "zhipu",
    "model_name": "glm-4-plus"
  },
  "2": {
    "name": "写手",
    "model": "openai", 
    "model_name": "gpt-4o"
  }
}
```

### 12.7 Credit 消耗表设计

#### 12.7.1 热表（实时查询）

```sql
CREATE TABLE credit_hot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    agent_id INTEGER NOT NULL,
    tier TEXT NOT NULL,
    budget_credits INTEGER NOT NULL,
    actual_credits INTEGER NOT NULL,
    model_calls INTEGER NOT NULL,
    status TEXT DEFAULT 'running',  -- running/completed/failed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agent_status ON credit_hot(agent_id, status);
CREATE INDEX idx_created_at ON credit_hot(created_at);
```

#### 12.7.2 冷备表（归档）

```sql
CREATE TABLE credit_cold (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT NOT NULL,
    agent_id INTEGER NOT NULL,
    tier TEXT NOT NULL,
    budget_credits INTEGER NOT NULL,
    actual_credits INTEGER NOT NULL,
    model_calls INTEGER NOT NULL,
    status TEXT,
    completed_at TIMESTAMP,
    archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,  -- 任务摘要
    tags TEXT     -- 标签
);

CREATE INDEX idx_cold_agent ON credit_cold(agent_id);
CREATE INDEX idx_cold_month ON credit_cold(archived_at);
```

#### 12.7.3 归档策略

- 任务完成后自动归档到 cold 表
- 保留最近 30 天热数据
- 每月 1 日清理超过 90 天的热数据

### 12.8 总结与遗忘机制

#### 12.8.1 定期总结

```python
class SummaryManager:
    """总结管理器"""
    
    def __init__(self, working_dir):
        self.db_path = working_dir / "summary.db"
    
    def check_idle_agents(self):
        """检查长时间不活跃的 Agent"""
        # 30 天未使用的技能
        # 60 天未使用的工具/MCP
        # 90 天未访问的任务记录
        pass
    
    def suggest_archive(self):
        """建议归档"""
        # 建议归档已完成的任务
        # 建议精简记忆
        pass
    
    def generate_reminder(self):
        """生成提醒"""
        return {
            "idle_skills": [...],
            "idle_tools": [...],
            "archive_suggestions": [...],
            "memory_cleanup": (...)
        }
```

#### 12.8.2 提醒示例

```
📌 Copaw 09 提醒

Agent 0 (码农):
  ⚠️ 技能 [docker] 已 45 天未使用
  ⚠️ MCP [tavily] 已 60 天未使用
  📋 建议归档: 12 个已完成任务记录

Agent 1 (研究员):
  📋 建议精简: memory/ 目录可清理 15MB
```

### 12.9 其他补充

#### 12.9.1 环境变量支持

配置中支持 `${ENV_VAR}` 语法：

```json
{
  "providers": {
    "custom": {
      "api_key": "${MINIMAX_API_KEY}"
    }
  }
}
```

#### 12.9.2 多语言支持

```json
{
  "language": "zh",  // zh / en
  "i18n": {
    "zh": { "agent_prefix": "【{name}】" },
    "en": "[{name}]"
  }
}
```

#### 12.9.3 日志轮转

```json
{
  "logging": {
    "level": "info",
    "rotation": {
      "max_size": "100MB",
      "max_days": 7,
      "backup_count": 10
    }
  }
}
```

#### 12.9.4 健康检查

```bash
# 健康检查
cp9 health

# 输出示例:
# {
#   "status": "healthy",
#   "agents": 3,
#   "sensors": {"dispatch": "running", "listen": "stopped"},
#   "credits_today": 45,
#   "memory": "120MB"
# }
```

#### 12.9.5 备份与恢复

```bash
# 备份
cp9 backup --output backup_20250226.tar.gz

# 恢复
cp9 restore backup_20250226.tar.gz
```

---

## 十三、待补充功能（你可能关心的）

1. **对话历史上下文** - 长期记忆与短期记忆的分层
2. **多模态输入输出** - 语音、视频、图像的完整支持
3. **Agent 间通信** - 多个 Agent 协作完成任务
4. **学习与适应** - 根据用户反馈调整行为
5. **安全与权限** - 敏感操作的二次确认
6. **API 扩展** - 供其他系统调用
7. **插件系统** - 第三方扩展支持

---

*文档版本: v0.2*
*最后更新: 2025-02-26*
*新增: 扩展需求章节（第十二、十三章）*
