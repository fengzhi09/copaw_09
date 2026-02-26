# Test 命令功能分析

## 一、用户期望 vs 当前实现

### 1. test agent

| 用户期望 | 当前实现 | 状态 |
|---------|---------|------|
| `-id 00` | `--agent-id 00` | ✅ 等效 |
| `-msg ""` | `--msg "你好"` | ✅ 已实现 |

### 2. test channel

| 用户期望 | 当前实现 | 状态 |
|---------|---------|------|
| `feishu send -msg ""` | ✅ 部分 | 需完善 |
| `feishu recv -msg ""` | ❌ 缺失 | 需开发 |
| `-file ""` | ❌ 缺失 | 需开发 |

### 3. test provider

| 用户期望 | 当前实现 | 状态 |
|---------|---------|------|
| `minimax -model 'minimax-m2.5'` | ⚠️ 模拟 | 需实际调用 |
| `-msg "hello"` | ⚠️ 模拟 | 需实际调用 |
| 其他 provider (glm/openai) | ❌ 缺失 | 需添加 |

### 4. test sensor

| 用户期望 | 当前实现 | 状态 |
|---------|---------|------|
| `dispatch -msg ""` | ✅ 已实现 |
| `-file ""` | ❌ 缺失 | 需开发 |

### 5. test skill

| 用户期望 | 当前实现 | 状态 |
|---------|---------|------|
| `feishu-doc -model '{}'` | ⚠️ 模拟 | 需实际调用 |
| `-env '{}'` | ❌ 缺失 | 需开发 |
| `-msg ""` | ❌ 缺失 | 需开发 |
| `-file ""` | ❌ 缺失 | 需开发 |

### 6. test cron

| 用户期望 | 当前实现 | 状态 |
|---------|---------|------|
| `del` | ⚠️ 模拟 | 需实际删除 |
| `add -agent -id 00 -msg ""` | ⚠️ 模拟 | 需实际添加 |
| `list` | ❌ 缺失 | 需开发 |

---

## 二、缺失功能清单

### P0 - 必须

1. **test channel recv** - 接收消息测试
2. **test channel -file** - 文件传输测试
3. **test provider 实际调用** - 真实 API 调用
4. **test sensor -file** - 文件传感器测试

### P1 - 重要

5. **test skill 实际调用** - 真实技能执行
6. **test skill -env** - 环境变量配置
7. **test cron list** - 列出定时任务
8. **test cron add/del** - 实际增删

### P2 - 增强

9. **test provider 输出 token 统计** - 显示消耗
10. **test skill 输出执行时间** - 性能监控
11. **test channel 多消息** - 批量测试
12. **test agent 上下文** - 多轮对话测试

---

## 三、测试命令使用示例

```bash
# Agent 测试
cp9 test agent -id 00 -msg "搜索机器学习论文"
cp9 test agent -id 01 -msg "帮我写个Python排序算法"

# Channel 测试
cp9 test channel feishu send -msg "Hello World"
cp9 test channel feishu recv -msg "收到请回复"
cp9 test channel feishu send -file "/tmp/test.png"

# Provider 测试
cp9 test provider minimax -model 'MiniMax-M2.5' -msg "你好"
cp9 test provider glm -model 'glm-5' -msg "解释一下什么是机器学习"

# Sensor 测试
cp9 test sensor dispatch -msg "搜索论文"
cp9 test sensor print -msg "生成一张图片"

# Skill 测试
cp9 test skill feishu-doc -msg "读取文档" -env '{"doc_id": "xxx"}'
cp9 test skill image_gen -msg "生成科技感图片"

# Cron 测试
cp9 test cron list
cp9 test cron add -agent 04 -msg "每日报告" -cron "0 18 * * *"
cp9 test cron del -id "daily_report"
```

---

*最后更新: 2025-02-26*
