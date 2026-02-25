# CoPaw 🦞

> Works for you, grows with you.

Your Personal AI Assistant; easy to install, deploy on your own machine or on the cloud; supports multiple chat apps with easily extensible capabilities.

---

## 项目简介

CoPaw 是一款**个人助理型产品**，部署在你自己的环境中。

- **多通道对话** — 通过钉钉、飞书、QQ、Discord、iMessage 等与你对话
- **定时执行** — 按你的配置自动运行任务
- **能力由 Skills 决定，有无限可能** — 内置定时任务、PDF 与表单、Word/Excel/PPT 文档处理、新闻摘要、文件阅读等
- **数据全在本地** — 不依赖第三方托管

---

## 核心特性

### 多通道支持
| 频道 | 状态 |
|------|------|
| 钉钉 (DingTalk) | ✅ |
| 飞书 (Feishu/Lark) | ✅ |
| QQ | ✅ |
| Discord | ✅ |
| iMessage (仅 Mac) | ✅ |
| Console (Web UI) | ✅ |

### 内置 Skills
- **定时任务 (cron)** — 定时执行预设任务
- **PDF 处理** — 读取、提取、合并、拆分
- **Office 文档** — Word/Excel/PPT 读写
- **新闻摘要** — 各领域资讯查询
- **文件阅读** — 文本类文件解析
- **邮件管理** — Himalaya CLI

### 数据与隐私
- 所有数据存储在本地
- 支持本地/云端部署
- 无第三方托管

---

## 安装

```bash
# 从 PyPI 安装
pip install copaw

# 或从源码安装
# git clone https://github.com/agentscope-ai/CoPaw.git // 来自 https://pypi.org/project/copaw
# cd CoPaw
 git clone https://github.com/fengzhi09/copaw_09
cd copaw_09
pip install -e .

# 启动服务
copaw app
```

### 快速开始

```bash
# 1. 初始化工作目录
copaw init my-assistant

# 2. 配置频道（钉钉/飞书/QQ/Discord/iMessage）
# 参考: https://copaw.agentscope.io/docs/channels

# 3. 启动服务
copaw app
```

---

## 项目来源

本项目源码从 Python 包 `copaw` 的 site-packages 目录中提取，原版由 [AgentScope 团队](https://github.com/agentscope-ai) 基于以下项目构建：

- [AgentScope](https://github.com/agentscope-ai/agentscope)
- [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime)
- [ReMe](https://github.com/agentscope-ai/ReMe)

官方文档：[copaw.agentscope.io](https://copaw.agentscope.io/docs/intro)

---

## 目录结构

```
copaw/
├── agents/              # Agent 核心实现
│   ├── skills/         # Skills 管理与加载
│   ├── memory/         # 记忆系统
│   └── tools/          # 工具集
├── app/                # 应用主程序
│   ├── channels/       # 频道实现（钉钉/飞书/QQ/Discord/iMessage）
│   ├── crons/          # 定时任务
│   └── runner/         # 运行器
├── cli/                # 命令行工具
├── config/             # 配置管理
├── console/            # Web 控制台前端
├── envs/               # 环境封装
├── providers/          # 模型提供商
└── utils/              # 工具函数
```

---

## 文档

| 主题 | 说明 |
|------|------|
| [Introduction](https://copaw.agentscope.io/docs/intro) | CoPaw 是什么及如何使用 |
| [Quick Start](https://copaw.agentscope.io/docs/quickstart) | 安装与快速启动 |
| [Console](https://copaw.agentscope.io/docs/console) | Web UI 对话与配置 |
| [Channels](https://copaw.agentscope.io/docs/channels) | 频道配置（钉钉/飞书/QQ/Discord/iMessage） |
| [Heartbeat](https://copaw.agentscope.io/docs/heartbeat) | 定时自检与摘要 |
| [CLI](https://copaw.agentscope.io/docs/cli) | 命令行工具 |
| [Skills](https://copaw.agentscope.io/docs/skills) | 扩展与自定义能力 |
| [Config](https://copaw.agentscope.io/docs/config) | 工作目录与配置文件 |

---

## 后续规划

本项目将持续扩展更多企业级能力：

- **MCP (Model Context Protocol)** — 支持 MCP 协议的工具接入
- **外置 Skills** — 支持从 ClawHub 等平台安装更多 Skills
- **多 Agent 协作** — 支持多 Agent 联合工作流
- **企业版** — 团队协作、企业级权限管理
- **Credit Plan** — 基于积分的计划体系

详见 [ROADMAP.md](./ROADMAP.md)

---

## License

基于 AgentScope 相关开源协议。

---

<p align="center">
  <sub>Built on AgentScope · CLI: copaw</sub>
</p>
