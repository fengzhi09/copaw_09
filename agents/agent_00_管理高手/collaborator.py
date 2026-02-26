# -*- coding: utf-8 -*-
"""
Task Collaborator - 任务协作器
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SubTask:
    """子任务"""
    task_id: int
    description: str
    agent_id: str
    status: str = "pending"  # pending/running/completed/failed
    result: Any = None
    error: str = ""
    dependencies: List[int] = field(default_factory=list)


@dataclass
class CollaborateResult:
    """协作结果"""
    success: bool
    task: str
    sub_tasks: List[SubTask] = field(default_factory=list)
    final_result: str = ""
    execution_time: float = 0.0


class TaskCollaborator:
    """任务协作器 - 协调多个 Agent 完成复杂任务"""
    
    # Agent 能力映射
    AGENT_CAPABILITIES = {
        "00": ["management", "coordination", "planning"],
        "01": ["research", "search", "analysis", "academic"],
        "02": ["code", "development", "debug", "engineering"],
        "03": ["creative", "writing", "design", "content"],
        "04": ["statistics", "collection", "reporting", "review"]
    }
    
    def __init__(self):
        self._results_cache: Dict[str, Any] = {}
    
    async def collaborate(
        self,
        task: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        协作处理任务。
        
        Args:
            task: 任务描述
            context: 上下文信息
        
        Returns:
            协作结果
        """
        start_time = datetime.now()
        
        # 1. 分析任务，分解子任务
        sub_tasks = self._decompose_task(task)
        
        # 2. 执行子任务
        results = await self._execute_subtasks(sub_tasks, context or {})
        
        # 3. 汇总结果
        final_result = self._aggregate_results(results)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": all(r.status == "completed" for r in results),
            "task": task,
            "sub_tasks": [
                {
                    "id": r.task_id,
                    "description": r.description,
                    "agent_id": r.agent_id,
                    "status": r.status,
                    "result": r.result,
                    "error": r.error
                }
                for r in results
            ],
            "final_result": final_result,
            "execution_time": execution_time
        }
    
    def _decompose_task(self, task: str) -> List[SubTask]:
        """分解任务为子任务"""
        task_lower = task.lower()
        sub_tasks = []
        task_id = 1
        
        # 研究类任务 -> 01
        if any(kw in task_lower for kw in ["调研", "搜索", "研究", "分析"]):
            sub_tasks.append(SubTask(
                task_id=task_id,
                description="进行调研分析",
                agent_id="01",
                dependencies=[]
            ))
            task_id += 1
        
        # 开发类任务 -> 02
        if any(kw in task_lower for kw in ["开发", "代码", "实现", "修复"]):
            sub_tasks.append(SubTask(
                task_id=task_id,
                description="开发实现",
                agent_id="02",
                dependencies=[task_id - 1] if sub_tasks else []
            ))
            task_id += 1
        
        # 创意类任务 -> 03
        if any(kw in task_lower for kw in ["创意", "文案", "包装", "展示"]):
            sub_tasks.append(SubTask(
                task_id=task_id,
                description="创意包装",
                agent_id="03",
                dependencies=[task_id - 1] if sub_tasks else []
            ))
            task_id += 1
        
        # 统计/总结类任务 -> 04
        if any(kw in task_lower for kw in ["总结", "复盘", "统计", "报告"]):
            sub_tasks.append(SubTask(
                task_id=task_id,
                description="总结报告",
                agent_id="04",
                dependencies=[task_id - 1] if sub_tasks else []
            ))
        
        # 默认分解
        if not sub_tasks:
            sub_tasks = [
                SubTask(task_id=1, description="处理任务", agent_id="00", dependencies=[])
            ]
        
        return sub_tasks
    
    async def _execute_subtasks(
        self,
        sub_tasks: List[SubTask],
        context: Dict[str, Any]
    ) -> List[SubTask]:
        """执行子任务"""
        # 按依赖顺序执行
        completed = {}
        results = []
        
        for sub_task in sub_tasks:
            # 等待依赖完成
            if sub_task.dependencies:
                await self._wait_for_dependencies(completed, sub_task.dependencies)
            
            # 执行子任务
            result = await self._execute_single_task(sub_task, context)
            completed[sub_task.task_id] = result
            results.append(result)
        
        return results
    
    async def _wait_for_dependencies(
        self,
        completed: Dict[int, SubTask],
        dependencies: List[int]
    ):
        """等待依赖完成"""
        while not all(dep_id in completed for dep_id in dependencies):
            await asyncio.sleep(0.1)
    
    async def _execute_single_task(
        self,
        sub_task: SubTask,
        context: Dict[str, Any]
    ) -> SubTask:
        """执行单个子任务"""
        sub_task.status = "running"
        
        try:
            # TODO: 实际调用 Agent
            # 模拟执行
            await asyncio.sleep(0.1)
            
            sub_task.status = "completed"
            sub_task.result = f"Agent {sub_task.agent_id} 完成: {sub_task.description}"
            
        except Exception as e:
            sub_task.status = "failed"
            sub_task.error = str(e)
        
        return sub_task
    
    def _aggregate_results(self, results: List[SubTask]) -> str:
        """汇总结果"""
        lines = ["📊 任务执行结果", ""]
        
        for r in results:
            status_emoji = {
                "completed": "✅",
                "failed": "❌",
                "running": "⏳"
            }.get(r.status, "❓")
            
            lines.append(f"{status_emoji} Agent {r.agent_id}: {r.description}")
            
            if r.result:
                lines.append(f"   结果: {r.result}")
            
            if r.error:
                lines.append(f"   错误: {r.error}")
        
        return "\n".join(lines)
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """获取可用 Agent 列表"""
        return [
            {"id": aid, "capabilities": caps}
            for aid, caps in self.AGENT_CAPABILITIES.items()
        ]


__all__ = ["TaskCollaborator", "SubTask", "CollaborateResult"]
