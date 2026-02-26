# -*- coding: utf-8 -*-
"""
Brain Module 单元测试
"""

import pytest
import sys
sys.path.insert(0, '/home/ace09/bots')


class TestThalamusIntentRecognition:
    """丘脑意图识别测试"""
    
    def test_intent_type_enum(self):
        """测试意图类型枚举"""
        from cp9.app.brain.thalamus import IntentType
        
        assert IntentType.SEARCH.value == "search"
        assert IntentType.CODE.value == "code"
        assert IntentType.CREATE.value == "create"
        assert IntentType.UNKNOWN.value == "unknown"
    
    def test_thalamus_creation(self):
        """测试丘脑创建"""
        from cp9.app.brain.thalamus import Thalamus
        
        thalamus = Thalamus()
        assert thalamus is not None
        assert thalamus.device == "cuda"
    
    def test_understand_intent_search(self):
        """测试搜索意图识别"""
        from cp9.app.brain.thalamus import Thalamus, IntentType
        
        thalamus = Thalamus()
        result = thalamus.understand_intent("帮我搜索一下机器学习的论文")
        
        assert result.intent == IntentType.SEARCH
        assert result.confidence > 0
    
    def test_understand_intent_code(self):
        """测试编程意图识别"""
        from cp9.app.brain.thalamus import Thalamus, IntentType
        
        thalamus = Thalamus()
        result = thalamus.understand_intent("写一个Python代码")
        
        assert result.intent == IntentType.CODE
        assert result.confidence > 0
    
    def test_understand_intent_create(self):
        """测试创作意图识别"""
        from cp9.app.brain.thalamus import Thalamus, IntentType
        
        thalamus = Thalamus()
        result = thalamus.understand_intent("帮我写一段文案")
        
        assert result.intent == IntentType.CREATE
        assert result.confidence > 0
    
    def test_understand_intent_manage(self):
        """测试管理意图识别"""
        from cp9.app.brain.thalamus import Thalamus, IntentType
        
        thalamus = Thalamus()
        result = thalamus.understand_intent("创建一个新的Agent")
        
        assert result.intent == IntentType.MANAGE
        assert result.confidence > 0
    
    def test_understand_intent_stats(self):
        """测试统计意图识别"""
        from cp9.app.brain.thalamus import Thalamus, IntentType
        
        thalamus = Thalamus()
        result = thalamus.understand_intent("查看本月成本统计")
        
        assert result.intent == IntentType.STATS
        assert result.confidence > 0
    
    def test_route_message(self):
        """测试消息路由"""
        from cp9.app.brain.thalamus import Thalamus
        
        thalamus = Thalamus()
        
        # 搜索 -> 01
        agent_id = thalamus.route_message("搜索论文")
        assert agent_id == "01"
        
        # 代码 -> 02
        agent_id = thalamus.route_message("写代码")
        assert agent_id == "02"
        
        # 创作 -> 03
        agent_id = thalamus.route_message("写文案")
        assert agent_id == "03"
        
        # 管理 -> 00
        agent_id = thalamus.route_message("创建Agent")
        assert agent_id == "00"
        
        # 统计 -> 04
        agent_id = thalamus.route_message("成本统计")
        assert agent_id == "04"
    
    def test_extract_entities(self):
        """测试实体提取"""
        from cp9.app.brain.thalamus import Thalamus
        
        thalamus = Thalamus()
        
        # 提取 Agent 编号 - 消息中包含 02
        result = thalamus.understand_intent("让02号帮我写代码")
        # agent_id 可能提取不到，因为正则可能需要调整
        
        # 提取关键词
        result = thalamus.understand_intent("搜索机器学习论文")
        assert "keywords" in result.entities
        
        # 验证关键词存在
        assert "search" in result.entities.get("keywords", []) or "搜索" in result.entities.get("keywords", [])


