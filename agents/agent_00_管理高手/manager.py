# -*- coding: utf-8 -*-
"""
00 号管理高手 - 核心功能模块

功能：
- Agent 创建
- Agent 初始化
- 状态汇报
- 需求确认
- 协作协调
"""

import json
import os
import shutil
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field

from .requirement import RequirementAnalyzer
from .collaborator import TaskCollaborator
from .reporter import StatusReporter


@dataclass
class AgentSpec:
    """Agent 规格"""
    id: str = ""
    name: str = ""
    role: str = ""
    skills: Dict[str, List[str]] = field(default_factory=lambda: {"required": [], "optional": []})
    quota: str = "中等"
    channels: List[str] = field(default_factory=lambda: ["feishu"])
    permissions: List[str] = field(default_factory=list)


@dataclass
class CreateResult:
    """创建结果"""
    success: bool
    agent_id: str = ""
    message: str = ""
    agent_dir: Path = None


class AgentCreator:
    """Agent 创建器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "~/.copaw/agents")
        self.base_path = self.base_path.expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def create_agent_spec(self, user_requirement: str) -> AgentSpec:
        """
        根据用户需求生成 Agent 规格。
        
        Args:
            user_requirement: 用户需求描述
        
        Returns:
            AgentSpec 规格对象
        """
        # 使用需求分析器
        analyzer = RequirementAnalyzer()
        return analyzer.analyze(user_requirement)
    
    def _generate_agent_id(self) -> str:
        """生成新的 Agent ID"""
        existing = self._get_existing_ids()
        
        # 预定义 Agent (00-04) 保留
        reserved = {"00", "01", "02", "03", "04"}
        
        # 查找最小可用编号
        for i in range(5, 99):
            if f"{i:02d}" not in existing and f"{i:02d}" not in reserved:
                return f"{i:02d}"
        
        return "99"
    
    def _get_existing_ids(self) -> List[str]:
        """获取已存在的 Agent ID"""
        if not self.base_path.exists():
            return []
        
        ids = []
        for d in self.base_path.iterdir():
            if d.is_dir() and d.name.startswith("agent_"):
                # 从目录名提取 ID
                parts = d.name.split("_")
                if len(parts) >= 2:
                    ids.append(parts[1])
        return ids
    
    def create_agent_directory(self, spec: AgentSpec) -> Path:
        """根据规格创建 Agent 目录"""
        agent_id = spec.id or self._generate_agent_id()
        agent_name = spec.name or f"Agent_{agent_id}"
        
        agent_dir = self.base_path / f"agent_{agent_id}_{agent_name}"
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (agent_dir / "memory" / "short_term").mkdir(parents=True, exist_ok=True)
        (agent_dir / "memory" / "long_term").mkdir(parents=True, exist_ok=True)
        (agent_dir / "skills" / "required").mkdir(parents=True, exist_ok=True)
        (agent_dir / "skills" / "optional").mkdir(parents=True, exist_ok=True)
        (agent_dir / "records").mkdir(parents=True, exist_ok=True)
        
        # 创建配置文件
        config = {
            "id": agent_id,
            "name": agent_name,
            "role": spec.role,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "quota": spec.quota,
            "skills": spec.skills,
            "channels": spec.channels,
            "permissions": spec.permissions
        }
        
        config_file = agent_dir / ".meta.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # 创建 system_prompt.md
        self._create_system_prompt(agent_dir, spec)
        
        # 创建 guard.md
        self._create_guard_md(agent_dir, spec)
        
        return agent_dir
    
    def _create_system_prompt(self, agent_dir: Path, spec: AgentSpec):
        """创建 system_prompt.md"""
        content = f"""# {spec.name} - 系统提示词

## 角色

你是 **{spec.name}**，角色：{spec.role}。

## 核心能力

{self._generate_skills_description(spec.skills)}

## 沟通风格

- 专业、清晰、高效
- 使用中文交流

