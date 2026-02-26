# -*- coding: utf-8 -*-
"""
Web Admin API - Web管理端路由

提供对话式管理接口：
- 00号管理高手：系统管理
- 04号统计学长：数据统计
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ==================== Request Models ====================

class ChatRequest(BaseModel):
    """对话请求"""
    agent_id: str  # 00 或 04
    message: str
    user_id: str = "admin"


class AgentStatusRequest(BaseModel):
    """Agent状态请求"""
    agent_id: Optional[str] = None


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    key: str
    value: Any


# ==================== Response Models ====================

class ChatResponse(BaseModel):
    """对话响应"""
    agent_id: str
    message: str
    timestamp: str


class AgentStatusResponse(BaseModel):
    """Agent状态响应"""
    agents: List[Dict[str, Any]]
    total: int
    active: int


class CostReportResponse(BaseModel):
    """成本报表响应"""
    period: str
    total_cost: float
    by_agent: Dict[str, float]
    by_model: Dict[str, float]


# ==================== Admin APIs ====================

@router.post("/chat", response_model=ChatResponse)
async def admin_chat(request: ChatRequest):
    """
    对话式管理接口
    
    支持与 00号(管理高手) 或 04号(统计学长) 对话
    """
    if request.agent_id not in ["00", "04"]:
        raise HTTPException(
            status_code=400,
            detail="只支持 00号(管理高手) 或 04号(统计学长)"
        )
    
    # TODO: 集成实际的 Agent 对话逻辑
    return ChatResponse(
        agent_id=request.agent_id,
        message=f"[模拟响应] 收到消息: {request.message}",
        timestamp="2025-02-26T10:00:00Z"
    )


@router.get("/agents", response_model=AgentStatusResponse)
async def list_agents(agent_id: Optional[str] = None):
    """获取 Agent 状态"""
    # TODO: 从数据库或注册表获取实际状态
    
    agents = [
        {"id": "00", "name": "管理高手", "role": "master", "status": "active"},
        {"id": "01", "name": "学霸", "role": "academic", "status": "active"},
        {"id": "02", "name": "编程高手", "role": "developer", "status": "active"},
        {"id": "03", "name": "创意青年", "role": "creative", "status": "active"},
        {"id": "04", "name": "统计学长", "role": "collector", "status": "active"},
    ]
    
    if agent_id:
        agents = [a for a in agents if a["id"] == agent_id]
    
    return AgentStatusResponse(
        agents=agents,
        total=len(agents),
        active=sum(1 for a in agents if a["status"] == "active")
    )


@router.get("/cost", response_model=CostReportResponse)
async def get_cost_report(period: str = "2025-02"):
    """获取成本报表"""
    # TODO: 从数据库获取实际成本数据
    
    return CostReportResponse(
        period=period,
        total_cost=173.50,
        by_agent={
            "00": 12.30,
            "01": 45.20,
            "02": 68.00,
            "03": 28.00,
            "04": 20.00
        },
        by_model={
            "glm-5": 128.50,
            "nano-banana-pro": 45.00
        }
    )


@router.post("/config")
async def update_config(request: ConfigUpdateRequest):
    """更新配置"""
    # TODO: 实现实际配置更新逻辑
    
    return {
        "success": True,
        "key": request.key,
        "value": request.value
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "version": "1.2.0",
        "agents_loaded": 5
    }


__all__ = ["router"]
