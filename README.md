# cp9 🐾

> 多 Agent 智能协作系统

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)

---

## 一、系统简介

cp9 (cp9) 是一个多 Agent 协作系统，包含：

| Agent | 编号 | 职责 |
|-------|------|------|
| 🏠 管理高手 | 00 | 系统管理、创建 Agent |
| 🧠 学霸 | 01 | 学术搜索、论文调研 |
| 💻 编程高手 | 02 | 代码开发、工具链检查 |
| 🎨 创意青年 | 03 | 文字创作、绘画提示词 |
| 📊 统计学长 | 04 | 每日复盘、知识收藏 |

---

## 二、快速开始

### 2.1 安装

```bash
git clone https://github.com/lhl_cp9/cp9.git
cd cp9
conda create -n cp9 python=3.12
conda activate cp9
pip install -r requirements.txt
```

### 2.2 初始化

```bash
cp9 mgr init
```

### 2.3 启动服务

```bash
cp9 mgr start
```

---

## 三、命令手册

### 3.1 管理命令

| 命令 | 说明 |
|------|------|
| `cp9 mgr start` | 启动服务 (后台运行) |
| `cp9 mgr stop` | 停止服务 |
| `cp9 mgr status` | 查看状态 |
| `cp9 mgr init` | 初始化配置 |
| `cp9 version` | 查看版本 |
| `cp9 upgrade` | 升级版本 |
| `cp9 log` | 查看日志 |
| `cp9 log -f` | 实时跟踪日志 |
| `cp9 reset` | 重置配置 |

### 3.2 列表命令

| 命令 | 说明 |
|------|------|
| `cp9 list agents` | 列出所有 Agent |
| `cp9 list channels` | 列出所有 Channel |
| `cp9 list providers` | 列出所有 Provider |
| `cp9 list skills` | 列出所有 Skill |
| `cp9 list sensors` | 列出所有 Sensor |
| `cp9 list crons` | 列出所有 Cron |
| `cp9 list envs` | 列出所有环境变量 |

### 3.3 状态命令

| 命令 | 说明 |
|------|------|
| `cp9 status agent 00` | 查看 Agent 状态 |
| `cp9 status channel feishu` | 查看 Channel 状态 |
| `cp9 status provider glm-5` | 查看 Provider 状态 |

### 3.4 配置命令

```bash
# 获取配置
cp9 get agent 00
cp9 get channel feishu
cp9 get provider glm-5

# 设置配置
cp9 set agent 05 '{"enabled": true}'
cp9 set channel feishu '{"enabled": true}'
```

### 3.5 测试命令

```bash
# 测试 Agent
cp9 test agent -id 00 -msg "你好"
cp9 test agent -id 01 -msg "搜索论文" -file "/path/to/doc.pdf"

# 测试 Channel
cp9 test channel feishu send -msg "Hello"
cp9 test channel feishu recv -msg "收到请回复"
cp9 test channel tui send -msg "你好"

# 测试 Provider
cp9 test provider minimax -msg "你好"
cp9 test provider glm-5 -model glm-5 -msg "写首诗"

# 测试 Sensor
cp9 test sensor dispatch -msg "搜索论文"
cp9 test sensor print -msg "生成图片"

# 测试 Skill
cp9 test skill feishu-doc -msg "列出知识库"
cp9 test skill image-gen -msg "科技感海报"

# 测试 Cron
cp9 test cron list
cp9 test cron add -agent 04 -id daily -msg "生成日报"
cp9 test cron del -id daily
```

---

## 四、配置文件

配置文件: `~/.cp9/config.yaml`

```yaml
app:
  name: cp9
  version: "1.0"

channels:
  feishu:
    enabled: true
    app_id: "xxx"
    app_secret: "xxx"

providers:
  glm-5:
    enabled: true
    api_key: "xxx"

agents:
  00:
    name: "管理高手"
    enabled: true
```

---

## 五、文档

- [📖 CLI 命令手册](./CLI.md) - 完整命令参考
- [🏗️ 架构文档](./ARCHITECTURE.md) - 系统架构详解

---

*最后更新: 2025-02-26*
