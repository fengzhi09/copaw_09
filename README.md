# Copaw 🐾

> 多 Agent 智能协作系统 | 基于「前额叶-丘脑-小脑」架构

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/postgreSQL-16+-blue.svg)](https://www.postgresql.org/)

---

## 📋 简介

Copaw 是一个多 Agent 协作系统，通过「前额叶-丘脑-小脑」架构实现智能协作。每个 Agent 拥有独立记忆、独立 Credit、独立模型配额，可通过多种渠道与用户交互。

---

## ✨ 特性

- 🤖 **多 Agent 协作** - 00 号管理高手 + 01-04 号专业职能 Agent
- 🧠 **独立记忆** - 每个 Agent 拥有短期/长期记忆
- 💰 **资源隔离** - 独立 Credit 和模型配额
- 💵 **成本计算** - 实时成本追踪和报表
- 🔗 **多渠道** - 飞书、钉钉、QQ、Discord、电报
- 🌐 **Web 管理端** - 对话式管理界面（仅限 00/04 号）
- 🐳 **Docker 部署** - 一键启动 PostgreSQL
- 🔄 **错误处理** - 自动重试和模型降级
- ⏰ **定时任务** - 每日复盘、每 3 天晚餐交流会
- 🔍 **全链路追踪** - trace_id + span_id 追溯

---

## 🏗️ 系统架构

```
用户 → Channels → Gateway → 丘脑 → Agent → 小脑 → PostgreSQL

┌─────────────────────────────────────────────────────────────────┐
│  前额叶 (Prefrontal)  │  GLM-5  │  深度思考                    │
├─────────────────────────────────────────────────────────────────┤
│  丘脑 (Thalamus)      │ Qwen3   │  意图识别 + 路由            │
├─────────────────────────────────────────────────────────────────┤
│  小脑 (Cerebellum)    │ Python  │  任务执行 + 工具调用        │
├─────────────────────────────────────────────────────────────────┤
│  感官 (Sensors)       │ nano    │  print(文生图)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Agent 矩阵

| 编号 | 角色 | 职责 | 沟通风格 |
|------|------|------|----------|
| **00** | 🏠 管理高手 | 创建 Agent、初始化、汇报状态 | 主动汇报、确认后执行 |
| **01** | 🧠 学霸 | 学术搜索、论文调研、多工具检索 | 理性严谨、证据充分 |
| **02** | 💻 编程高手 | 代码开发、工具链检查、技术调研 | 逻辑缜密、结构化 |
| **03** | 🎨 创意青年 | 文字创作、绘画提示词、视频脚本 | 发散思维、积极执行 |
| **04** | 📊 统计学长 | 每日复盘、知识收藏、总结启发 | 善于倾听、归纳整理 |

---

## 🔗 Channels（消息渠道）

| 渠道 | 协议 | 状态 |
|------|------|------|
| 飞书 | WebSocket | 🔶 开发中 |
| 钉钉 | WebHook | ⏳ 待开发 |
| QQ | OneBot | ⏳ 待开发 |
| Discord | Bot API | ⏳ 待开发 |
| 电报 | Bot API | ⏳ 待开发 |

**事件过滤**：支持忽略指定事件类型、用户、关键词

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/fengzhi09/lhl_copaw_prjs.git
cd lhl_copaw_prjs/copaw
```

### 2. 启动 PostgreSQL

```bash
docker run -d \
  --name copaw-db \
  -e POSTGRES_DB=copaw \
  -e POSTGRES_USER=copaw \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  -v ./data:/var/lib/postgresql/data \
  postgres:16-alpine
```

### 3. 配置环境

```bash
cp config.example.yaml config.yaml
vim config.yaml
```

### 4. 启动服务

```bash
cp9 dev              # 开发模式
cp9 start --daemon  # 生产模式
```

---

## 📖 文档

- [📑 设计文档](./DESIGN.md) - 完整设计规范 (24 章)
- [🏗️ 架构文档](./ARCHITECTURE.md) - 系统架构详解
- [🗺️ 路线图](./ROADMAP.md) - 开发计划

---

## 📊 命令

```bash
cp9                      # 启动系统
cp9 status               # 查看状态
cp9 list                 # 列出 Agent
cp9 create <需求>        # 创建新 Agent
cp9 credit               # 查看 Credit

# 定时任务
cp9 cron add "0 18 * * *" daily_report      # 每日 18:00 日报
cp9 cron add "0 21 * * */3" dinner_meeting # 每 3 天 21:00 晚餐会
```

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| **语言** | Python 3.10+ |
| **数据库** | PostgreSQL 16 (Docker) |
| **前额叶** | GLM-5 (智谱) |
| **丘脑** | Qwen3-0.6B-FP8 (本地 GPU) |
| **图片** | nano-banana-pro |
| **渠道** | 飞书/钉钉/QQ/Discord/电报 |

---

## 📄 许可证

MIT License

---

## 👤 作者

**卡泡** - 科研编程助理

*让 AI 成为你的智能伙伴*