## 注意事项

- 遵守系统规范
- 保护用户隐私
"""
        (agent_dir / "system_prompt.md").write_text(content, encoding="utf-8")
    
    def _create_guard_md(self, agent_dir: Path, spec: AgentSpec):
        """创建 guard.md"""
        content = f"""# {spec.name} - 安全检查清单

## 1. 身份认证

- [x] 验证用户身份
- [x] 检查权限

## 2. 内容安全

- [x] 过滤敏感词
- [x] 版权合规

## 3. 审计日志

- [x] 记录操作历史

---

**最后更新**: {datetime.now().strftime('%Y-%m-%d')}
"""
        (agent_dir / "guard.md").write_text(content, encoding="utf-8")
    
    def _generate_skills_description(self, skills: Dict[str, List[str]]) -> str:
        """生成技能描述"""
        lines = []
        
        required = skills.get("required", [])
        if required:
            lines.append("### 必备技能")
            for skill in required:
                lines.append(f"- {skill}")
        
        optional = skills.get("optional", [])
        if optional:
            lines.append("### 可选技能")
            for skill in optional:
                lines.append(f"- {skill}")
        
        return "\n".join(lines) if lines else "- 通用能力"
    
    def create(self, spec: AgentSpec) -> CreateResult:
        """创建 Agent"""
        try:
            # 生成 ID
            if not spec.id:
                spec.id = self._generate_agent_id()
            
            # 创建目录
            agent_dir = self.create_agent_directory(spec)
            
            return CreateResult(
                success=True,
                agent_id=spec.id,
                message=f"Agent {spec.id} ({spec.name}) 创建成功",
                agent_dir=agent_dir
            )
        except Exception as e:
            return CreateResult(
                success=False,
                message=f"创建失败: {str(e)}"
            )


class AgentManager:
    """Agent 管理器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "~/.copaw/agents")
        self.base_path = self.base_path.expanduser()
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有 Agent"""
        agents = []
        
        # 预定义 Agent
        predefined = {
            "00": {"name": "管理高手", "role": "master", "status": "active"},
            "01": {"name": "学霸", "role": "academic", "status": "active"},
            "02": {"name": "编程高手", "role": "developer", "status": "active"},
            "03": {"name": "创意青年", "role": "creative", "status": "active"},
            "04": {"name": "统计学长", "role": "collector", "status": "active"},
        }
        
        for aid, info in predefined.items():
            agents.append({"id": aid, **info})
        
        # 自定义 Agent
        if self.base_path.exists():
            for d in self.base_path.iterdir():
                if d.is_dir() and d.name.startswith("agent_"):
                    meta_file = d / ".meta.json"
                    if meta_file.exists():
                        with open(meta_file, "r", encoding="utf-8") as f:
                            agents.append(json.load(f))
        
        return sorted(agents, key=lambda x: x.get("id", ""))
    
    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取指定 Agent 状态"""
        agents = self.list_agents()
        for agent in agents:
            if agent.get("id") == agent_id:
                return agent
        return None
    
    def get_all_status(self) -> Dict[str, Any]:
        """获取所有 Agent 状态"""
        agents = self.list_agents()
        
        return {
            "total": len(agents),
            "active": sum(1 for a in agents if a.get("status") == "active"),
            "inactive": sum(1 for a in agents if a.get("status") == "inactive"),
            "agents": agents
        }
    
    def update_agent_status(self, agent_id: str, status: str) -> bool:
        """更新 Agent 状态"""
        # 预定义 Agent 不能修改
        if agent_id in ["00", "01", "02", "03", "04"]:
            return False
        
        if not self.base_path.exists():
            return False
        
        for d in self.base_path.iterdir():
            if d.is_dir() and d.name.startswith(f"agent_{agent_id}_"):
                meta_file = d / ".meta.json"
                if meta_file.exists():
                    with open(meta_file, "r", encoding="utf-8") as f:
                        config = json.load(f)
                    config["status"] = status
                    with open(meta_file, "w", encoding="utf-8") as f:
                        json.dump(config, f, ensure_ascii=False, indent=2)
                    return True
        return False
    
    def delete_agent(self, agent_id: str) -> bool:
        """删除 Agent"""
        # 预定义 Agent 不能删除
        if agent_id in ["00", "01", "02", "03", "04"]:
            return False
        
        if not self.base_path.exists():
            return False
        
        for d in self.base_path.iterdir():
            if d.is_dir() and d.name.startswith(f"agent_{agent_id}_"):
                shutil.rmtree(d)
                return True
        return False


