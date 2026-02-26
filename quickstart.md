# Copaw 快速入门指南

> Copaw 多 Agent 协作系统

---

## 一、系统简介

Copaw 是一个多 Agent 协作系统，包含：

| Agent | 编号 | 职责 |
|-------|------|------|
| 🏠 管理高手 | 00 | 创建 Agent、系统管理、状态汇报 |
| 🧠 学霸 | 01 | 学术搜索、论文调研 |
| 💻 编程高手 | 02 | 代码开发、工具链检查 |
| 🎨 创意青年 | 03 | 文字创作、绘画提示词 |
| 📊 统计学长 | 04 | 每日复盘、知识收藏 |

---

## 二、安装配置

### 2.1 环境要求

- Python 3.10+
- CUDA (可选，用于本地模型)
- PostgreSQL (可选，用于记忆存储)

### 2.2 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/lhl coping/copaw_09.git
cd copaw_09

# 2. 创建虚拟环境
conda create -n copaw python=3.12
conda activate copaw

# 3. 安装依赖
pip install -r requirements.txt
```

### 2.3 配置环境变量

```bash
# 飞书配置
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_BOT_PREFIX="/ai"

# 智谱 API (用于前额叶)
export ZHIPU_API_KEY="your_zhipu_key"

# MiniMax API (备用)
export MINIMAX_API_KEY="your_minimax_key"
```

### 2.4 配置文件

创建 `~/.copaw_mgr.yaml`:

```yaml
app:
  name: copaw
  version: "1.0"

config:
  channel:
    feishu:
      enabled: true
      app_id: "${FEISHU_APP_ID}"
      app_secret: "${FEISHU_APP_SECRET}"
      bot_prefix: "/ai"
      filters:
        ignore_keywords: []
        ignore_users: []
```

---

## 三、使用方法

### 3.1 启动系统

```bash
# 方式1: 直接运行
python -m app.main

# 方式2: 使用启动脚本
bash start.sh
```

### 3.2 通过飞书对话

| 命令 | 说明 |
|------|------|
| `@AI 搜索机器学习论文` | 学术搜索 |
| `@AI 帮我写个 Python 脚本` | 代码开发 |
| `@AI 写一段小红书文案` | 创意写作 |
| `@AI 创建新 Agent` | 系统管理 |
| `@AI 查看本月成本` | 统计报表 |

### 3.3 创建新 Agent

```
用户: 创建一个学术助手
AI: 请问需要具备哪些技能？
用户: 搜索和论文调研
AI: 📋 需求确认
    - Agent 名称: 学术助手
    - 角色: academic
    - 技能: academic_search, paper_review
    请确认以上信息，回复"确认"创建
用户: 确认
AI: ✅ Agent 创建成功！
```

---

## 四、模块说明

### 4.1 Gateway (网关)

消息入口，负责：
- 身份认证
- 事件过滤
- 消息分发

### 4.2 Brain (脑部)

- **丘脑 (Thalamus)**: 意图识别、路由决策
- **前额叶 (Prefrontal)**: 深度思考、推理规划

### 4.3 Channels (渠道)

支持的通讯渠道：
- 飞书
- 钉钉
- QQ
- Discord
- Telegram

### 4.4 记忆系统

- **短期记忆**: 当前会话上下文
- **长期记忆**: 重要信息持久化

---

## 五、开发指南

### 5.1 项目结构

```
copaw_09/
├── app/
│   ├── brain/          # 脑部模块
│   ├── channels/       # 渠道适配
│   ├── gateway/        # 网关
│   └── router.py       # 路由
├── agents/
│   ├── agent_00_管理高手/
│   ├── agent_01_学霸/
│   └── ...
├── tests/              # 单元测试
└── docs/               # 文档
```

### 5.2 运行测试

```bash
cd /home/ace09/bots/copaw_09
python -m pytest tests/ -v
```

---

## 六、常见问题

### Q1: 如何添加新的 Agent？

编辑 `agents/registry/__init__.py`，在 `PREDEFINED_AGENTS` 中添加。

### Q2: 如何添加新的渠道？

在 `app/channels/` 下创建新的 Channel 类，继承 `BaseChannel`。

### Q3: 如何配置模型？

在 `app/brain/` 模块中修改 `MODEL_CONFIG`。

---

## 七、联系支持

- 问题反馈: GitHub Issues
- 功能建议: 联系维护者

---

*最后更新: 2025-02-26*
