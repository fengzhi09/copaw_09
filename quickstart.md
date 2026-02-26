# Cp9 快速入门

> Cp9 多 Agent 协作系统

---

## 一、安装

```bash
git clone https://github.com/lhl_cp9/cp9.git
cd cp9
conda create -n cp9 python=3.12
conda activate cp9
pip install -r requirements.txt
```

---

## 二、快速开始

```bash
# 初始化
cp9 mgr init

# 启动
cp9 mgr start

# 状态
cp9 mgr status
```

---

## 三、命令速查

### 管理

| 命令 | 说明 |
|------|------|
| `cp9 mgr start` | 启动服务 |
| `cp9 mgr stop` | 停止服务 |
| `cp9 mgr status` | 查看状态 |
| `cp9 mgr init` | 初始化 |
| `cp9 version` | 版本 |
| `cp9 log` | 日志 |

### 列表

| 命令 | 说明 |
|------|------|
| `cp9 list agents` | Agent 列表 |
| `cp9 list channels` | Channel 列表 |
| `cp9 list providers` | Provider 列表 |
| `cp9 list skills` | Skill 列表 |
| `cp9 list sensors` | Sensor 列表 |
| `cp9 list crons` | Cron 列表 |

### 状态

| 命令 | 说明 |
|------|------|
| `cp9 status agent 00` | Agent 状态 |
| `cp9 status channel feishu` | Channel 状态 |

### 配置

```bash
cp9 get agent 00
cp9 set agent 05 '{"enabled": true}'
```

### 测试

```bash
# Agent
cp9 test agent -id 00 -msg "你好"

# Channel
cp9 test channel feishu send -msg "Hello"
cp9 test channel feishu recv -msg "测试"

# Provider
cp9 test provider minimax -msg "你好"

# Sensor
cp9 test sensor dispatch -msg "搜索"

# Skill
cp9 test skill feishu-doc -msg "列出知识库"

# Cron
cp9 test cron list
cp9 test cron add -agent 04 -id daily -msg "日报"
```

---

## 四、选项

| 选项 | 说明 |
|------|------|
| -c | 配置文件 |
| -i --id | ID |
| -m --msg | 消息 |
| -f --file | 文件 |
| -M --model | 模型 |
| -e --env | 环境变量 |
| -a --agent | Agent ID |

---

*最后更新: 2025-02-26*
