# -*- coding: utf-8 -*-
"""
Predefined Cron Tasks for cp9

定时任务定义：
- daily_report: 每日 18:00 日报
- dinner_meeting: 每3天 21:00 晚餐交流会
- health_check: 每6小时健康检查
"""

from typing import Dict, Any
from app.crons.models import (
    CronJobSpec,
    ScheduleSpec,
    DispatchSpec,
    DispatchTarget,
    CronJobRequest,
)


# 默认目标用户和会话
DEFAULT_USER = "user_001"
DEFAULT_SESSION = "default"


def create_daily_report_job(
    user_id: str = DEFAULT_USER,
    session_id: str = DEFAULT_SESSION,
    channel: str = "console"
) -> CronJobSpec:
    """创建每日日报任务 (每天 18:00)"""
    
    return CronJobSpec(
        id="daily_report",
        name="每日复盘",
        enabled=True,  # 已启用
        schedule=ScheduleSpec(
            cron="0 18 * * *",
            timezone="Asia/Shanghai"
        ),
        task_type="agent",
        request=CronJobRequest(
            input="请进行每日复盘，收集今天的工作总结",
            user_id=user_id,
            session_id=session_id
        ),
        dispatch=DispatchSpec(
            type="channel",
            channel=channel,
            target=DispatchTarget(
                user_id=user_id,
                session_id=session_id
            ),
            mode="final"
        ),
        meta={
            "description": "每天 18:00 收集各 Agent 工作总结",
            "agent_id": "04"
        }
    )


def create_dinner_meeting_job(
    user_id: str = DEFAULT_USER,
    session_id: str = DEFAULT_SESSION,
    channel: str = "console"
) -> CronJobSpec:
    """创建晚餐交流会任务 (每3天 21:00)"""
    
    return CronJobSpec(
        id="dinner_meeting",
        name="晚餐交流会",
        enabled=True,  # 已启用
        schedule=ScheduleSpec(
            cron="0 21 * * */3",
            timezone="Asia/Shanghai"
        ),
        task_type="agent",
        request=CronJobRequest(
            input="请主持晚餐交流会，让各 Agent 分享今天的工作和心得",
            user_id=user_id,
            session_id=session_id
        ),
        dispatch=DispatchSpec(
            type="channel",
            channel=channel,
            target=DispatchTarget(
                user_id=user_id,
                session_id=session_id
            ),
            mode="final"
        ),
        meta={
            "description": "每3天 21:00 Agent 晚餐交流会",
            "agent_id": "00",
            "participants": ["00", "01", "02", "03", "04"]
        }
    )


def create_health_check_job() -> CronJobSpec:
    """创建健康检查任务 (每6小时)"""
    
    return CronJobSpec(
        id="health_check",
        name="系统健康检查",
        enabled=True,
        schedule=ScheduleSpec(
            cron="0 */6 * * *",
            timezone="UTC"
        ),
        task_type="text",
        text="进行系统健康检查",
        dispatch=DispatchSpec(
            type="channel",
            channel="console",
            target=DispatchTarget(
                user_id="system",
                session_id="health_check"
            ),
            mode="final"
        ),
        meta={
            "description": "每6小时检查系统状态",
            "type": "system"
        }
    )


# 预定义任务映射
PREDEFINED_JOBS: Dict[str, CronJobSpec] = {}


def init_predefined_jobs(
    user_id: str = DEFAULT_USER,
    session_id: str = DEFAULT_SESSION,
    channel: str = "console"
) -> Dict[str, CronJobSpec]:
    """初始化预定义任务"""
    
    global PREDEFINED_JOBS
    
    PREDEFINED_JOBS = {
        "daily_report": create_daily_report_job(user_id, session_id, channel),
        "dinner_meeting": create_dinner_meeting_job(user_id, session_id, channel),
        "health_check": create_health_check_job(),
    }
    
    return PREDEFINED_JOBS


def get_predefined_job(job_id: str) -> CronJobSpec:
    """获取预定义任务"""
    return PREDEFINED_JOBS.get(job_id)


__all__ = [
    "create_daily_report_job",
    "create_dinner_meeting_job",
    "create_health_check_job",
    "init_predefined_jobs",
    "get_predefined_job",
]
