# -*- coding: utf-8 -*-
"""
Requirement Analyzer - 需求分析器
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field


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


class RequirementAnalyzer:
    """需求分析器"""
    
    # 关键词到角色的映射
    ROLE_KEYWORDS = {
        "academic": ["学术", "论文", "研究", "调研", "搜索", "google", "pubmed"],
        "developer": ["代码", "编程", "开发", "bug", "报错", "github", "技术"],
        "creative": ["创意", "写作", "文案", "画", "视频", "小红书", "抖音"],
        "collector": ["统计", "报表", "成本", "复盘", "总结", "知识"],
        "master": ["管理", "创建", "配置", "系统", "agent"],
    }
    
    # 角色到技能的映射
    ROLE_SKILLS = {
        "academic": {
            "required": ["academic_search", "paper_review", "literature_summary"],
            "optional": ["data_analysis", "translation"]
        },
        "developer": {
            "required": ["code_analysis", "code_generation", "bug_fix"],
            "optional": ["code_review", "security_check"]
        },
        "creative": {
            "required": ["text_creative", "image_prompt"],
            "optional": ["video_script", "copywriting"]
        },
        "collector": {
            "required": ["data_collect", "report_generate"],
            "optional": ["visualization", "trend_analysis"]
        },
        "master": {
            "required": ["agent_management", "task_coordination"],
            "optional": ["status_report", "resource_allocation"]
        },
    }
    
    def analyze(self, requirement: str) -> AgentSpec:
        """
        分析需求并生成规格。
        
        Args:
            requirement: 用户需求描述
        
        Returns:
            AgentSpec 规格对象
        """
        req_lower = requirement.lower()
        
        # 确定角色
        role = self._detect_role(req_lower)
        
        # 获取技能
        skills = self.ROLE_SKILLS.get(role, {"required": [], "optional": []})
        
        # 确定名称
        name = self._generate_name(role, requirement)
        
        # 确定配额
        quota = self._detect_quota(requirement)
        
        return AgentSpec(
            id="",  # 由 creator 生成
            name=name,
            role=role,
            skills=skills,
            quota=quota,
            channels=["feishu"],
            permissions=[]
        )
    
    def _detect_role(self, requirement: str) -> str:
        """检测角色"""
        scores = {}
        
        for role, keywords in self.ROLE_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in requirement)
            scores[role] = score
        
        if not scores or max(scores.values()) == 0:
            return "general"
        
        return max(scores, key=scores.get)
    
    def _generate_name(self, role: str, requirement: str) -> str:
        """生成名称"""
        name_map = {
            "academic": "学术助手",
            "developer": "编程助手",
            "creative": "创意助手",
            "collector": "统计助手",
            "master": "管理助手",
            "general": "通用助手"
        }
        
        # 尝试从需求中提取名称
        for word in ["助手", "高手", "专家", "小助手"]:
            if word in requirement:
                return requirement.split(word)[0] + word
        
        return name_map.get(role, "助手")
    
    def _detect_quota(self, requirement: str) -> str:
        """检测配额需求"""
        if any(w in requirement for w in ["大量", "高频", "深度", "挑战"]):
            return "高"
        elif any(w in requirement for w in ["少量", "轻量", "简单"]):
            return "低"
        return "中等"
    
    def generate_questions(self, requirement: str) -> List[str]:
        """生成确认问题"""
        questions = []
        req_lower = requirement.lower()
        
        # 角色不明确
        if not any(role in req_lower for role in ["助手", "高手", "专家"]):
            questions.append("请问这个 Agent 的角色定位是什么？")
        
        # 技能不明确
        if "技能" not in requirement and "能力" not in requirement:
            if not questions:  # 只有一个问题时不需要再问
                questions.append("需要具备哪些具体技能？")
        
        # 配额不明确
        if "配额" not in requirement and "资源" not in requirement:
            if not questions:
                questions.append("资源配额需求是什么？（轻量/一般/中等）")
        
        return questions[:2]  # 最多2个问题


__all__ = ["RequirementAnalyzer"]