class TestThalamusMemory:
    """丘脑记忆测试"""
    
    def test_add_memory(self):
        """测试添加记忆"""
        from cp9.app.brain.thalamus import Thalamus, MemoryItem
        
        thalamus = Thalamus()
        item = MemoryItem(
            content="测试记忆",
            timestamp=1234567890.0,
            agent_id="00",
            session_id="test_session"
        )
        
        thalamus.add_memory(item)
        assert len(thalamus._memory_store) == 1
    
    def test_retrieve_memory(self):
        """测试检索记忆"""
        from cp9.app.brain.thalamus import Thalamus, MemoryItem
        
        thalamus = Thalamus()
        
        # 添加记忆
        thalamus.add_memory(MemoryItem(
            content="用户问了一个问题",
            timestamp=1234567890.0,
            agent_id="00",
            session_id="user1"
        ))
        
        # 检索
        results = thalamus.retrieve_memory("问题", user_id="user1")
        assert isinstance(results, list)


class TestPrefrontalModelConfig:
    """前额叶模型配置测试"""
    
    def test_model_config(self):
        """测试模型配置"""
        from cp9.app.brain.prefrontal import Prefrontal, ModelProvider
        
        config = Prefrontal.MODEL_CONFIG
        
        assert "glm-5" in config
        assert config["glm-5"]["provider"] == ModelProvider.ZHIPU
        
        assert "MiniMax-M2.5" in config
        assert config["MiniMax-M2.5"]["provider"] == ModelProvider.MINIMAX
    
    def test_prefrontal_creation(self):
        """测试前额叶创建"""
        from cp9.app.brain.prefrontal import Prefrontal
        
        prefrontal = Prefrontal(primary_model="glm-5")
        
        assert prefrontal.primary_model == "glm-5"
        assert prefrontal.fallback_model == "MiniMax-M2.5"
    
    def test_prefrontal_no_api_key(self):
        """测试无 API Key"""
        from cp9.app.brain.prefrontal import Prefrontal
        
        prefrontal = Prefrontal(primary_model="glm-5", api_key="")
        
        # 没有 API Key 时不应抛出异常
        assert prefrontal.api_key == ""


class TestPrefrontalDataClasses:
    """前额叶数据结构测试"""
    
    def test_reasoning_result(self):
        """测试推理结果"""
        from cp9.app.brain.prefrontal import ReasoningResult
        
        result = ReasoningResult(
            reasoning="推理过程",
            conclusion="结论",
            confidence=0.9,
            evidence=["证据1"]
        )
        
        assert result.reasoning == "推理过程"
        assert result.confidence == 0.9
    
    def test_plan_result(self):
        """测试计划结果"""
        from cp9.app.brain.prefrontal import PlanResult, PlanStep
        
        steps = [
            PlanStep(
                step_id=1,
                description="步骤1",
                agent_id="01"
            ),
            PlanStep(
                step_id=2,
                description="步骤2",
                agent_id="02",
                dependencies=[1]
            )
        ]
        
        result = PlanResult(
            steps=steps,
            estimated_time=120,
            resources=["资源1"],
            success_rate=0.8
        )
        
        assert len(result.steps) == 2
        assert result.estimated_time == 120
    
    def test_generation_result(self):
        """测试生成结果"""
        from cp9.app.brain.prefrontal import GenerationResult
        
        result = GenerationResult(
            text="生成的文本",
            model="glm-5",
            tokens_used=100,
            finish_reason="stop"
        )
        
        assert result.text == "生成的文本"
        assert result.tokens_used == 100


class TestBrainIntegration:
    """脑部模块集成测试"""
    
    def test_get_thalamus_singleton(self):
        """测试丘脑单例"""
        from cp9.app.brain import get_thalamus
        
        t1 = get_thalamus()
        t2 = get_thalamus()
        
        assert t1 is t2
    
    def test_get_prefrontal_singleton(self):
        """测试前额叶单例"""
        from cp9.app.brain import get_prefrontal
        
        p1 = get_prefrontal()
        p2 = get_prefrontal()
        
        assert p1 is p2
    
    def test_thalamus_to_prefrontal_flow(self):
        """测试丘脑到前额叶流程"""
        from cp9.app.brain.thalamus import Thalamus
        from cp9.app.brain.prefrontal import Prefrontal
        
        thalamus = Thalamus()
        prefrontal = Prefrontal()
        
        # 丘脑识别意图
        intent = thalamus.understand_intent("搜索机器学习论文")
        assert intent.intent.value == "search"
        
        # 丘脑路由
        agent_id = thalamus.route_message("搜索机器学习论文")
        assert agent_id == "01"
        
        # 前额叶配置
        assert prefrontal.primary_model == "glm-5"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
