# CoPaw Roadmap 🗺️

> CoPaw 的未来发展规划

---

## 愿景

将 CoPaw 打造成一个**可扩展的个人 AI 助理平台**，支持从单用户到企业团队的各种场景。

---

## 版本规划

### Phase 1: 基础能力完善 (v0.1.x)
- [x] 多通道支持（钉钉、飞书、QQ、Discord、iMessage）
- [x] 内置 Skills（PDF、Office、新闻、文件阅读、邮件）
- [x] 定时任务 (cron)
- [x] 心跳 (Heartbeat)
- [x] Web 控制台
- [ ] 完善文档和示例

### Phase 2: 能力扩展 (v0.2.x)

#### MCP 支持
- [ ] MCP 协议兼容层
- [ ] MCP 工具注册与调用
- [ ] MCP Server 连接管理

#### 外置 Skills
- [ ] ClawHub Skills 集成
  - [ ] minimax-mcp
  - [ ] feishu-bridge
  - [ ] feishu-doc / feishu-sheets / feishu-bitable
  - [ ] 更多飞书/语音相关 Skills
- [ ] Skills 商店发现与安装
- [ ] 自定义 Skills 仓库支持

#### 记忆系统增强
- [ ] 向量记忆存储
- [ ] 语义搜索
- [ ] 长期记忆与短期记忆分层

### Phase 3: 多 Agent 架构 (v0.3.x)

#### 多 Agent 协作
- [ ] Agent 编排与工作流
- [ ] Agent 间通信协议
- [ ] 任务分发与聚合
- [ ] Agent 模板市场

#### 团队协作
- [ ] 多用户支持
- [ ] 权限管理
- [ ] 共享 Skills 与知识库

### Phase 4: 企业版 (v0.4.x)

#### 企业级功能
- [ ] SSO / LDAP 集成
- [ ] 企业级权限模型
- [ ] 审计日志
- [ ] 高可用部署
- [ ] 监控与告警

#### 商业化支持
- [ ] Credit Plan（基于积分的计划体系）
- [ ] 多租户支持
- [ ] SLA 保障

### Phase 5: 生态扩展 (v0.5.x+)

#### 更多渠道
- [ ] 微信企业版
- [ ] Slack
- [ ] Telegram
- [ ] 邮件协议增强

#### 更多模型
- [ ] OpenAI API 兼容
- [ ] Anthropic Claude
- [ ] 国产大模型（通义千问、文心一言、智谱清言）
- [ ] 本地模型 (Ollama, LM Studio)

#### 开发者生态
- [ ] SDK / API 文档
- [ ] 插件市场
- [ ] 社区模板分享
- [ ] VSCode 插件

---

## 功能优先级

| 优先级 | 功能 | 预计版本 |
|--------|------|----------|
| P0 | MCP 支持 | v0.2.0 |
| P0 | ClawHub Skills 集成 | v0.2.0 |
| P1 | 向量记忆 | v0.2.1 |
| P1 | 多 Agent 协作 | v0.3.0 |
| P2 | 企业版基础 | v0.4.0 |
| P2 | Credit Plan | v0.4.1 |
| P3 | 更多渠道 | v0.5.x |
| P3 | 更多模型 | v0.5.x |

---

## 贡献指南

欢迎提交 Issue 和 PR！请参考 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## 更新日志

See [CHANGELOG.md](./CHANGELOG.md)
