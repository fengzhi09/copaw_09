# Copaw CLI 命令设计

> 最终版本

---

## 一、命令结构

### 1.1 管理命令

```bash
# 服务管理
cp9 mgr start              # 启动服务 (后台运行)
cp9 mgr stop              # 停止服务
cp9 mgr status            # 查看状态
cp9 mgr init              # 初始化配置
```

选项：
- `-c --config` 配置文件路径 (默认 ~/.cp9/config.yaml)

### 1.2 配置命令

```bash
# 获取配置
cp9 get agent 00                    # 获取 Agent 配置
cp9 get channel feishu              # 获取 Channel 配置
cp9 get provider glm-5              # 获取 Provider 配置
cp9 get skill feishu-doc           # 获取 Skill 配置
cp9 get sensor dispatch            # 获取 Sensor 配置
cp9 get cron daily                 # 获取 Cron 配置
cp9 get mcpserver github           # 获取 MCP Server 配置

# 获取状态
cp9 status agent 00                 # 获取 Agent 状态
cp9 status channel feishu          # 获取 Channel 状态

# 设置配置
cp9 set agent 00 '{"enabled": true}'
cp9 set channel feishu '{"enabled": true}'
cp9 set provider glm-5 '{"api_key": "xxx"}'

# 列表
cp9 list agents
cp9 list channels
cp9 list providers
cp9 list skills
cp9 list sensors
cp9 list crons
cp9 list mcpservers
```

### 1.3 测试命令

```bash
# 测试 Agent
cp9 test agent -id 00 -msg "搜索论文"

# 测试 Channel
cp9 test channel feishu send -msg "Hello"
cp9 test channel feishu recv -msg "收到请回复"
cp9 test channel tui send -msg "你好"

# 测试 Provider
cp9 test provider minimax -model 'minimax-m2.5' -msg "你好"
cp9 test provider glm-5 -model 'glm-5' -msg "你好"

# 测试 Sensor
cp9 test sensor dispatch -msg "搜索论文"
cp9 test sensor print -msg "生成图片"

# 测试 Skill
cp9 test skill feishu-doc -model '{"provider":"glm-5","model":"glm-5"}' -env '{"APP_ID":"xxx"}' -msg "读取文档"

# 测试 Cron
cp9 test cron list
cp9 test cron add -agent 04 -id daily -msg "每日报告"
cp9 test cron del -id daily
```

---

## 二、选项说明

### 2.1 通用选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| -c --config | 配置文件路径 | ~/.cp9/config.yaml |

### 2.2 get/status 选项

| 选项 | 说明 |
|------|------|
| (位置参数) | resource type |

### 2.3 set 选项

| 选项 | 说明 |
|------|------|
| (位置参数1) | resource type |
| (位置参数2) | key |
| (位置参数3) | JSON value |

### 2.4 list 选项

| 选项 | 说明 |
|------|------|
| (位置参数) | resource type (复数) |

### 2.5 test agent 选项

| 选项 | 说明 |
|------|------|
| -i --id | Agent ID |
| -m --msg | 测试消息 |

### 2.6 test channel 选项

| 选项 | 说明 |
|------|------|
| (位置参数1) | channel name |
| (位置参数2) | send/recv |
| -m --msg | 消息内容 |
| -f --file | 文件路径 |

### 2.7 test provider 选项

| 选项 | 说明 |
|------|------|
| (位置参数) | provider name |
| -m --model | 模型名称 |
| -m --msg | 测试消息 |

### 2.8 test sensor 选项

| 选项 | 说明 |
|------|------|
| (位置参数) | sensor name |
| -m --msg | 消息内容 |
| -f --file | 文件路径 |

### 2.9 test skill 选项

| 选项 | 说明 |
|------|------|
| (位置参数) | skill name |
| -m --model | 模型配置 JSON |
| -e --env | 环境变量 JSON |
| -m --msg | 消息内容 |
| -f --file | 文件路径 |

### 2.10 test cron 选项

| 选项 | 说明 |
|------|------|
| (位置参数) | list/add/del |
| -a --agent | Agent ID |
| -i --id | Cron ID |
| -m --msg | 消息内容 |

---

## 三、资源类型

| 单数 | 复数 | 说明 |
|------|------|------|
| agent | agents | Agent |
| channel | channels | 通道 |
| provider | providers | 模型提供商 |
| skill | skills | 技能 |
| sensor | sensors | 传感器 |
| cron | crons | 定时任务 |
| mcpserver | mcpservers | MCP 服务器 |

---

## 四、使用示例

```bash
# 启动服务
cp9 mgr start
cp9 mgr start -c /path/to/config.yaml

# 查看状态
cp9 mgr status

# 获取配置
cp9 get agent 00
cp9 get channel feishu

# 设置配置
cp9 set agent 05 '{"enabled": true}'

# 列出资源
cp9 list agents
cp9 list channels

# 测试 Agent
cp9 test agent -id 00 -msg "你好"
cp9 test agent -id 01 -msg "搜索机器学习论文"

# 测试 Channel
cp9 test channel feishu send -msg "Hello World"
cp9 test channel tui recv -msg "测试消息"

# 测试 Provider
cp9 test provider glm-5 -model glm-5 -msg "你好"
cp9 test provider minimax -model minimax-m2.5 -msg "测试"

# 测试 Sensor
cp9 test sensor dispatch -msg "搜索论文"

# 测试 Skill
cp9 test skill feishu-doc -msg "读取文档"

# 测试 Cron
cp9 test cron list
cp9 test cron add -agent 04 -id daily -msg "生成日报"
cp9 test cron del -id daily
```

---

*最后更新: 2025-02-26*
