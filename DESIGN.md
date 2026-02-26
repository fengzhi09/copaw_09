# Copaw 设计文档

> 版本：v1.0  
> 日期：2025-02-25  
> 作者：卡泡（科研编程助理）

---

## 目录

- [一、项目概述](#一项目概述)
- [二、系统架构](#二系统架构)
- [三、Agent 详细定义](#三agent-详细定义)
- [四、Channels（消息渠道）](#四channels消息渠道)
- [五、模型配置](#五模型配置)
- [六、资源配额](#六资源配额)
- [七、Agent 目录结构](#七agent-目录结构)
- [八、命令规范](#八命令规范)
- [九、MCP 工具](#九mcp-工具)
- [十、Agent 创建流程（00 号核心能力）](#十agent-创建流程00-号核心能力)
- [十一、记忆系统](#十一记忆系统)
- [十二、资源配额系统](#十二资源配额系统)
- [十三、Agent 间协作](#十三agent-间协作)
  - [13.1 协作模式](#131-协作模式)
  - [13.2 全链路追踪 ID](#132-全链路追踪-id)
  - [13.3 协作协议](#133-协作协议)
  - [13.4 04 号每日复盘](#134-04-号每日复盘)
  - [13.5 晚餐交流会（每 3 天）](#135-晚餐交流会每-3-天)
- [十四、消息协议](#十四消息协议)
- [十五、安全与权限](#十五安全与权限)
- [十六、日志与监控](#十六日志与监控)
- [十七、部署方案](#十七部署方案)
- [十八、数据库（PostgreSQL）](#十八数据库postgresql)
  - [18.1 概述](#181-概述)
  - [18.2 Docker 部署](#182-docker-部署)
  - [18.3 表结构设计](#183-表结构设计)
  - [18.4 连接配置](#184-连接配置)
  - [18.5 数据库管理命令](#185-数据库管理命令)
- [十九、配置文件](#十九配置文件)
- [二十、技能配置详情](#二十技能配置详情)
- [二十一、定时任务](#二十一定时任务)
- [二十二、待实现功能](#二十二待实现功能)
- [二十三、版本历史](#二十三版本历史)
- [二十四、附录](#二十四附录)

---

## 一、项目概述

Copaw 是一个多 Agent 协作系统，通过「前额叶-丘脑-小脑」架构实现智能协作。每个 Agent 拥有独立记忆、独立 Credit、独立模型配额，可通过多种渠道（飞书、钉钉、QQ、Discord、电报）与用户交互。

---

## 二、系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                          用户 (User)                                │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Channels (5 个渠道)                              │
│         飞书 | 钉钉 | QQ | Discord | 电报                           │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        入口 Gateway                                  │
│                    消息分发 + 身份认证                               │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        丘脑 (Thalamus)                              │
│              本地运行 Qwen3-0.6B-FP8                                │
│              意图识别 + 路由 + 记忆检索                              │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
┌─────────────────────────┐   ┌─────────────────────────────────────┐
│    00 管理高手          │   │        专业职能 (01-04)            │
│  • 创建新 Agent         │   │  01 学霸   │ 02 编程高手           │
│  • 初始化流程           │   │  03 创意青年│ 04 统计学长           │
│  • 汇报状态             │   │           (05-08 预留)             │
└─────────────────────────┘   └─────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 功能 | 模型/技术 |
|------|------|-----------|
| **前额叶 (Prefrontal)** | 深度思考、推理、规划 | GLM-5 (智谱) |
| **丘脑 (Thalamus)** | 意图识别、消息路由、记忆索引 | Qwen3-0.6B-FP8 (本地) |
| **小脑 (Cerebellum)** | 任务执行、工具调用、流程控制 | Python + MCP |
| **感官 (Sensors)** | 看、听、说、触 | 视/听/说模型 |

### 2.3 Agent 编号规则

- **00 号**：管理高手（系统级）
- **01-04 号**：专业职能（业务级）
- **05-08 号**：预留

---

## 三、Agent 详细定义

### 3.1 00 号 - 管理高手

| 属性 | 值 |
|------|-----|
| **角色** | 管家、指挥官 |
| **沟通风格** | 主动汇报、统筹协调、确认后执行 |
| **核心能力** | 1. 根据需求创建新 Agent<br>2. 执行 Agent 初始化流程<br>3. 汇报各 Agent 状态和问题<br>4. 反问确认需求细节<br>5. 协调多 Agent 协作 |

**工作流程**：

```
用户需求 → 分析需求 → [补充问题] → 用户确认 → 创建/分配 Agent → 初始化 → 执行 → 汇报结果
```

### 3.2 01 号 - 学霸

| 属性 | 值 |
|------|-----|
| **角色** | 学术调研专家 |
| **沟通风格** | 理性严谨、证据充分、引用规范 |
| **核心能力** | 学术论文检索、文献综述、事实核查 |

**数据源**：

| 类别 | 来源 |
|------|------|
| 学术搜索 | 谷歌学术、百度学术、PubMed、SciHub、ArXiv、PubScholar、ProQuest Summon、中国科学院文献情报中心、国家图书馆 |
| 代码/模型 | GitHub、ModelScope |
| 社区 | 知乎、爱去 |
| 视频 | B 站、油管 |
| 社交媒体 | X (Twitter) 追踪科技新闻 |

### 3.3 02 号 - 编程高手

| 属性 | 值 |
|------|-----|
| **角色** | 软件开发专家 |
| **沟通风格** | 逻辑缜密、结构化、代码规范 |
| **核心能力** | 代码开发、调试、架构设计、技术调研 |

**工作习惯**：

- 启动自动检查相关工具链
- 习惯在 GitHub 和 CSDN、知乎、B 站中畅游
- 善用 OpenCode 进行代码协作

**数据源**：GitHub、CSDN、知乎、B 站、OpenCode

### 3.4 03 号 - 创意青年

| 属性 | 值 |
|------|-----|
| **角色** | 创意内容专家 |
| **沟通风格** | 发散思维、积极执行、网感强 |
| **核心能力** | 文字创作、绘画提示词、视频脚本、创意生成 |

**工作习惯**：

- 擅长文字创作、画画、拍摄
- 创意多有想法
- 讨论积极但执行不发散
- 没事习惯在小红书学习相关技巧

**数据源**：小红书、抖音、B 站

### 3.5 04 号 - 统计学长 / 收藏家

| 属性 | 值 |
|------|-----|
| **角色** | 知识管理专家 |
| **沟通风格** | 善于倾听、善于启发、温暖耐心 |
| **核心能力** | 每日复盘、总结归纳、知识收藏、经验萃取 |

**工作习惯**：

- 其他 Agent 每天都会跟它聊聊今天的工作
- 从别人那里接手有价值但经常被忽略的东西
- 喜欢在喜马拉雅和得物中学习

**数据源**：喜马拉雅、得物、知乎

---

## 四、Channels（消息渠道）

### 4.1 支持的渠道

| 编号 | 渠道 | 协议 | 参考实现 |
|------|------|------|----------|
| 1 | 飞书 | WebSocket | nanobot |
| 2 | 钉钉 | WebHook | - |
| 3 | QQ | OneBot 协议 | - |
| 4 | Discord | Bot API | nanobot |
| 5 | 电报 | Bot API | - |

### 4.2 配置结构

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxx",
      "appSecret": "xxx",
      "encryptKey": "",
      "verificationToken": "",
      "allowFrom": [],
      "filters": {
        "ignore_events": ["pin_added", "pin_removed", "reaction_added"],
        "ignore_users": ["bot_xxx"],
        "ignore_keywords": ["[表情]"]
      }
    },
    "dingtalk": {
      "enabled": false,
      "webhook": "",
      "secret": "",
      "filters": {
        "ignore_events": ["oa_notification"],
        "ignore_keywords": ["收到"]
      }
    },
    "qq": {
      "enabled": false,
      "onebotUrl": "",
      "token": "",
      "filters": {
        "ignore_events": ["notice"]
      }
    },
    "discord": {
      "enabled": false,
      "botToken": "",
      "guildId": "",
      "channelIds": [],
      "filters": {
        "ignore_events": ["MESSAGE_REACTION_ADD", "THREAD_CREATED"]
      }
    },
    "telegram": {
      "enabled": false,
      "botToken": "",
      "allowedUsers": [],
      "filters": {
        "ignore_events": ["edited_message", "callback_query"]
      }
    }
  }
}
```

### 4.3 事件过滤机制

> Channel 收到消息后，根据过滤配置忽略指定类型事件，避免报错

```python
class ChannelFilter:
    """Channel 消息过滤器"""
    
    def __init__(self, filters: dict):
        self.ignore_events = filters.get("ignore_events", [])
        self.ignore_users = filters.get("ignore_users", [])
        self.ignore_keywords = filters.get("ignore_keywords", [])
    
    def should_process(self, event: dict) -> bool:
        """
        判断事件是否需要处理
        返回 True = 处理事件
        返回 False = 忽略事件
        """
        # 1. 检查事件类型
        event_type = event.get("type", "")
        if event_type in self.ignore_events:
            logger.info(f"忽略事件类型: {event_type}")
            return False
        
        # 2. 检查用户
        user_id = event.get("user_id", "")
        if user_id in self.ignore_users:
            logger.info(f"忽略用户: {user_id}")
            return False
        
        # 3. 检查关键词
        content = event.get("content", "")
        for keyword in self.ignore_keywords:
            if keyword in content:
                logger.info(f"忽略关键词: {keyword}")
                return False
        
        return True

def handle_channel_event(channel: str, event: dict):
    """Channel 事件处理入口"""
    config = load_channel_config(channel)
    filters = ChannelFilter(config.get("filters", {}))
    
    if not filters.should_process(event):
        return  # 静默忽略，不报错
    
    # 正常处理事件
    process_event(channel, event)
```

### 4.4 过滤规则说明

| 规则 | 说明 | 示例 |
|------|------|------|
| `ignore_events` | 忽略指定类型的事件 | `pin_added`, `reaction_added` |
| `ignore_users` | 忽略指定用户的消息 | 机器人、某些用户 |
| `ignore_keywords` | 忽略包含关键词的消息 | `[表情]`, `收到` |

### 4.5 常见事件过滤示例

**飞书**：

```json
{
  "feishu": {
    "filters": {
      "ignore_events": [
        "pin_added",        // 收藏消息
        "pin_removed",     // 取消收藏
        "reaction_added",  // 添加表情
        "reaction_removed" // 移除表情
      ]
    }
  }
}
```

**钉钉**：

```json
{
  "dingtalk": {
    "filters": {
      "ignore_events": [
        "oa_notification",  // OA 通知
        "link_clicked"     // 链接点击
      ]
    }
  }
}
```

**Discord**：

```json
{
  "discord": {
    "filters": {
      "ignore_events": [
        "MESSAGE_REACTION_ADD",
        "THREAD_CREATED",
        "GUILD_MEMBER_JOIN"
      ]
    }
  }
}
```

---

## 五、模型配置

### 5.1 前额叶（Prefrontal）

> 每个 Agent 独立配置

```json
{
  "agents": {
    "00": {
      "prefrontal": {
        "provider": "zhipu",
        "model": "glm-5",
        "fallback": "custom/MiniMax-M2.5-highspeed"
      }
    },
    "01": { "prefrontal": { "provider": "zhipu", "model": "glm-5" } },
    "02": { "prefrontal": { "provider": "zhipu", "model": "glm-5" } },
    "03": { "prefrontal": { "provider": "zhipu", "model": "glm-5" } },
    "04": { "prefrontal": { "provider": "zhipu", "model": "glm-5" } }
  }
}
```

### 5.2 感官（Sensors）

| 感官 | 模型 | 用途 |
|------|------|------|
| **print** (说/画) | nano-banana-pro | 文生图 |
| **recorder** (录) | - | 文生视频（暂不调用） |
| **dispatch** | Qwen/Qwen3-0.6B | 意图分发 |

### 5.3 丘脑（本地）

```json
{
  "thalamus": {
    "model": "Qwen/Qwen3-0.6B-FP8",
    "device": "cuda",
    "quantization": "fp8"
  }
}
```

---

## 六、资源配额

### 6.1 Credit 档位

> 每个 Agent 独立 Credit 池

| 档位 | Credit 额度 | 适用场景 |
|------|-------------|----------|
| 轻量 | < 5 | 简单问答 |
| 一般 | < 20 | 日常任务 |
| 中等 | < 50 | 复杂任务 |
| 挑战 | < 200 | 大型项目 |
| 深度 | < 500 | 科研/课题 |

### 6.2 模型配额

> 每个 Agent 独立模型调用配额

```json
{
  "agents": {
    "00": {
      "quota": {
        "glm-5": { "daily": 100, "monthly": 3000 },
        "nano-banana-pro": { "daily": 10, "monthly": 300 }
      }
    }
  }
}
```

---

## 七、Agent 目录结构

```
copaw/
├── agents/
│   ├── agent_00_管理高手/
│   │   ├── .meta.json          # 元数据
│   │   ├── agent.md            # 工作流配置
│   │   ├── soul.md            # 风格配置
│   │   ├── memory/            # 独立记忆
│   │   │   ├── short_term/    # 短期记忆
│   │   │   └── long_term/     # 长期记忆
│   │   ├── skills/            # 技能配置
│   │   │   ├── general/       # 通用技能
│   │   │   ├── required/      # 专业必备
│   │   │   └── optional/      # 专业可选
│   │   └── records/           # 执行记录
│   ├── agent_01_学霸/
│   ├── agent_02_编程高手/
│   ├── agent_03_创意青年/
│   ├── agent_04_统计学长/
│   └── agent_XX_自定义/       # 用户创建的 Agent
├── skills/                    # 全局技能
├── memory/                    # 全局记忆
├── channels/                  # 渠道适配器
├── models/                    # 模型配置
└── copaw.py                   # 主入口
```

---

## 八、命令规范

### 8.1 主命令

```bash
cp9                    # 启动 Copaw 系统
cp9 status             # 查看系统状态
cp9 list               # 列出所有 Agent
cp9 create <需求>      # 创建新 Agent（自然语言）
cp9 credit             # 查看 Credit 余额

# 定时任务（使用 cron skill）
cp9 cron add "0 18 * * *" daily_report      # 每日 18:00 日报
cp9 cron add "0 21 * * */3" dinner_meeting # 每 3 天 21:00 晚餐会
cp9 cron list         # 列出定时任务
cp9 cron remove <id>  # 删除定时任务
```

### 8.2 Agent 管理

```bash
cp9 agent 00 status    # 查看 00 号状态
cp9 agent 01 memory    # 查看 01 号记忆
cp9 agent 02 quota     # 查看 02 号配额
cp9 agent 00 trace     # 查看 00 号追踪日志
```

---

## 九、MCP 工具

### 9.1 内置工具

| 工具 | 说明 |
|------|------|
| tavily_search | 网页搜索 |
| tavily_crawl | 网页抓取 |
| tavily_extract | 内容提取 |
| agent-reach | 社交媒体检索 |
| file_reader | 文件读取 |
| xlsx | Excel 处理 |
| docx | Word 处理 |
| pdf | PDF 处理 |
| pptx | PPT 处理 |
| browser | 浏览器控制 |

### 9.2 MCP 配置

```json
{
  "mcp": {
    "tavily": { "enabled": true },
    "agent-reach": { "enabled": true },
    "browser-use": { "enabled": true }
  }
}
```

---

## 十、Agent 创建流程（00 号核心能力）

### 10.1 创建流程图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        用户输入需求                                   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     00 号分析需求                                      │
│    • 理解需求意图                                                    │
│    • 识别需要哪种类型的 Agent                                        │
│    • 检查现有 Agent 是否满足                                         │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────┐
              │      是否需要补充信息？            │
              └──────────────────────────────────┘
                    │                    │
                   是                    否
                    │                    │
                    ▼                    ▼
┌────────────────────────┐    ┌─────────────────────────────────────┐
│    00 号反问确认       │    │      00 号生成 Agent 规格           │
│ • 需求细节确认         │    │  • 角色定义                          │
│ • 预期成果确认         │    │  • 技能配置                          │
│ • 时间节点确认         │    │  • 资源配额                          │
└────────────────────────┘    └─────────────────────────────────────┘
        │                                   │
        │      用户确认                      │
        │◄──────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     执行初始化                                        │
│  1. 创建目录结构                                                    │
│  2. 生成 .meta.json                                                 │
│  3. 生成 agent.md / soul.md                                        │
│  4. 初始化 memory/                                                  │
│  5. 挂载 skills/                                                   │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     返回结果                                          │
│  • 新 Agent 编号和角色                                               │
│  • 初始化状态                                                        │
│  • 下一步操作建议                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.2 规格生成模板

```json
{
  "name": "新Agent名称",
  "role": "角色定位",
  "style": "沟通风格",
  "skills": ["required/xxx", "optional/yyy"],
  "quota": "中等",
  "channels": ["feishu", "dingtalk"],
  "permissions": ["file_write", "browser_use"]
}
```

### 10.3 用户确认示例

```
📋 需求理解确认

我理解您需要：创建一个帮助撰写 SCI 论文的学术助手

请确认以下信息：
1. ✅ 专业方向：生物医学/机器学习交叉领域
2. ✅ 语言：英文为主，中文学术规范也可
3. ✅ 重点：文献综述 / 实验方法 / 统计分析（多选）
4. ⏳ 是否需要协助投稿？

请回复确认或补充 👆
```

---

## 十一、记忆系统

### 11.1 记忆分层

| 层级 | 存储位置 | 内容 | 生命周期 |
|------|----------|------|----------|
| **即时记忆** | 内存 | 当前对话上下文 | 会话结束 |
| **短期记忆** | agents/XX/memory/short_term/ | 本次任务相关 | 任务完成 |
| **长期记忆** | agents/XX/memory/long_term/ | 经验总结、知识沉淀 | 持久化 |

### 11.2 记忆检索

```
用户消息
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     丘脑记忆检索                                     │
│  1. 提取关键词                                                      │
│  2. 搜索即时记忆 → 匹配度高? → 返回结果                            │
│  3. 搜索短期记忆 → 匹配度高? → 返回结果                            │
│  4. 搜索长期记忆 → 匹配度高? → 返回结果                            │
└─────────────────────────────────────────────────────────────────────┘
```

### 11.3 记忆格式

**短期记忆（JSON）**：

```json
{
  "session_id": "2025-02-25-001",
  "started_at": "2025-02-25T10:30:00Z",
  "task": "调研 Transformer 架构在医学影像的应用",
  "key_findings": [
    "ViT 在 CT 图像分类准确率达 95%",
    "MedViT 是最新 SOTA 模型"
  ],
  "sources": [
    {"type": "pubmed", "id": "PMID:123456"},
    {"type": "arxiv", "id": "arXiv:2301.12345"}
  ],
  "status": "completed"
}
```

**长期记忆（Markdown）**：

```markdown
# 2025-02 学术调研经验

## 常用数据库
- PubMed: 医学文献
- arXiv: 前沿预印本
- GitHub: 代码实现

## 检索技巧
1. 组合关键词用 AND/OR
2. 关注高引用论文（>100）
3. 追踪领域大牛的最新工作
```

---

## 十二、资源配额系统

### 12.1 Credit 计算

| 操作 | Credit 消耗 |
|------|-------------|
| 发送消息（用户） | 0 |
| 前额叶推理（GLM-5） | 1 Credit / 1K tokens |
| 短期搜索 | 0.5 Credit |
| 深度搜索 | 2 Credit |
| 文生图（nano-banana） | 5 Credit |
| 文件读取 | 0.1 Credit / MB |

### 12.2 配额检查

```python
def check_quota(agent_id: str, operation: str, tokens: int = 0) -> bool:
    """检查并扣减配额"""
    agent = load_agent(agent_id)
    
    # 检查日限额
    daily_used = get_daily_usage(agent_id, operation)
    daily_limit = agent.quota[operation]['daily']
    
    if daily_used >= daily_limit:
        # 尝试月限额
        monthly_used = get_monthly_usage(agent_id, operation)
        monthly_limit = agent.quota[operation]['monthly']
        
        if monthly_used >= monthly_limit:
            return False  # 配额耗尽
    
    # 扣减配额
    deduct_credit(agent_id, operation, tokens)
    return True
```

### 12.3 告警机制

| 阈值 | 动作 |
|------|------|
| < 20% 日限额 | 提醒 Agent 节约使用 |
| < 10% 日限额 | 提醒用户充值 |
| 耗尽 | 暂停该 Agent 服务 |

---

## 十三、Agent 间协作

### 13.1 协作模式

| 模式 | 说明 | 示例 |
|------|------|------|
| **串联** | A → B → C 依次执行 | 01 调研 → 02 实现 → 03 包装 |
| **并联** | A 和 B 同时执行 | 01 调研 + 02 编程 同时进行 |
| **汇聚** | A 和 B 结果汇总给 C | 01+02 → 04 总结 |

### 13.2 全链路追踪 ID

> 多 Agent 协作任务需要统一追踪

```json
{
  "trace_id": "trace-20250225-a1b2c3d4",
  "parent_id": null,
  "span_id": "span-001",
  "task_type": "chain",
  "agents": ["01", "02", "03"],
  "start_time": "2025-02-25T18:00:00Z",
  "status": "running"
}
```

**ID 格式**：`trace-{日期}-{8位随机字符}`

**追踪结构**：

```
trace-20250225-a1b2c3d4
├── span-001 (00 分配任务)
├── span-002 (01 执行调研)
├── span-003 (02 实现代码) 
│   └── span-003-1 (02 调用搜索工具)
│   └── span-003-2 (02 生成代码)
├── span-004 (03 创意包装)
└── span-005 (00 汇总结果)
```

**日志记录**：

```python
def log_trace(trace_id: str, span_id: str, agent_id: str, action: str):
    """记录追踪日志"""
    logger.info({
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_id": get_parent_id(span_id),
        "agent_id": agent_id,
        "action": action,
        "timestamp": datetime.utcnow().isoformat()
    })
```

### 13.3 协作协议

```json
{
  "task_id": "task-2025-02-25-001",
  "trace_id": "trace-20250225-a1b2c3d4",
  "type": "chain",
  "steps": [
    {
      "agent": "01",
      "action": "research",
      "span_id": "span-002",
      "input": "Transformer 在医学影像的最新进展",
      "output": "survey_report.md"
    },
    {
      "agent": "02", 
      "action": "implement",
      "span_id": "span-003",
      "input": "基于 survey_report.md 实现代码",
      "output": "code_repository"
    },
    {
      "agent": "03",
      "action": "creative",
      "span_id": "span-004",
      "input": "将代码成果制作成展示材料",
      "output": "presentation.pptx"
    }
  ]
}
```

### 13.4 04 号每日复盘

```
定时任务：每天 18:00

┌─────────────────────────────────────────────────────────────────────┐
│                    04 号触发每日复盘                                 │
│  1. 向 01-03 号发送复盘邀请                                         │
│  2. 收集当日工作摘要                                                │
│  3. 提取有价值的知识点                                             │
│  4. 存入长期记忆                                                    │
│  5. 生成今日简报发送给用户                                          │
└─────────────────────────────────────────────────────────────────────┘
```

### 13.5 晚餐交流会（每 3 天）

> 每 3 天晚上 9-10 点，Agent 群聊交流

```yaml
dinner_meeting:
  schedule: "0 21 * * */3"  # 每 3 天晚上 9 点
  duration: 1h
  participants: ["00", "01", "02", "03", "04"]
  topics:
    - 工作进展分享
    - 遇到的问题讨论
    - 经验互相学习
    - 灵感火花碰撞
```

**交流会流程**：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    晚餐交流会开始                                    │
│  20:55  04 号发出邀请                                               │
│  21:00  00 号主持开场                                               │
│  21:05  01 号分享学术发现                                           │
│  21:15  02 号分享代码技巧                                           │
│  21:25  03 号分享创意灵感                                           │
│  21:35  04 号总结归纳                                               │
│  21:50  自由讨论                                                     │
│  22:00  00 号总结结束                                               │
└─────────────────────────────────────────────────────────────────────┘
```

**记录保存**：

```
agents/04_统计学长/memory/long_term/
├── dinner_2025-02-23.md   # 晚餐交流记录
├── dinner_2025-02-20.md
└── dinner_2025-02-17.md
```

---

## 十四、消息协议

### 14.1 统一消息格式

```json
{
  "msg_id": "msg-2025-02-25-001",
  "channel": "feishu",
  "from": {
    "type": "user",
    "id": "user-123",
    "name": "刘海龙"
  },
  "to": {
    "type": "agent",
    "id": "00"
  },
  "content": {
    "type": "text",
    "body": "帮我创建一个学术调研助手"
  },
  "timestamp": "2025-02-25T10:30:00Z",
  "meta": {
    "trace_id": "trace-001",
    "reply_to": null
  }
}
```

### 14.2 响应格式

```json
{
  "msg_id": "msg-2025-02-25-002",
  "to": {
    "type": "user",
    "id": "user-123"
  },
  "content": {
    "type": "text",
    "body": "📋 需求理解确认\n\n我理解您需要...",
    "actions": [
      {"type": "button", "label": "确认", "value": "confirm"},
      {"type": "button", "label": "补充", "value": "modify"}
    ]
  },
  "from": {
    "type": "agent",
    "id": "00"
  }
}
```

---

## 十五、安全与权限

### 15.1 认证机制

| 层级 | 机制 |
|------|------|
| **Channel 层** | API Key / Webhook 签名 / Bot Token |
| **Gateway 层** | 用户白名单（allowFrom） |
| **Agent 层** | 敏感操作需用户确认 |

### 15.2 权限控制

```json
{
  "permissions": {
    "file_read": ["*"],           // 读取所有文件
    "file_write": ["workspace/"], // 仅工作区
    "browser_use": true,          // 允许浏览器
    "network": true,              // 允许网络访问
    "execute_shell": false,      // 禁止执行命令
    "create_agent": true,         // 允许创建 Agent
    "view_credit": true          // 允许查看配额
  }
}
```

### 15.3 敏感操作确认

```
⚠️ 敏感操作确认

Agent 02 正在执行以下操作：
• 写入文件：/opt/ai_works/copaw/agents/xxx/workspace/main.py
• 执行命令：pip install xxx

是否确认执行？ [确认] [取消]
```

---

## 十六、日志与监控

### 16.1 日志结构

```json
{
  "level": "INFO",
  "timestamp": "2025-02-25T10:30:00Z",
  "agent_id": "02",
  "action": "research",
  "duration_ms": 2500,
  "tokens": 1200,
  "credit_used": 1.2,
  "sources": ["github", "arxiv"],
  "result": "success",
  "error": null
}
```

### 16.2 监控指标

| 指标 | 说明 |
|------|------|
| **响应延迟** | P50/P95/P99 |
| **Credit 消耗** | 按 Agent/按天/按月 |
| **错误率** | 按 Agent/按操作 |
| **活跃度** | 消息数/会话数 |

---

## 十七、部署方案

### 17.1 环境要求

| 组件 | 要求 |
|------|------|
| **Python** | 3.10+ |
| **CUDA** | 12.0+ |
| **内存** | 16GB+ |
| **显存** | 8GB+（丘脑模型） |
| **磁盘** | 50GB+ |

### 17.2 环境变量

```bash
# 模型配置
ZHIPU_API_KEY=xxx
MINIMAX_API_KEY=xxx
NANO_BANANA_API_KEY=xxx

# Channel 配置
FEISHU_APP_ID=xxx
FEISHU_APP_SECRET=xxx
DISCORD_BOT_TOKEN=xxx
TELEGRAM_BOT_TOKEN=xxx

# 系统配置
LOG_LEVEL=INFO
DATA_DIR=/opt/ai_works/copaw
```

### 17.3 启动方式

```bash
# 开发模式
cp9 dev

# 生产模式
cp9 start --daemon

# 查看状态
cp9 status
```

---

## 十八、数据库（PostgreSQL）

### 18.1 概述

> 采用 PostgreSQL 统一存储，通过 Docker 运行

| 数据类型 | 说明 |
|----------|------|
| **记忆数据** | 短期记忆、长期记忆、向量索引 |
| **执行日志** | 追踪日志、操作记录 |
| **配置数据** | Agent 配置、Channel 配置 |
| **统计数据** | Credit 消耗、成本记录、监控指标 |
| **用户数据** | 用户画像、对话历史 |

### 18.2 Docker 部署

```bash
# 启动 PostgreSQL 容器
docker run -d \
  --name copaw-db \
  -e POSTGRES_DB=copaw \
  -e POSTGRES_USER=copaw \
  -e POSTGRES_PASSWORD=your_secure_password \
  -p 5432:5432 \
  -v /opt/ai_works/copaw/data:/var/lib/postgresql/data \
  postgres:16-alpine
```

**参数说明**：

| 参数 | 说明 | 示例 |
|------|------|------|
| `-p` | 宿主机端口 | `5432:5432` |
| `-e POSTGRES_PASSWORD` | 数据库密码 | （需修改） |
| `-v` | 数据持久化目录 | `/opt/ai_works/copaw/data` |

**推荐配置**：

```bash
# 带密码和健康检查的完整配置
docker run -d \
  --name copaw-db \
  --restart unless-stopped \
  -e POSTGRES_DB=copaw \
  -e POSTGRES_USER=copaw \
  -e POSTGRES_PASSWORD=your_secure_password \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -p 5432:5432 \
  -v /opt/ai_works/copaw/data:/var/lib/postgresql/data \
  postgres:16-alpine \
  -c max_connections=100 \
  -c shared_buffers=256MB \
  -c effective_cache_size=1GB
```

### 18.3 表结构设计

```sql
-- Agent 元数据
CREATE TABLE agents (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 记忆存储（短期）
CREATE TABLE short_term_memory (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    session_id VARCHAR(50),
    content JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

-- 记忆存储（长期）
CREATE TABLE long_term_memory (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    title VARCHAR(200),
    content TEXT,
    tags TEXT[],
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 执行追踪日志
CREATE TABLE trace_logs (
    id SERIAL PRIMARY KEY,
    trace_id VARCHAR(50),
    span_id VARCHAR(50),
    parent_id VARCHAR(50),
    agent_id VARCHAR(10) REFERENCES agents(id),
    action VARCHAR(100),
    status VARCHAR(20),
    duration_ms INTEGER,
    tokens INTEGER,
    credit_used DECIMAL(10, 4),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Credit 消耗记录
CREATE TABLE credit_logs (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    operation VARCHAR(50),
    tokens INTEGER,
    cost DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 成本统计
CREATE TABLE cost_stats (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(10) REFERENCES agents(id),
    model VARCHAR(50),
    usage_amount DECIMAL(10, 4),
    cost DECIMAL(10, 4),
    period DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 用户对话历史
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    agent_id VARCHAR(10) REFERENCES agents(id),
    channel VARCHAR(20),
    user_message TEXT,
    agent_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 系统配置
CREATE TABLE configs (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 索引优化
CREATE INDEX idx_short_term_agent ON short_term_memory(agent_id, session_id);
CREATE INDEX idx_long_term_agent ON long_term_memory(agent_id);
CREATE INDEX idx_trace_traceid ON trace_logs(trace_id);
CREATE INDEX idx_credit_agent_date ON credit_logs(agent_id, created_at);
CREATE INDEX idx_conversation_user ON conversations(user_id, created_at);
```

### 18.4 连接配置

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
  name: copaw
  user: copaw
  password: ${DB_PASSWORD}
  pool:
    min_size: 5
    max_size: 20
    timeout: 30
  
  # 备份配置
  backup:
    enabled: true
    schedule: "0 2 * * *"  # 每天凌晨 2 点
    retention: 7  # 保留 7 天
    path: /opt/ai_works/copaw/backups
```

### 18.5 数据库管理命令

```bash
# 初始化数据库（首次运行）
cp9 db init

# 备份数据库
cp9 db backup

# 恢复数据库
cp9 db restore <backup_file>

# 查看数据库状态
cp9 db status

# 连接数据库（调试）
cp9 db connect
```

---

## 十九、配置文件

### 18.1 完整配置示例

```yaml
# config.yaml
system:
  name: Copaw
  version: 1.0.0
  env: production

channels:
  feishu:
    enabled: true
    appId: ${FEISHU_APP_ID}
    appSecret: ${FEISHU_APP_SECRET}
    allowFrom: ["+86138xxxxxxx"]
  dingtalk:
    enabled: false
  qq:
    enabled: false
  discord:
    enabled: false
  telegram:
    enabled: false

models:
  prefrontal:
    default: glm-5
    providers:
      zhipu:
        api_key: ${ZHIPU_API_KEY}
        base_url: https://open.bigmodel.cn/api/paas/v4
      minimax:
        api_key: ${MINIMAX_API_KEY}
  
  thalamus:
    model: Qwen/Qwen3-0.6B-FP8
    device: cuda
    quantization: fp8

  sensors:
    print:
      model: nano-banana-pro
      provider: custom

agents:
  "00":
    name: 管理高手
    quota_level: 挑战
    prefrontal: glm-5
  "01":
    name: 学霸
    quota_level: 中等
    prefrontal: glm-5
  "02":
    name: 编程高手
    quota_level: 中等
    prefrontal: glm-5
  "03":
    name: 创意青年
    quota_level: 中等
    prefrontal: glm-5
  "04":
    name: 统计学长
    quota_level: 中等
    prefrontal: glm-5

mcp:
  tavily:
    api_key: ${TAVILY_API_KEY}
    enabled: true
  agent-reach:
    enabled: true
  browser-use:
    enabled: true

logging:
  level: INFO
  format: json
  output: /var/log/copaw/app.log


---

## 二十、技能配置详情

### 19.1 01 号 - 学霸

```yaml
skills:
  required:
    - academic_search     # 学术搜索
    - paper_review        # 论文综述
    - citation_manager   # 引文管理
    - fact_check         # 事实核查
  
  optional:
    - translate          # 翻译
    - data_analysis     # 数据分析
    - visualization     # 可视化

data_sources:
  search:
    - name: 谷歌学术
      priority: 1
    - name: PubMed
      priority: 2
    - name: arXiv
      priority: 3
  media:
    - name: X (Twitter)
      priority: 1
    - name: YouTube
      priority: 2
```

### 19.2 02 号 - 编程高手

```yaml
skills:
  required:
    - code_analysis      # 代码分析
    - code_generation    # 代码生成
    - debug_assist      # 调试辅助
    - git_assist        # Git 辅助
  
  optional:
    - code_review        # 代码审查
    - architecture      # 架构设计
    - security_scan     # 安全扫描

startup_check:
  - python_version
  - node_version
  - git_config
  - docker_status
  - venv_status

data_sources:
  - GitHub
  - CSDN
  - 知乎
  - B 站
  - OpenCode
```

### 19.3 03 号 - 创意青年

```yaml
skills:
  required:
    - text_creative     # 文字创作
    - image_prompt      # 绘画提示词
    - video_script      # 视频脚本
    - copywriter        # 文案撰写
  
  optional:
    - video_edit        # 视频剪辑
    - social_media      # 社媒运营
    - trend_analysis    # 趋势分析

tools:
  print:
    model: nano-banana-pro

data_sources:
  - 小红书
  - 抖音
  - B 站
  - 微博
```

### 19.4 04 号 - 统计学长

```yaml
skills:
  required:
    - summary           # 总结归纳
    - knowledge_org     # 知识组织
    - daily_report      # 日报生成
    - insight_extract   # 洞察提取
  
  optional:
    - knowledge_graph   # 知识图谱
    - trend_report      # 趋势报告
    - recommendation    # 推荐建议

daily_routine:
  trigger: "每天 18:00"
  steps:
    - query_agents_work
    - collect_summaries
    - extract_insights
    - save_to_memory
    - generate_report

data_sources:
  - 喜马拉雅
  - 得物
  - 知乎
```

---

## 二十一、定时任务

### 21.1 任务列表

| 任务名 | Cron 表达式 | 说明 | 执行者 |
|--------|-------------|------|--------|
| `daily_report` | `0 18 * * *` | 每日 18:00 日报 | 04 号 |
| `dinner_meeting` | `0 21 * * */3` | 每 3 天 21:00 晚餐会 | 00 号 |
| `health_check` | `0 */6 * * *` | 每 6 小时健康检查 | 系统 |

### 21.2 定时任务配置

```yaml
cron:
  tasks:
    daily_report:
      enabled: true
      schedule: "0 18 * * *"
      handler: "agent.04.daily_report"
      timeout: 300s
    
    dinner_meeting:
      enabled: true
      schedule: "0 21 * * */3"
      handler: "agent.00.dinner_meeting"
      timeout: 3600s  # 1小时
    
    health_check:
      enabled: true
      schedule: "0 */6 * * *"
      handler: "system.health_check"
      timeout: 60s
```

### 21.3 晚餐交流会详情

> 每 3 天晚上 9-10 点，Agent 互相交流学习

```yaml
dinner_meeting:
  schedule: "0 21 * * */3"  # 每 3 天晚上 9 点
  duration: 1h
  participants: ["00", "01", "02", "03", "04"]
  auto_start: true
  topics:
    - 工作进展分享
    - 遇到的问题讨论
    - 经验互相学习
    - 灵感火花碰撞
  channel: "feishu"  # 交流渠道
  group_name: "Copaw 晚餐会"
```

**交流会流程**：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    晚餐交流会开始                                    │
│  20:55  04 号发出邀请                                               │
│  21:00  00 号主持开场                                               │
│  21:05  01 号分享学术发现                                           │
│  21:15  02 号分享代码技巧                                           │
│  21:25  03 号分享创意灵感                                           │
│  21:35  04 号总结归纳                                               │
│  21:50  自由讨论                                                     │
│  22:00  00 号总结结束                                               │
└─────────────────────────────────────────────────────────────────────┘
```

**记录保存**：

```
agents/04_统计学长/memory/long_term/
├── dinner_2025-02-23.md   # 晚餐交流记录
├── dinner_2025-02-20.md
└── dinner_2025-02-17.md
```

---

## 二十二、待实现功能

### 22.1 高优先级

- [ ] 飞书渠道适配（参考 nanobot）
- [ ] 钉钉渠道开发
- [ ] QQ 渠道开发（OneBot）
- [ ] Discord 渠道开发
- [ ] 电报渠道开发
- [ ] 00 号 Agent 创建流程
- [ ] Credit 配额系统

### 22.2 中优先级

- [ ] 01-04 号 Agent 技能配置
- [ ] 记忆系统（短期+长期）
- [ ] 日/周报自动生成
- [ ] 04 号每日复盘机制

### 22.3 低优先级

- [ ] VEO 视频生成接入
- [ ] Agent 05-08 预留
- [ ] 多语言支持

---

## 二十三、版本历史

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.1 | 2025-02-25 | 新增：全链路追踪ID、Channel事件过滤、晚餐交流会 |
| v1.0 | 2025-02-25 | 初始版本 |

---

## 附录

### A. nanobot 参考

- 仓库：https://github.com/HKUDS/nanobot
- 飞书配置：WebSocket 长连接
- Discord 配置：Bot API

### B. 灵芽 API 参考

- 文档：https://api.lingyaai.cn/doc/
- VEO：文生视频（首尾帧，暂不调用）

### C. 相关资源

- 智谱 GLM：https://www.zhipuai.cn/
- Qwen3：https://github.com/QwenLM/Qwen3
- MiniMax：https://www.minimax.io/

---

*文档版本：v1.0 | 最后更新：2025-02-25*
