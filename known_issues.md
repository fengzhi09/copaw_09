# CoPaw 09 已知问题列表

## 定时任务默认禁用

- **问题描述**: 预定义的定时任务（daily_report, dinner_meeting）默认启用
- **状态**: ✅ 已解决 - 修改为 `enabled=False`
- **文件**: `app/crons/tasks.py`

---

## API 路由被静态文件覆盖（已解决）

- **问题描述**: 前端静态资源（SPA fallback）覆盖 API 路由
- **状态**: ✅ 已解决 - 注释掉静态资源挂载代码，待前端开发完成后再启用
- **文件**: `app/_app.py`

---

## MiniMax API 地址

- **问题描述**: 之前使用了错误的 API 地址 `api.minimax.com`
- **状态**: ✅ 已解决 - 使用正确的 `api.minimaxi.com`

---

## FsCompactor 返回 None

- **问题描述**: `FsCompactor.compress_files` 方法未正确返回值
- **状态**: ✅ 已解决

---

## CLI 导入问题

- **问题描述**: 多个模块导入失败（agent, channel, provider, sensor, skill, cron）
- **状态**: ✅ 已解决 - 统一使用 cp9_cli.py
