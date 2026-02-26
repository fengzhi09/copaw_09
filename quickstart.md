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
- CUDA (可选)

### 2.2 安装步骤

```bash
# 克隆项目
git clone https://github.com/lhl_copaw/copaw_09.git
cd copaw_09

# 创建环境
conda create -n copaw python=3.12
conda activate copaw

# 安装依赖
pip install -r requirements.txt
```

### 2.3 初始化

```bash
# 初始化配置
cp9 mgr init
```

配置文件默认: `~/.cp9/config.yaml`

---

## 三、使用方法

### 3.1 服务管理

```bash
# 启动 (后台运行)
cp9 mgr start

# 停止
cp9 mgr stop

# 状态
cp9 mgr status

# 指定配置
cp9 mgr start -c /path/to/config.yaml
```

### 3.2 配置操作

```bash
# 获取配置
cp9 get agent 00
cp9 get channel feishu

# 设置配置
cp9 set agent 05 '{"enabled": true}'

# 列出资源
cp9 list agents
cp9 list channels
```

### 3.3 测试命令

```bash
# 测试 Agent
cp9 test agent -id 00 -msg "搜索论文"

# 测试 Channel
cp9 test channel feishu send -msg "Hello"
cp9 test channel tui recv -msg "测试"

# 测试 Provider
cp9 test provider glm-5 -model glm-5 -msg "你好"

# 测试 Sensor
cp9 test sensor dispatch -msg "搜索论文"

# 测试 Skill
cp9 test skill feishu-doc -msg "读取文档"

# 测试 Cron
cp9 test cron list
cp9 test cron add -agent 04 -id daily -msg "日报"
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

- 飞书、钉钉、QQ、Discord、Telegram

---

## 五、配置文件

配置文件: `~/.cp9/config.yaml`

```yaml
app:
  name: copaw
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

## 六、常见问题

### Q: 如何运行测试?

```bash
cd copaw_09
python -m pytest tests/ -v
```

### Q: 如何查看日志?

查看服务输出或检查配置文件中的日志设置。

---

*最后更新: 2025-02-26*
