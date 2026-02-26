# CLI 设计反思与改进

## 一、当前问题

### 1.1 命令风格问题

| 用户期望 | 当前实现 | 问题 |
|---------|---------|------|
| `cp9 mgr start` | `python cli.py mgr start` | 需要 `python` 前缀 |
| `cp9 get agent 00` | `python cli.py get agent 00` | 参数解析可能有问题 |
| `cp9 test channel feishu send` | 部分实现 | 子命令不完整 |

### 1.2 功能缺失

| 功能 | 状态 | 说明 |
|------|------|------|
| 可执行脚本 | ❌ | 需要添加 `#!/usr/bin/env python` 并加执行权限 |
| Shell Alias | ❌ | 需要提供 alias 配置 |
| 配置文件自动创建 | ❌ | 首次运行应自动创建 |
| 详细错误处理 | ❌ | 错误信息不够友好 |
| 日志控制 | ❌ | 无日志级别控制 |
| 帮助信息 | ⚠️ | 部分命令缺少详细帮助 |

### 1.3 test 命令不完整

```
# 用户期望
cp9 test channel feishu send -msg ""
cp9 test channel feishu recv -msg ""
cp9 test provider minimax -model 'minimax-m2.5' -msg "hello"
cp9 test sensor dispatch -msg "" -file ""
cp9 test skill feishu-doc -model '{}' -env '{}' -msg "" -file ""
cp9 test cron del|add -agent -id 00 -msg ""
```

当前只实现了基础测试，缺少：
- channel recv 测试
- provider 实际 API 调用
- sensor 文件测试
- skill 完整测试
- cron 增删改查

## 二、需要补充

### 2.1 可执行脚本

```bash
#!/usr/bin/env python
# 添加到 cli.py 开头
if __name__ == "__main__":
    main()
```

### 2.2 完整 test 命令实现

```python
# test channel recv
# test provider 实际调用
# test sensor 文件处理
# test skill 技能执行
# test cron 任务管理
```

### 2.3 错误处理

- 配置文件不存在 → 自动创建或提示
- API 调用失败 → 详细错误信息
- 权限问题 → 友好提示

### 2.4 日志控制

```bash
cp9 mgr start -v  # verbose
cp9 mgr start -vv  # debug
```

## 三、改进计划

### P0 - 必须

1. **可执行脚本** - 添加 `#!/usr/bin/env python` + 执行权限
2. **cp9 别名** - 提供 shell 配置
3. **test channel** - 完善 recv/send
4. **test provider** - 实际 API 调用

### P1 - 重要

5. **错误处理** - 友好错误信息
6. **自动补全** - shell completion
7. **日志控制** - -v/-vv 选项

### P2 - 优化

8. **配置文件模板** - 完整默认配置
9. **历史命令** - 命令历史记录
10. **交互模式** - 类似 `ipython`

---

*反思时间: 2025-02-26*
