# Known Issues

记录已知的外部依赖问题及应对措施。

---

## FsCompactor 返回 None (2025-07-12)

### 问题描述
`reme-ai` 包的 `FsCompactor.call()` 方法在某些情况下返回 `None`，导致 `'NoneType' object has no attribute 'content'` 错误。

### 影响范围
- `MemoryManager.compact_memory()` 方法
- 手动 `/compact` 命令
- 自动 memory compaction 触发

### 应对措施
在 `agents/memory/memory_manager.py` 的 `compact_memory` 方法中添加了空值检查：
- 如果 `super().compact()` 返回 `None`，则使用之前的 summary 或空字符串
- 记录 warning 日志

### 后续
- 观察是否还有此问题
- 如频繁发生，考虑向 reme-ai 社区报告 issue
