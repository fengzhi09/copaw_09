# Cp9 CLI 命令手册

> Cp9 多 Agent 协作系统命令行工具

---

## 一、命令概览

### 1.1 管理命令

```bash
cp9 mgr start|stop|status|init [-c config]
cp9 list agents|channels|mcpservers|skills|providers|sensors|crons|envs
cp9 status agent|channel|mcpserver|skill|provider|sensor|cron|env $key
cp9 version|upgrade|log|reset
```

### 1.2 配置命令

```bash
cp9 set agent|channel|mcpserver|skill|provider|sensor|cron|env $key "{}"
cp9 get agent|channel|mcpserver|skill|provider|sensor|cron|env $key
```

### 1.3 测试命令

```bash
cp9 test agent -id 00 -msg "" -file ""
cp9 test channel feishu|tui send|recv -msg "" -file ""
cp9 test provider minimax -model 'minimax-m2.5' -msg "" -file ""
cp9 test sensor dispatch -msg "" -file ""
cp9 test skill feishu-doc -model '{"provider":"","model":""}' -env '{"APP_ID":""}' -msg "" -file ""
cp9 test cron del|add -agent -id 00 -msg "" -file ""
```

---

## 二、管理命令

### 2.1 mgr - 服务管理

#### 启动服务

```bash
# 使用默认配置启动
cp9 mgr start

# 指定配置文件启动
cp9 mgr start -c ~/.cp9/config.yaml

# 示例
$ cp9 mgr start
✅ Cp9 服务已启动 (PID: 12345)

$ cp9 mgr start -c /etc/cp9/config.yaml
✅ Cp9 服务已启动 (PID: 12346)
```

#### 停止服务

```bash
cp9 mgr stop

# 示例
$ cp9 mgr stop
✅ Cp9 服务已停止
```

#### 查看状态

```bash
cp9 mgr status

# 示例
$ cp9 mgr status
✅ 服务运行中 (PID: 12345)
   启动时间: 2025-02-26 10:00:00
   配置文件: ~/.cp9/config.yaml
```

#### 初始化配置

```bash
cp9 mgr init

# 指定配置路径
cp9 mgr init -c ~/.cp9/config.yaml

# 示例
$ cp9 mgr init
✅ 配置文件已创建: ~/.cp9/config.yaml
   请编辑配置文件后运行 cp9 mgr start
```

---

### 2.2 list - 资源列表

```bash
# 列出所有 Agent
cp9 list agents

# 列出所有 Channel
cp9 list channels

# 列出所有 MCP Server
cp9 list mcpservers

# 列出所有 Skill
cp9 list skills

# 列出所有 Provider
cp9 list providers

# 列出所有 Sensor
cp9 list sensors

# 列出所有 Cron
cp9 list crons

# 列出所有环境变量
cp9 list envs

# 示例
$ cp9 list agents
┌────┬───────────┬────────┐
│ ID │ Name      │ Status │
├────┼───────────┼────────┤
│ 00 │ 管理高手  │ active │
│ 01 │ 学霸     │ active │
│ 02 │ 编程高手 │ active │
│ 03 │ 创意青年 │ active │
│ 04 │ 统计学长 │ active │
└────┴───────────┴────────┘
```

---

### 2.3 status - 查看状态

```bash
# 查看 Agent 状态
cp9 status agent 00

# 查看 Channel 状态
cp9 status channel feishu

# 查看 Provider 状态
cp9 status provider glm-5

# 查看 Cron 状态
cp9 status cron daily

# 示例
$ cp9 status agent 00
Agent: 00 (管理高手)
Status: active
Quota: 100
Channels: feishu
Skills: agent_management, task_coordination

$ cp9 status channel feishu
Channel: feishu
Status: connected
Messages: 1234
LastMsg: 2025-02-26 10:30:00
```

---

### 2.4 version - 版本信息

```bash
cp9 version

# 示例
$ cp9 version
Cp9 v1.0.0
Python: 3.12.0
Config: ~/.cp9/config.yaml
```

---

### 2.5 upgrade - 升级

```bash
cp9 upgrade

# 示例
$ cp9 upgrade
正在检查更新...
当前版本: v1.0.0
最新版本: v1.0.1
✅ 有可用更新，是否升级? [y/N]
```

---

### 2.6 log - 日志

```bash
# 查看最近日志
cp9 log

# 实时跟踪日志
cp9 log -f

# 查看最后 N 行
cp9 log -n 500

# 示例
$ cp9 log -n 20
[2025-02-26 10:30:00] INFO: 服务启动
[2025-02-26 10:30:01] INFO: Channel feishu 已连接
[2025-02-26 10:30:05] INFO: 收到消息 from user_001

$ cp9 log -f
[实时跟踪模式, Ctrl+C 退出]
[2025-02-26 10:30:10] INFO: 收到消息
```

---

### 2.7 reset - 重置

```bash
# 重置配置
cp9 reset

# 示例
$ cp9 reset
⚠️  确定要重置所有配置吗? [y/N]
✅ 配置已重置
```

---

## 三、配置命令

### 3.1 get - 获取配置

```bash
# 获取 Agent 配置
cp9 get agent 00
cp9 get agent 01

# 获取 Channel 配置
cp9 get channel feishu
cp9 get channel dingtalk

# 获取 Provider 配置
cp9 get provider glm-5
cp9 get provider minimax

# 获取 Skill 配置
cp9 get skill feishu-doc
cp9 get skill image-gen

# 获取 Sensor 配置
cp9 get sensor dispatch
cp9 get sensor print

# 获取 Cron 配置
cp9 get cron daily

# 获取环境变量
cp9 get env ZHIPU_API_KEY

# 示例
$ cp9 get agent 00
{
  "id": "00",
  "name": "管理高手",
  "enabled": true,
  "quota": 100,
  "channels": ["feishu"]
}

$ cp9 get channel feishu
{
  "enabled": true,
  "app_id": "cli_xxx",
  "bot_prefix": "/ai"
}
```

