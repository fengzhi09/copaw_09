# CoPaw 🦞

> Works for you, grows with you.

Personal AI Assistant - Easy to install, deploy locally or on cloud, supports multiple chat apps with extensible capabilities.

---

## 项目简介

CoPaw 是一款**个人助理型产品**，基于 [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime) 构建，部署在你的本地或云端环境中。

- **多通道对话** — 通过钉钉、飞书、QQ、Discord、iMessage 与你对话
- **定时执行** — 按配置自动运行任务（cron）
- **能力由 Skills 决定** — 内置 PDF/Office/新闻/文件阅读等能力，支持自定义扩展
- **数据本地存储** — 不依赖第三方托管

---

## 核心特性

### 多通道支持
| 频道 | 文件 | 状态 |
|------|------|------|
| 飞书 (Feishu/Lark) | `app/channels/feishu.py` | ✅ |
| 钉钉 (DingTalk) | `app/channels/dingtalk.py` | ✅ |
| QQ | `app/channels/qq.py` | ✅ |
| Discord | `app/channels/discord_.py` | ✅ |
| iMessage (仅 Mac) | `app/channels/imessage.py` | ✅ |
| Console (Web UI) | `app/channels/console.py` | ✅ |

### 内置 Skills
| Skill | 路径 | 功能 |
|-------|------|------|
| pdf | `agents/skills/pdf/` | PDF 读取、提取、合并、拆分 |
| xlsx | `agents/skills/xlsx/` | Excel 读写、公式、图表 |
| docx | `agents/skills/docx/` | Word 文档处理 |
| pptx | `agents/skills/pptx/` | PPT 演示文稿 |
| news | `agents/skills/news/` | 新闻资讯查询 |
| himalaya | `agents/skills/himalaya/` | 邮件管理 |
| cron | `agents/skills/cron/` | 定时任务 |
| browser_visible | `agents/skills/browser_visible/` | 可见浏览器 |
| file_reader | `agents/skills/file_reader/` | 文本文件读取 |

### Agent 工具 (Tools)
| Tool | 文件 | 功能 |
|------|------|------|
| file_io | `agents/tools/file_io.py` | 文件读写 |
| shell | `agents/tools/shell.py` | 执行命令 |
| browser_control | `agents/tools/browser_control.py` | 浏览器控制 |
| browser_snapshot | `agents/tools/browser_snapshot.py` | 浏览器截图 |
| memory_search | `agents/tools/memory_search.py` | 记忆搜索 |
| desktop_screenshot | `agents/tools/desktop_screenshot.py` | 桌面截图 |
| send_file | `agents/tools/send_file.py` | 发送文件 |
| get_current_time | `agents/tools/get_current_time.py` | 获取时间 |

---

## 版本信息

- **当前版本**: 0.0.2
- **源码来源**: 从 Python 包 `copaw` (v0.0.2) site-packages 提取
- **构建基础**: 
  - [AgentScope](https://github.com/agentscope-ai/agentscope)
  - [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime)
  - [ReMe](https://github.com/agentscope-ai/ReMe)

---

## 目录结构

```
copaw/
├── __init__.py              # 包入口
├── __version__.py           # 版本号 (0.0.2)
├── constant.py              # 常量定义
├── copaw_mgr.py             # 生命周期管理脚本
│
├── agents/                  # Agent 核心
│   ├── react_agent.py       # CoPawAgent (ReAct 推理)
│   ├── skills_manager.py    # Skills 加载与管理
│   ├── prompt.py            # Prompt 模板
│   ├── schema.py            # 数据结构
│   ├── utils.py             # 工具函数
│   ├── md_files/           # Markdown 文件处理
│   ├── memory/             # 记忆系统
│   ├── skills/             # 内置 Skills (9个)
│   └── tools/               # Agent 工具集
│
├── app/                     # 应用主程序
│   ├── _app.py             # FastAPI 应用入口
│   ├── channels/           # 频道实现 (6个)
│   ├── crons/              # 定时任务
│   ├── runner/             # AgentRunner 运行器
│   └── routers/             # API 路由
│
├── cli/                     # 命令行工具
│   ├── main.py             # CLI 入口
│   ├── app_cmd.py          # 启动命令
│   ├── init_cmd.py         # 初始化命令
│   ├── channels_cmd.py     # 频道命令
│   ├── cron_cmd.py         # 定时任务命令
│   ├── skills_cmd.py       # Skills 命令
│   └── ...
│
├── config/                  # 配置管理
├── envs/                    # 环境变量加载
├── providers/               # 模型提供商
├── tokenizer/               # 分词器
└── utils/                   # 工具函数
```

---

## 安装

```bash
# 从 PyPI 安装
pip install copaw

# 或从源码安装
pip install -e ".[dev]"
cd console && npm ci && npm run build
copaw app
```

### 快速开始

```bash
# 1. 初始化
copaw init my-assistant

# 2. 配置频道
# 参考: https://copaw.agentscope.io/docs/channels

# 3. 启动
copaw app
```

### 使用 copaw_mgr.py 管理

```bash
# 初始化配置
python3 copaw_mgr.py init

# 启动/停止/重启
python3 copaw_mgr.py start
python3 copaw_mgr.py stop
python3 copaw_mgr.py restart

# 状态/日志
python3 copaw_mgr.py status
python3 copaw_mgr.py log
```

---

## 官方文档

| 主题 | 链接 |
|------|------|
| 官方文档 | [copaw.agentscope.io](https://copaw.agentscope.io/docs/intro) |
| AgentScope | [github.com/agentscope-ai](https://github.com/agentscope-ai) |

---

## License

基于 AgentScope 相关开源协议。

---

<p align="center">
  <sub>Built on AgentScope Runtime · CLI: copaw</sub>
</p>