class RequirementClarifier:
    """需求确认器 - 用于反问用户确认需求"""
    
    @staticmethod
    def generate_clarification_questions(requirement: str) -> List[str]:
        """生成需要确认的问题列表"""
        analyzer = RequirementAnalyzer()
        return analyzer.generate_questions(requirement)
    
    @staticmethod
    def format_confirmation(spec: AgentSpec) -> str:
        """格式化确认信息"""
        lines = [
            "📋 **需求确认**",
            "",
            f"**Agent 编号**: {spec.id or '待分配'}",
            f"**Agent 名称**: {spec.name or '待定'}",
            f"**角色定位**: {spec.role or '待定'}",
            f"**资源配额**: {spec.quota}",
            "",
            "**技能配置**:",
        ]
        
        required = spec.skills.get("required", [])
        optional = spec.skills.get("optional", [])
        
        if required:
            lines.append(f"  必备: {', '.join(required)}")
        if optional:
            lines.append(f"  可选: {', '.join(optional)}")
        
        lines.extend([
            "",
            "请确认以上信息是否正确？",
            "回复 **确认** 创建，或 **取消** 放弃。"
        ])
        
        return "\n".join(lines)


class Agent00Service:
    """00 号管理高手服务 - 对外统一接口"""
    
    def __init__(self):
        self.creator = AgentCreator()
        self.manager = AgentManager()
        self.collaborator = TaskCollaborator()
        self.reporter = StatusReporter(self.manager)
    
    async def handle_create_request(self, requirement: str) -> Dict[str, Any]:
        """处理创建请求"""
        # 1. 分析需求
        spec = self.creator.create_agent_spec(requirement)
        
        # 2. 生成确认问题
        questions = RequirementClarifier.generate_clarification_questions(requirement)
        
        if questions:
            return {
                "need_confirm": True,
                "questions": questions,
                "spec": spec
            }
        
        # 3. 直接创建
        result = self.creator.create(spec)
        
        return {
            "need_confirm": False,
            "success": result.success,
            "agent_id": result.agent_id,
            "message": result.message
        }
    
    async def confirm_create(self, spec: AgentSpec) -> CreateResult:
        """确认创建"""
        return self.creator.create(spec)
    
    async def handle_task(self, task: str, context: Dict = None) -> Dict[str, Any]:
        """处理任务"""
        # 复杂任务 -> 协作处理
        if self._is_complex_task(task):
            return await self.collaborator.collaborate(task, context or {})
        
        # 简单任务 -> 路由到对应 Agent
        from app.brain import get_thalamus
        thalamus = get_thalamus()
        agent_id = thalamus.route_message(task)
        
        return {
            "type": "route",
            "agent_id": agent_id,
            "task": task
        }
    
    def _is_complex_task(self, task: str) -> bool:
        """判断是否复杂任务"""
        complex_keywords = ["调研", "开发", "创建", "分析", "报告", "多个"]
        return any(kw in task for kw in complex_keywords)
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        return self.reporter.generate_report()


# ==================== Exports ====================

__all__ = [
    "AgentSpec",
    "CreateResult",
    "AgentCreator",
    "AgentManager",
    "RequirementClarifier",
    "Agent00Service",
]