---

### 3.2 set - 设置配置

```bash
# 设置 Agent
cp9 set agent 05 '{"name": "学术助手", "enabled": true}'

# 设置 Channel
cp9 set channel feishu '{"enabled": true, "app_id": "xxx"}'

# 设置 Provider
cp9 set provider glm-5 '{"enabled": true, "api_key": "xxx"}'

# 设置 Skill
cp9 set skill feishu-doc '{"enabled": true}'

# 设置 Cron
cp9 set cron daily '{"agent_id": "04", "cron": "0 18 * * *"}'

# 设置环境变量
cp9 set env ZHIPU_API_KEY '"your-api-key"'

# 示例
$ cp9 set agent 05 '{"name": "学术助手", "enabled": true}'
✅ Agent 05 配置已更新

$ cp9 set channel feishu '{"enabled": true}'
✅ Channel feishu 配置已更新
```

---

## 四、测试命令

### 4.1 test agent - 测试 Agent

```bash
# 基本测试
cp9 test agent -id 00 -msg "你好"

# 带文件测试
cp9 test agent -id 01 -msg "分析这个文档" -file "/path/to/doc.pdf"

# 示例
$ cp9 test agent -id 00 -msg "搜索机器学习论文"
意图: search
路由: Agent 01
置信度: 0.85

$ cp9 test agent -id 01 -msg "分析代码" -file "/tmp/main.py"
✅ 收到文件: main.py (Python)
处理结果: 代码分析完成
```

---

### 4.2 test channel - 测试 Channel

```bash
# 发送文本消息
cp9 test channel feishu send -msg "Hello"

# 接收消息测试
cp9 test channel feishu recv -msg "收到请回复"

# 发送文件
cp9 test channel feishu send -file "/path/to/image.png"

# TUI 测试
cp9 test channel tui send -msg "你好"

# 示例
$ cp9 test channel feishu send -msg "Hello World"
✅ 消息已发送 (msg_id: om_xxx)

$ cp9 test channel feishu recv -msg "测试"
等待消息...
收到: om_xxx from user_001
```

---

### 4.3 test provider - 测试 Provider

```bash
# 测试默认模型
cp9 test provider minimax -msg "你好"

# 指定模型
cp9 test provider glm-5 -model glm-5 -msg "你好"

# 带文件
cp9 test provider minimax -msg "分析" -file "/tmp/data.txt"

# 示例
$ cp9 test provider minimax -msg "你好"
✅ 请求成功
Token: 150
响应: 你好！有什么可以帮助你的？

$ cp9 test provider glm-5 -model glm-5 -msg "写首诗"
✅ 请求成功
Token: 320
响应: [生成的诗歌]
```

---

### 4.4 test sensor - 测试 Sensor

```bash
# 测试 dispatch 传感器
cp9 test sensor dispatch -msg "搜索论文"

# 测试 print 传感器
cp9 test sensor print -msg "生成图片"

# 带文件
cp9 test sensor dispatch -msg "识别" -file "/tmp/image.jpg"

# 示例
$ cp9 test sensor dispatch -msg "搜索机器学习"
意图: search
Agent: 01
置信度: 0.90

$ cp9 test sensor print -msg "科技感图片"
✅ 任务已提交
TaskID: task_xxx
```

---

### 4.5 test skill - 测试 Skill

```bash
# 基本测试
cp9 test skill feishu-doc -msg "读取我的文档"

# 指定模型
cp9 test skill feishu-doc -model '{"provider":"glm-5","model":"glm-5"}' -msg "列出知识库"

# 指定环境变量
cp9 test skill feishu-doc -env '{"APP_ID":"xxx","APP_SECRET":"yyy"}' -msg "读取文档"

# 带文件
cp9 test skill feishu-doc -msg "总结这个文档" -file "/tmp/report.pdf"

# 示例
$ cp9 test skill feishu-doc -msg "列出知识库"
✅ 执行成功
结果: 知识库包含 3 个文档

$ cp9 test skill feishu-doc -model '{"provider":"glm-5","model":"glm-5"}' -msg "创建文档"
✅ 文档已创建
DocID: doc_xxx
```

---

### 4.6 test cron - 测试 Cron

```bash
# 列出所有 Cron
cp9 test cron list

# 添加 Cron
cp9 test cron add -agent 04 -id daily -msg "生成每日报告"

# 删除 Cron
cp9 test cron del -id daily

# 示例
$ cp9 test cron list
┌───────┬────────┬─────────────┬────────────┐
│ ID    │ Agent  │ Cron       │ Status    │
├───────┼────────┼─────────────┼───────────┤
│ daily │ 04     │ 0 18 * * *│ active   │
│ weekly│ 04     │ 0 9 * * 0│ active   │
└───────┴────────┴─────────────┴───────────┘

$ cp9 test cron add -agent 04 -id daily -msg "生成日报"
✅ Cron 已添加: daily

$ cp9 test cron del -id daily
✅ Cron 已删除: daily
```

---

## 五、选项说明

### 5.1 通用选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| -c --config | 配置文件路径 | ~/.cp9/config.yaml |

### 5.2 test 命令选项

| 选项 | 说明 | 适用命令 |
|------|------|----------|
| -i --id | 资源 ID | agent, cron |
| -m --msg | 消息内容 | all |
| -f --file | 文件路径 | agent, channel, provider, sensor, skill |
| -M --model | 模型配置 JSON | provider, skill |
| -e --env | 环境变量 JSON | skill |
| -a --agent | Agent ID | cron |

---

*最后更新: 2025-02-26*
