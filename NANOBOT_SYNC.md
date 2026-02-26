# Copaw 与 nanobot 功能对比

> 基于 https://github.com/HKUDS/nanobot 分析

---

## nanobot 核心功能

### 1. Agent 核心 (agent/)
| 功能 | nanobot | copaw_09 | 状态 |
|------|---------|-----------|------|
| Agent Loop | ✅ loop.py | ⚠️ 待完善 | 需要 |
| Context Builder | ✅ context.py | ⚠️ 待完善 | 需要 |
| Memory | ✅ memory.py | ⚠️ 待完善 | 需要 |
| Skills | ✅ skills.py | ⚠️ 待完善 | 需要 |
| Subagent | ✅ subagent.py | ❌ 无 | 需要 |
| Tools | ✅ tools/ | ⚠️ 部分 | 完善 |

### 2. Channels (channels/)
| 渠道 | nanobot | copaw_09 | 状态 |
|------|---------|-----------|------|
| 飞书 | ✅ | ✅ | ✅ 完成 |
| 钉钉 | ✅ | ✅ | ✅ 完成 |
| QQ | ✅ | ✅ | ✅ 完成 |
| Discord | ✅ | ✅ | ✅ 完成 |
| Telegram | ✅ | ✅ | ✅ 完成 |
| WhatsApp | ✅ | ❌ 无 | 待添加 |

### 3. Providers (LLM)
| 提供商 | nanobot | copaw_09 | 状态 |
|--------|---------|-----------|------|
| OpenAI | ✅ | ✅ | ✅ |
| Anthropic | ✅ | ✅ | ✅ |
| OpenRouter | ✅ | ⚠️ | 完善 |
| Local (vLLM) | ✅ | ❌ 无 | 待添加 |
| Ollama | ✅ | ❌ 无 | 待添加 |

### 4. Cron 定时任务
| 功能 | nanobot | copaw_09 | 状态 |
|------|---------|-----------|------|
| 定时任务 | ✅ cron add | ✅ | ✅ 完成 |
| 每日复盘 | ✅ | ✅ | ✅ |
| 晚餐交流会 | ✅ | ✅ | ✅ |

### 5. Heartbeat 主动唤醒
| 功能 | nanobot | copaw_09 | 状态 |
|------|---------|-----------|------|
| 定时检查 | ✅ | ⚠️ | 待完善 |

### 6. Session 会话管理
| 功能 | nanobot | copaw_09 | 状态 |
|------|---------|-----------|------|
| 会话存储 | ✅ | ⚠️ | 待完善 |
| 历史记录 | ✅ | ⚠️ | 待完善 |

### 7. CLI 命令
| 命令 | nanobot | copaw_09 | 状态 |
|------|---------|-----------|------|
| nanobot onboard | ✅ | ❌ 无 | 需要 |
| nanobot agent | ✅ | ⚠️ | 需要 |
| nanobot gateway | ✅ | ❌ 无 | 需要 |
| nanobot status | ✅ | ⚠️ | 需要 |
| nanobot cron | ✅ | ✅ | ✅ |
| nanobot channels | ✅ | ⚠️ | 需要 |

---

## 需要同步的功能

### P0 - 核心功能
1. **Agent Loop** - 完善 agent 执行循环
2. **Context Builder** - 完善上下文构建
3. **Memory** - 完善记忆系统

### P1 - 重要功能
4. **Session** - 会话管理
5. **CLI 完善** - 命令行工具

### P2 - 增强功能
6. **更多 Channels** - WhatsApp 等
7. **更多 Providers** - vLLM, Ollama

---

## nanobot 命令参考

```bash
# 初始化
nanobot onboard

# Agent 对话
nanobot agent -m "你好"
nanobot agent  # 交互模式

# Gateway
nanobot gateway

# 状态
nanobot status

# 定时任务
nanobot cron add --name "daily" --message "Good morning!" --cron "0 9 * * *"
nanobot cron list

# Channels
nanobot channels login  # 扫码登录
nanobot channels status

# Providers
nanobot provider login openai-codex
```

---

*最后更新: 2025-02-26*
