# CLI 配置文件设计

> 版本：v1.0 | 更新：2025-02-26

---

## 一、配置文件结构

```yaml
# ~/.cp9/config.yaml

# ==================== 应用配置 ====================
app:
  name: copaw              # 应用名称
  version: "1.0.0"        # 版本
  debug: false             # 调试模式

# ==================== 服务配置 ====================
server:
  host: "0.0.0.0"         # 监听地址
  port: 9090               # 监听端口
  workers: 1                # 工作进程数
  reload: false            # 热重载

# ==================== 日志配置 ====================
logging:
  level: "INFO"            # 日志级别: DEBUG/INFO/WARNING/ERROR
  file: "~/.cp9/logs/app.log"  # 日志文件
  max_size: 10             # 最大文件大小(MB)
  backup: 3                # 备份数量
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== Channel 配置 ====================
channels:
  feishu:
    enabled: true
    app_id: "${FEISHU_APP_ID}"
    app_secret: "${FEISHU_APP_SECRET}"
    bot_prefix: "/ai"
    filters:
      ignore_keywords: ["广告", "spam"]
      ignore_users: []

  dingtalk:
    enabled: false
    app_key: ""
    app_secret: ""
    agent_id: ""

  qq:
    enabled: false
    qq_id: ""
    token: ""

  discord:
    enabled: false
    bot_token: ""

  telegram:
    enabled: false
    bot_token: ""

# ==================== Provider 配置 ====================
providers:
  glm-5:
    enabled: true
    api_key: "${ZHIPU_API_KEY}"
    api_base: "https://open.bigmodel.cn/api/paas/v4"
    model: "glm-5"
    temperature: 0.7
    max_tokens: 4096

  minimax:
    enabled: true
    api_key: "${MINIMAX_API_KEY}"
    api_base: "https://api.minimax.chat/v1"
    model: "MiniMax-M2.5"
    temperature: 0.7

  openai:
    enabled: false
    api_key: ""
    model: "gpt-4"

  anthropic:
    enabled: false
    api_key: ""
    model: "claude-3"

# ==================== Agent 配置 ====================
agents:
  00:
    name: "管理高手"
    enabled: true
    quota: 100
    channels: ["feishu"]

  01:
    name: "学霸"
    enabled: true
    quota: 50
    channels: ["feishu"]
    skills: ["academic_search", "paper_review"]

  02:
    name: "编程高手"
    enabled: true
    quota: 50
    channels: ["feishu"]
    skills: ["code_analysis", "code_generation"]

  03:
    name: "创意青年"
    enabled: true
    quota: 50
    channels: ["feishu"]
    skills: ["text_creative", "image_prompt"]

  04:
    name: "统计学长"
    enabled: true
    quota: 50
    channels: ["feishu"]
    skills: ["data_collect", "report_generate"]

# ==================== Skill 配置 ====================
skills:
  text_creative:
    enabled: true
    provider: "glm-5"

  image_prompt:
    enabled: true
    provider: "glm-5"

  academic_search:
    enabled: true
    provider: "glm-5"

# ==================== Sensor 配置 ====================
sensors:
  dispatch:
    enabled: true
    provider: "glm-5"
    model: "glm-5"

  print:
    enabled: true
    provider: "dall-e-3"

  recorder:
    enabled: false
    provider: "veo-3"

# ==================== Cron 配置 ====================
crons:
  daily_report:
    enabled: true
    agent_id: "04"
    cron: "0 18 * * *"
    message: "生成每日报告"

  dinner_meeting:
    enabled: true
    agent_id: "00"
    cron: "0 21 * * */3"
    message: "晚餐交流会"

# ==================== 记忆配置 ====================
memory:
  short_term:
    max_items: 100
    ttl: 3600

  long_term:
    enabled: true
    vector_store: "pgvector"
    connection:
      host: "localhost"
      port: 5432
      database: "copaw"
      user: "copaw"
      password: ""

# ==================== 安全配置 ====================
security:
  allow_from: []            # 白名单用户，空=允许所有
  enable_rate_limit: true
  rate_limit_count: 60
  rate_limit_window: 60

# ==================== MCP Server 配置 ====================
mcpservers:
  filesystem:
    enabled: false
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]

  github:
    enabled: false
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_TOKEN: ""
```

---

## 二、CLI 命令与配置对应

| 配置项 | CLI 命令 |
|--------|---------|
| server.port | `mgr start -p 9090` (可覆盖) |
| logging.level | `mgr start -v` (DEBUG) |
| channels.* | `set channel feishu {}` |
| providers.* | `set provider glm-5 {}` |
| agents.* | `set agent 00 {}` |

---

## 三、环境变量

配置文件中可使用环境变量：

```yaml
providers:
  glm-5:
    api_key: "${ZHIPU_API_KEY}"  # 自动替换
```

---

*最后更新: 2025-02-26*
