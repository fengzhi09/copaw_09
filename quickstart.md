# Copaw 快速入门指南

> Copaw 多 Agent 协作系统

---

## 一、系统简介

Copaw (cp9) 是一个多 Agent 协作系统，包含：

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
git clone https://github.com/fengzhi09/lhl_copaw_prjs.git
cd lhl_copaw_prjs/copaw

# 2. 创建虚拟环境
conda create -n cp9 python=3.12
conda activate cp9

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

创建 `~/.cp9/config.yaml`:

```yaml
app:
  name: cp9
  version: "1.0"

mgr:
  log_level: info

channels:
  feishu:
    enabled: true
    app_id: "${FEISHU_APP_ID}"
    app_secret: "${FEISHU_APP_SECRET}"
    bot_prefix: "/ai"

providers:
  minimax:
    enabled: true
    api_key: "${MINIMAX_API_KEY}"
  zhipu:
    enabled: true
    api_key: "${ZHIPU_API_KEY}"
```

---

## 三、CLI 命令

### 3.1 管理命令 (mgr)

```bash
# 初始化配置
cp9 mgr init -c ~/.cp9/config.yaml

# 启动服务（后台运行）
cp9 mgr start -c ~/.cp9/config.yaml

# 停止服务
cp9 mgr stop

# 查看状态
cp9 mgr status
```

### 3.2 查询命令

```bash
# 获取资源
cp9 get agent 00
cp9 get channel feishu
cp9 get provider minimax

# 查看状态
cp9 status agent
cp9 status channel
cp9 status provider
```

### 3.3 设置命令

```bash
# 设置资源配置
cp9 set agent 05 '{"name":"学术助手","role":"academic"}'
cp9 set channel feishu '{"enabled":true}'
cp9 set provider minimax '{"api_key":"xxx"}'
```

### 3.4 列表命令

```bash
# 列出所有资源
cp9 list agents
cp9 list channels
cp9 list providers
cp9 list skills
cp9 list crons
```

### 3.5 测试命令

```bash
# 测试 Agent
cp9 test agent -id 00 -msg "你好"
cp9 test agent -id 01 -msg "搜索机器学习论文"

# 测试 Channel
cp9 test channel feishu send -msg "Hello"
cp9 test channel tui recv -msg "测试消息"

# 测试 Provider
cp9 test provider minimax -model 'minimax-m2.5' -msg "你好"

# 测试 Sensor
cp9 test sensor dispatch -msg "搜索论文"

# 测试 Skill
cp9 test skill feishu-doc -msg "列出知识库"

# 测试 Cron
cp9 test cron add -agent 01 -msg "每日调研" -cron "0 9 * * *"
cp9 test cron del -id <task_id>
```

---

## 四、使用示例

### 4.1 通过飞书对话

| 命令 | 说明 |
|------|------|
| `@AI 搜索机器学习论文` | 学术搜索 |
| `@AI 帮我写个 Python 脚本` | 代码开发 |
| `@AI 写一段小红书文案` | 创意写作 |
| `@AI 创建新 Agent` | 系统管理 |
| `@AI 查看本月成本` | 统计报表 |

### 4.2 创建新 Agent

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

## 五、模块说明

### 5.1 Gateway (网关)

消息入口，负责：
- 身份认证
- 事件过滤
- 消息分发

### 5.2 Brain (脑部)

- **丘脑 (Thalamus)**: 意图识别、路由决策
- **前额叶 (Prefrontal)**: 深度思考、推理规划

### 5.3 Channels (渠道)

支持的通讯渠道：
- 飞书
- 钉钉
- QQ
- Discord
- Telegram

### 5.4 记忆系统

- **短期记忆**: 当前会话上下文
- **长期记忆**: 重要信息持久化

---

## 六、常见问题

### Q1: 如何添加新的 Agent？

```bash
cp9 mgr init  # 初始化后自动发现
```

### Q2: 如何添加新的渠道？

在配置文件中添加渠道配置：

```yaml
channels:
  discord:
    enabled: true
    bot_token: "xxx"
```

### Q3: 如何配置模型？

```bash
cp9 set provider minimax '{"api_key":"xxx","default_model":"minimax-m2.5"}'
```

---

## 七、命令速查表

| 命令 | 说明 |
|------|------|
| `cp9 mgr start` | 启动服务 |
| `cp9 mgr stop` | 停止服务 |
| `cp9 mgr status` | 查看状态 |
| `cp9 get <type> <key>` | 获取资源 |
| `cp9 set <type> <key> <json>` | 设置资源 |
| `cp9 list <type>s` | 列出资源 |
| `cp9 test agent -id 00 -msg ""` | 测试 Agent |
| `cp9 test channel feishu send -msg ""` | 测试 Channel |
| `cp9 test provider minimax -model '' -msg ""` | 测试 Provider |

---

## 八、联系支持

- 问题反馈: GitHub Issues
- 功能建议: 联系维护者

---

*最后更新: 2025-02-26*
