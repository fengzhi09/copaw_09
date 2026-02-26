# Copaw CLI 命令设计

> 版本：v1.0 | 状态：待确认

---

## 一、命令结构

```
cp9 <command> [subcommand] [options] [arguments]
```

---

## 二、命令详解

### 2.1 管理命令 (mgr)

```bash
# 启动服务（后台运行）
cp9 mgr start -c ~/.cp9/config.yaml

# 停止服务
cp9 mgr stop

# 查看状态
cp9 mgr status

# 初始化配置
cp9 mgr init -c ~/.cp9/config.yaml
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --config | -c | 配置文件路径 | ~/.cp9/config.yaml |

---

### 2.2 查询命令 (get/status)

```bash
# 获取单个资源
cp9 get agent 00
cp9 get channel feishu
cp9 get mcpserver github
cp9 get skill feishu-doc
cp9 get provider minimax
cp9 get sensor dispatch
cp9 get cron daily_report

# 查看资源状态
cp9 status agent
cp9 status channel
cp9 status mcpserver
cp9 status skill
cp9 status provider
cp9 status sensor
cp9 status cron
```

---

### 2.3 设置命令 (set)

```bash
# 设置资源配置
cp9 set agent 05 '{"name":"学术助手","role":"academic"}'
cp9 set channel feishu '{"enabled":true,"app_id":"xxx"}'
cp9 set mcpserver github '{"token":"xxx"}'
cp9 set skill feishu-doc '{"enabled":true}'
cp9 set provider minimax '{"api_key":"xxx"}'
cp9 set sensor dispatch '{"model":"qwen3-0.6b"}'
cp9 set cron daily_report '{"enabled":true,"cron":"0 18 * * *"}'
```

---

### 2.4 列表命令 (list)

```bash
# 列出所有资源
cp9 list agents
cp9 list channels
cp9 list mcpservers
cp9 list skills
cp9 list providers
cp9 list sensors
cp9 list crons
```

---

### 2.5 测试命令 (test)

#### 2.5.1 test agent

```bash
# 测试 Agent 响应
cp9 test agent -id 00 -msg "你好"
cp9 test agent -id 01 -msg "搜索机器学习论文"
cp9 test agent -id 02 -msg "写一个Python函数"
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --id | -i | Agent ID | required |
| --msg | -m | 测试消息 | required |

#### 2.5.2 test channel

```bash
# 测试 Channel 发送
cp9 test channel feishu send -msg "Hello"
cp9 test channel feishu send -file /path/to/image.png

# 测试 Channel 接收
cp9 test channel tui recv -msg "测试消息"
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --msg | -m | 消息内容 | optional |
| --file | -f | 文件路径 | optional |

#### 2.5.3 test provider

```bash
# 测试 LLM Provider
cp9 test provider minimax -model 'minimax-m2.5' -msg "你好"
cp9 test provider zhipu -model 'glm-5' -msg "介绍你自己"

# 支持的模型
# - minimax: minimax-m2.5, minimax-m2.5-highspeed
# - zhipu: glm-5, glm-4-flash
# - openai: gpt-4o, gpt-4o-mini
# - anthropic: claude-3-5-sonnet
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --model | -m | 模型名称 | required |
| --msg | -m | 测试消息 | "你好" |

#### 2.5.4 test sensor

```bash
# 测试 Sensor
cp9 test sensor dispatch -msg "搜索论文"
cp9 test sensor print -msg "一只猫"
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --msg | -m | 测试消息 | required |
| --file | -f | 测试文件 | optional |

#### 2.5.5 test skill

```bash
# 测试 Skill
cp9 test skill feishu-doc -msg "列出知识库"
cp9 test skill text-creative -msg "写一首诗"
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --msg | -m | 测试消息 | required |
| --env | -e | 环境变量 JSON | {} |
| --model | -m | 模型配置 JSON | {} |

#### 2.5.6 test cron

```bash
# 添加定时任务
cp9 test cron add -agent 01 -msg "每日调研" -cron "0 9 * * *"
cp9 test cron add -agent 02 -msg "代码审查" -cron "0 14 * * 1-5"

# 删除定时任务
cp9 test cron del -id <task_id>

# 列出定时任务
cp9 test cron list
```

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| --agent | -a | Agent ID | required |
| --msg | -m | 消息内容 | required |
| --cron | -c | Cron 表达式 | required |
| --id | -i | 任务 ID | required |

---

## 三、命令速查表

| 命令 | 说明 |
|------|------|
| `cp9 mgr start` | 后台启动服务 |
| `cp9 mgr stop` | 停止服务 |
| `cp9 mgr status` | 查看服务状态 |
| `cp9 mgr init` | 初始化配置 |
| `cp9 get <type> <key>` | 获取资源 |
| `cp9 status <type>` | 查看资源状态 |
| `cp9 set <type> <key> <json>` | 设置资源 |
| `cp9 list <type>s` | 列出所有资源 |
| `cp9 test agent -id 00 -msg ""` | 测试 Agent |
| `cp9 test channel feishu send -msg ""` | 测试 Channel |
| `cp9 test provider minimax -model '' -msg ""` | 测试 Provider |
| `cp9 test sensor dispatch -msg ""` | 测试 Sensor |
| `cp9 test skill feishu-doc -msg ""` | 测试 Skill |
| `cp9 test cron add -agent 01 -msg "" -cron ""` | 测试 Cron |

---

## 四、输出格式

### 4.1 JSON 输出

```bash
cp9 get agent 00 --json
```

```json
{
  "id": "00",
  "name": "管理高手",
  "role": "master",
  "status": "active"
}
```

### 4.2 表格输出

```bash
cp9 list agents
```

```
┌──────┬──────────┬────────┬────────┐
│ ID   │ Name     │ Role   │ Status │
├──────┼──────────┼────────┼────────┤
│ 00   │ 管理高手  │ master │ active │
│ 01   │ 学霸     │ academic│ active │
│ 02   │ 编程高手 │ developer│ active│
│ 03   │ 创意青年 │ creative│ active │
│ 04   │ 统计学长 │ collector│active │
└──────┴──────────┴────────┴────────┘
```

---

## 五、配置文件

```yaml
# ~/.cp9/config.yaml

app:
  name: copaw
  version: "1.0"

mgr:
  log_level: info
  log_file: ~/.cp9/logs/copaw.log
  pid_file: ~/.cp9/copaw.pid

channels:
  feishu:
    enabled: true
    app_id: ${FEISHU_APP_ID}
    app_secret: ${FEISHU_APP_SECRET}
  tui:
    enabled: true

providers:
  minimax:
    enabled: true
    api_key: ${MINIMAX_API_KEY}
  zhipu:
    enabled: true
    api_key: ${ZHIPU_API_KEY}

agents:
  default_quota: 100

crons:
  daily_report:
    enabled: true
    cron: "0 18 * * *"
```

---

*最后更新: 2025-02-26*
