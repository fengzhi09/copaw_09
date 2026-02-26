# Copaw 快速验证指南

> 用于验证系统各模块是否正常工作

---

## 1. 验证环境准备

```bash
cd /home/ace09/bots

# 激活环境
source ~/miniforge3/etc/profile.d/conda.sh
conda activate copaw
```

---

## 2. 一键验证脚本

```bash
cd /home/ace09/bots && python -c "
print('='*50)
print('Copaw 系统验证')
print('='*50)

# 1. Brain
from copaw_09.app.brain import Thalamus
t = Thalamus()
intent = t.understand_intent('搜索机器学习论文')
print(f'✅ Brain - 意图: {intent.intent.value}, 路由: {t.route_message(\"搜索论文\")}')

# 2. Gateway
from copaw_09.app.gateway import GatewayAuth, GatewayFilter
auth = GatewayAuth(allow_from=['user1'])
result = auth.authenticate('user1')
print(f'✅ Gateway - 认证: {result.result.value}')

f = GatewayFilter(ignore_keywords=['spam'])
result = f.should_process({'type': 'message', 'content': 'spam'})
print(f'✅ Gateway - 过滤: 关键词 spam 被过滤')

# 3. 00号管理高手
from copaw_09.agents.agent_00_管理高手 import AgentCreator
creator = AgentCreator('/tmp/test_verify')
spec = creator.create_agent_spec('创建一个学术助手')
print(f'✅ 00号 - Agent: {spec.name}, 角色: {spec.role}')

# 4. 路由
from copaw_09.app.router import AgentRouter
r = AgentRouter()
print(f'✅ Router - \"搜索论文\" -> {r.route(\"搜索论文\")}')

# 5. 飞书文档
from copaw_09.app.channels.feishu_document import FeishuDocument
print(f'✅ Feishu - 类存在: {FeishuDocument is not None}')

print('='*50)
print('🎉 核心模块验证通过!')
print('='*50)
"
```

**预期输出：**
```
==================================================
Copaw 系统验证
==================================================
✅ Brain - 意图: search, 路由: 01
✅ Gateway - 认证: pass
✅ Gateway - 过滤: 关键词 spam 被过滤
✅ 00号 - Agent: 创建一个学术助手, 角色: academic
✅ Router - "搜索论文" -> 01
✅ Feishu - 类存在: True
==================================================
🎉 核心模块验证通过!
==================================================
```

---

## 3. 分模块验证

### 3.1 Brain 模块

```bash
python -c "
from copaw_09.app.brain import Thalamus, Prefrontal

# 测试丘脑
thalamus = Thalamus()
intent = thalamus.understand_intent('搜索机器学习论文')
print(f'意图识别: {intent.intent.value}')
print(f'路由结果: {thalamus.route_message(\"搜索论文\")}')

# 测试前额叶
prefrontal = Prefrontal(primary_model='glm-5')
print(f'前额叶模型: {prefrontal.primary_model}')
"
```

---

### 3.2 Gateway 模块

```bash
python -c "
from copaw_09.app.gateway import GatewayAuth, GatewayFilter

# 测试认证
auth = GatewayAuth(allow_from=['user1', 'user2'])
result = auth.authenticate('user1')
print(f'认证结果: {result.result.value}')

# 测试过滤
filter = GatewayFilter(ignore_keywords=['spam'])
result = filter.should_process({'type': 'message', 'content': 'spam'})
print(f'过滤结果: {result}')
"
```

---

### 3.3 00号管理高手

```bash
python -c "
from copaw_09.agents.agent_00_管理高手 import AgentCreator, AgentManager

# 测试需求分析
creator = AgentCreator('/tmp/test_agents')
spec = creator.create_agent_spec('创建一个学术助手')
print(f'Agent名称: {spec.name}')
print(f'角色: {spec.role}')
print(f'技能: {spec.skills}')

# 测试创建
result = creator.create(spec)
print(f'创建结果: {result.success}')
print(f'消息: {result.message}')

# 测试状态管理
manager = AgentManager('/tmp/test_agents')
status = manager.get_all_status()
print(f'Agent总数: {status[\"total\"]}')
"
```

---

### 3.4 飞书文档

```bash
python -c "
from copaw_09.app.channels.feishu_document import FeishuDocument

print(f'类存在: {FeishuDocument is not None}')
print(f'上传方法: {hasattr(FeishuDocument, \"upload_file\")}')
print(f'下载方法: {hasattr(FeishuDocument, \"download_file\")}')
print(f'创建文档: {hasattr(FeishuDocument, \"create_document\")}')
print(f'知识库: {hasattr(FeishuDocument, \"list_spaces\")}')
"
```

---

### 3.5 路由模块

```bash
python -c "
from copaw_09.app.router import AgentRouter

router = AgentRouter()
tests = [
    ('搜索论文', '01'),
    ('写代码', '02'),
    ('创意文案', '03'),
    ('成本统计', '04'),
    ('创建Agent', '00'),
    ('你好', '00'),
]

for msg, expected in tests:
    result = router.route(msg)
    status = '✅' if result == expected else '❌'
    print(f'{status} \"{msg}\" -> {result}')
"
```

---

## 4. 清理测试数据

```bash
rm -rf /tmp/test_verify
rm -rf /tmp/test_agents
echo "✅ 清理完成"
```

---

*最后更新: 2025-02-26*
