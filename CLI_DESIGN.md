# Copaw CLI 命令格式设计 (对比分析版)

> 对比 nanobot, openclaw 后优化

---

## 一、命令结构对比

| nanobot | openclaw | copaw (设计) |
|---------|----------|--------------|
| `nanobot onboard` | `openclaw onboard` | `cp9 init` |
| `nanobot agent -m` | `openclaw agent --message` | `cp9 test agent -i -m` |
| `nanobot gateway` | `openclaw gateway` | `cp9 start` |
| `nanobot status` | - | `cp9 status` |
| `nanobot cron add` | - | `cp9 test cron add` |
| `nanobot provider login` | - | `cp9 config set provider` |
| `nanobot channels login` | - | `cp9 config set channel` |

---

## 二、最终命令结构

### 2.1 服务管理

| 命令 | 说明 | 对比 |
|------|------|------|
| `cp9 start` | 启动服务 | nanobot gateway |
| `cp9 start -d` | 后台运行 | - |
| `cp9 stop` | 停止服务 | - |
| `cp9 status` | 服务状态 | nanobot status |
| `cp9 restart` | 重启服务 | - |
| `cp9 version` | 版本信息 | openclaw --version |
| `cp9 upgrade` | 升级版本 | openclaw (upgrading guide) |
| `cp9 doctor` | 诊断检查 | openclaw doctor |

### 2.2 日志

| 命令 | 说明 |
|------|------|
| `cp9 logs` | 查看日志 (默认最后100行) |
| `cp9 logs -f` | 实时跟踪日志 |
| `cp9 logs -n 500` | 查看最后500行 |

### 2.3 配置管理

| 命令 | 说明 | 对比 |
|------|------|------|
| `cp9 init` | 初始化配置 | nanobot onboard |
| `cp9 config show` | 显示配置 | - |
| `cp9 config validate` | 验证配置 | - |
| `cp9 get agent -i 00` | 获取配置 | - |
| `cp9 set agent -i 00 '{}'` | 设置配置 | nanobot provider login |
| `cp9 list agents` | 列出资源 | nanobot cron list |

### 2.4 测试命令

| 命令 | 说明 |
|------|------|
| `cp9 test agent -i 00 -m "消息"` | 测试 Agent |
| `cp9 test channel -c feishu -m "消息"` | 测试 Channel |
| `cp9 test channel -c feishu --recv` | 接收测试 |
| `cp9 test provider -p glm-5 -m "消息"` | 测试 Provider |
| `cp9 test sensor -s dispatch -m "消息"` | 测试 Sensor |
| `cp9 test skill -s feishu-doc -m "消息"` | 测试 Skill |
| `cp9 test cron list` | 列出 Cron |
| `cp9 test cron add -i daily -a 04 -m "日报"` | 添加 Cron |
| `cp9 test cron del -i daily` | 删除 Cron |

---

## 三、选项规范

### 3.1 通用选项

| 短选项 | 全选项 | 说明 |
|--------|--------|------|
| -c | --config | 配置文件 |
| -h | --help | 帮助 |
| -v | --verbose | 详细输出 |
| -j | --json | JSON 输出 |
| -d | --daemon | 后台运行 |

### 3.2 资源选项

| 短选项 | 全选项 | 适用命令 |
|--------|--------|----------|
| -i | --id | get/set/test |
| -m | --msg | test |
| -f | --file | test channel/sensor |
| -p | --provider | test provider |
| -s | --sensor | test sensor/skill |
| -a | --agent | test cron |
| -n | --lines | logs |
| -t | --cron | test cron |

---

## 四、输出格式

### 4.1 表格 (list)

```
┌────┬───────────┬────────┐
│ ID │ Name      │ Status │
├────┼───────────┼────────┤
│ 00 │ 管理高手  │ active │
│ 01 │ 学霸     │ active │
└────┴───────────┴────────┘
```

### 4.2 JSON (-j)

```bash
cp9 get agent -i 00 -j
```

```json
{
  "id": "00",
  "name": "管理高手",
  "enabled": true
}
```

### 4.3 详细 (-v)

```
cp9 test agent -i 00 -m "搜索论文" -v
[10:30:00] 🔄 加载配置...
[10:30:01] 📡 路由: Agent 01
[10:30:01] 🧠 意图: search (0.85)
[10:30:02] ✅ 完成

意图: search
置信度: 0.85
```

---

## 五、快速参考

```bash
# 启动/停止
cp9 start              # 启动
cp9 start -d           # 后台运行
cp9 stop               # 停止
cp9 status             # 状态

# 日志
cp9 logs               # 查看日志
cp9 logs -f            # 实时跟踪
cp9 logs -n 500       # 最后500行

# 配置
cp9 init               # 初始化
cp9 list agents        # 列出
cp9 get agent -i 00   # 获取

# 测试
cp9 test agent -i 00 -m "搜索论文"
cp9 test channel -c feishu -m "Hello"

# 其他
cp9 version            # 版本
cp9 upgrade           # 升级
cp9 doctor            # 诊断
```

---

## 六、与 nanobot/openclaw 对比

| 特性 | nanobot | openclaw | copaw |
|------|---------|----------|-------|
| 初始化 | onboard | onboard | init |
| 交互 | agent | agent | test agent |
| 服务 | gateway | gateway | start |
| 状态 | status | - | status |
| 日志 | - | - | logs ✓ |
| 版本 | - | --version | version ✓ |
| 升级 | - | (guide) | upgrade ✓ |
| 诊断 | - | doctor | doctor ✓ |
| 配置 | - | config | config ✓ |

---

*最后更新: 2025-02-26*
