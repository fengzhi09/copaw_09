# -*- coding: utf-8 -*-
"""
Status Reporter - 状态汇报器
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class AgentStatus:
    """Agent 状态"""
    id: str
    name: str
    role: str
    status: str
    last_active: str = ""
    tasks_completed: int = 0


@dataclass
class SystemStatus:
    """系统状态"""
    total_agents: int
    active_agents: int
    inactive_agents: int
    uptime: str
    timestamp: str


class StatusReporter:
    """状态汇报器"""
    
    def __init__(self, manager):
        self.manager = manager
        self._start_time = datetime.now()
    
    def generate_report(self) -> Dict[str, Any]:
        """生成状态报告"""
        status = self.manager.get_all_status()
        
        return {
            "system": self._get_system_status(status),
            "agents": self._get_agent_summaries(status),
            "recommendations": self._generate_recommendations(status)
        }
    
    def _get_system_status(self, status: Dict) -> SystemStatus:
        """获取系统状态"""
        uptime = datetime.now() - self._start_time
        uptime_str = self._format_uptime(uptime)
        
        return SystemStatus(
            total_agents=status.get("total", 0),
            active_agents=status.get("active", 0),
            inactive_agents=status.get("inactive", 0),
            uptime=uptime_str,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_agent_summaries(self, status: Dict) -> List[Dict]:
        """获取 Agent 摘要"""
        agents = status.get("agents", [])
        
        summaries = []
        for agent in agents:
            summaries.append({
                "id": agent.get("id", ""),
                "name": agent.get("name", ""),
                "role": agent.get("role", ""),
                "status": agent.get("status", "unknown")
            })
        
        return summaries
    
    def _generate_recommendations(self, status: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        active = status.get("active", 0)
        total = status.get("total", 0)
        
        if total < 5:
            recommendations.append("建议创建更多专业 Agent 以满足不同需求")
        
        if active == 0:
            recommendations.append("当前没有活跃的 Agent，请检查配置")
        
        # 检查预定义 Agent
        agents = status.get("agents", [])
        agent_ids = [a.get("id") for a in agents]
        
        if "01" not in agent_ids:
            recommendations.append("建议配置 01 号学霸 Agent 用于学术调研")
        
        if "02" not in agent_ids:
            recommendations.append("建议配置 02 号编程高手 Agent 用于代码开发")
        
        if not recommendations:
            recommendations.append("系统运行良好")
        
        return recommendations
    
    def _format_uptime(self, duration: timedelta) -> str:
        """格式化运行时间"""
        days = duration.days
        hours = duration.seconds // 3600
        minutes = (duration.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}天 {hours}小时"
        elif hours > 0:
            return f"{hours}小时 {minutes}分钟"
        else:
            return f"{minutes}分钟"
    
    def format_text_report(self) -> str:
        """格式化文本报告"""
        report = self.generate_report()
        sys = report["system"]
        
        lines = [
            "=" * 40,
            "📊 Copaw 系统状态报告",
            "=" * 40,
            "",
            f"⏰ 运行时间: {sys.uptime}",
            f"🕐 更新时间: {sys.timestamp}",
            "",
            "🤖 Agent 统计:",
            f"   总数: {sys.total_agents}",
            f"   活跃: {sys.active_agents}",
            f"   休眠: {sys.inactive_agents}",
            "",
            "📋 Agent 列表:",
        ]
        
        for agent in report["agents"]:
            status_icon = "✅" if agent["status"] == "active" else "❌"
            lines.append(f"   {status_icon} {agent['id']}: {agent['name']} ({agent['role']})")
        
        lines.extend([
            "",
            "💡 建议:",
        ])
        
        for rec in report["recommendations"]:
            lines.append(f"   • {rec}")
        
        lines.append("")
        lines.append("=" * 40)
        
        return "\n".join(lines)
    
    def format_daily_report(self) -> str:
        """格式化日报"""
        report = self.generate_report()
        sys = report["system"]
        
        lines = [
            "📅 每日简报",
            "",
            f"**运行时间**: {sys.uptime}",
            f"**Agent 总数**: {sys.total_agents}",
            f"**活跃 Agent**: {sys.active_agents}",
            "",
            "**Agent 状态**:",
        ]
        
        for agent in report["agents"]:
            status = "🟢" if agent["status"] == "active" else "🔴"
            lines.append(f"{status} {agent['name']}: {agent['role']}")
        
        lines.extend([
            "",
            "**建议**:",
        ])
        
        for rec in report["recommendations"][:3]:
            lines.append(f"- {rec}")
        
        return "\n".join(lines)


__all__ = ["StatusReporter", "AgentStatus", "SystemStatus"]
