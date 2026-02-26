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
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class AgentCreator:
    """Agent 创建器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "~/.copaw/agents")
        self.base_path = self.base_path.expanduser()
    
    def create_agent_spec(self, user_requirement: str) -> Dict[str, Any]:
        """
        根据用户需求生成 Agent 规格。
        
        返回规格字典，包含：
        - id: Agent 编号
        - name: Agent 名称
        - role: 角色定位
        - skills: 技能配置
        - quota: 资源配额
        """
        # 简单的关键词匹配生成规格
        # TODO: 使用 LLM 智能分析
        
        requirement_lower = user_requirement.lower()
        
        spec = {
            "id": self._generate_agent_id(),
            "name": "",
            "role": "",
            "skills": {
                "required": [],
                "optional": []
            },
            "quota": "中等",
            "channels": ["feishu"],
            "permissions": []
        }
        
        # 关键词匹配
        if any(w in requirement_lower for w in ["学术", "论文", "研究", "调研"]):
            spec["name"] = "学术助手"
            spec["role"] = "academic"
            spec["skills"]["required"] = ["academic_search", "paper_review"]
            
        elif any(w in requirement_lower for w in ["代码", "编程", "开发", "bug"]):
            spec["name"] = "编程助手"
            spec["role"] = "developer"
            spec["skills"]["required"] = ["code_analysis", "code_generation"]
            
        elif any(w in requirement_lower for w in ["创意", "写作", "文案", "画"]):
            spec["name"] = "创意助手"
            spec["role"] = "creative"
            spec["skills"]["required"] = ["text_creative", "image_prompt"]
            
        else:
            spec["name"] = "通用助手"
            spec["role"] = "general"
            spec["skills"]["required"] = []
        
        return spec
    
    def _generate_agent_id(self) -> str:
        """生成新的 Agent ID"""
        existing = self._get_existing_ids()
        
        # 查找最小可用编号
        for i in range(5, 99):
            if f"{i:02d}" not in existing:
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
    
    def create_agent_directory(self, spec: Dict[str, Any]) -> Path:
        """根据规格创建 Agent 目录"""
        agent_id = spec["id"]
        agent_name = spec.get("name", f"Agent_{agent_id}")
        
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
            "role": spec.get("role", "general"),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "quota": spec.get("quota", "中等"),
            "skills": spec.get("skills", {}),
            "channels": spec.get("channels", ["feishu"]),
            "permissions": spec.get("permissions", [])
        }
        
        config_file = agent_dir / ".meta.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return agent_dir


class AgentManager:
    """Agent 管理器"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or "~/.copaw/agents")
        self.base_path = self.base_path.expanduser()
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有 Agent"""
        agents = []
        
        if not self.base_path.exists():
            return agents
        
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
        
        status = {
            "total": len(agents),
            "active": sum(1 for a in agents if a.get("status") == "active"),
            "inactive": sum(1 for a in agents if a.get("status") == "inactive"),
            "agents": agents
        }
        
        return status


class RequirementClarifier:
    """需求确认器 - 用于反问用户确认需求"""
    
    @staticmethod
    def generate_clarification_questions(requirement: str) -> List[str]:
        """生成需要确认的问题列表"""
        questions = []
        
        requirement_lower = requirement.lower()
        
        # 检查是否需要确认角色
        if not any(w in requirement_lower for w in ["助手", "高手", "专家", "学霸", "编程", "创意"]):
            questions.append("请问这个 Agent 的角色定位是什么？（如：学术助手、编程高手、创意专家等）")
        
        # 检查是否需要确认技能
        if "技能" not in requirement and "能力" not in requirement:
            questions.append("请问需要具备哪些技能或能力？")
        
        # 检查是否需要确认资源配额
        if "配额" not in requirement and "credit" not in requirement.lower():
            questions.append("请问资源配额需求是什么？（轻量/一般/中等/挑战/深度）")
        
        # 检查是否需要确认沟通渠道
        if "渠道" not in requirement and "飞书" not in requirement and "钉钉" not in requirement:
            questions.append("需要通过哪些渠道与用户沟通？（飞书/钉钉/QQ等）")
        
        return questions[:3]  # 最多返回3个问题
    
    @staticmethod
    def format_confirmation(spec: Dict[str, Any]) -> str:
        """格式化确认信息"""
        lines = [
            "📋 **需求确认**",
            "",
            f"**Agent 编号**: {spec.get('id', '待分配')}",
            f"**Agent 名称**: {spec.get('name', '待定')}",
            f"**角色定位**: {spec.get('role', '待定')}",
            f"**资源配额**: {spec.get('quota', '中等')}",
            "",
            "**技能配置**:",
        ]
        
        skills = spec.get("skills", {})
        required = skills.get("required", [])
        optional = skills.get("optional", [])
        
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


# ==================== Exports ====================

__all__ = [
    "AgentCreator",
    "AgentManager", 
    "RequirementClarifier",
]
