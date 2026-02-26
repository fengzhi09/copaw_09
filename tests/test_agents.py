# -*- coding: utf-8 -*-
"""
Tests for cp9 Agent modules
"""

import pytest
from agents.agent_00_管理高手 import AgentCreator, AgentManager, RequirementClarifier
from agents.agent_01_学霸 import Agent01Config
from agents.agent_02_编程高手 import Agent02Config
from agents.agent_03_创意青年 import Agent03Config
from agents.agent_04_统计学长 import Agent04Config
from agents.registry import AgentRegistry, get_registry


class TestAgentConfigs:
    """Test Agent configurations"""
    
    def test_agent_01_config(self):
        config = Agent01Config()
        assert config.meta.id == "01"
        assert config.meta.role == "academic"
        assert "谷歌学术" in config.meta.data_sources
    
    def test_agent_02_config(self):
        config = Agent02Config()
        assert config.meta.id == "02"
        assert config.meta.role == "developer"
        assert "python_version" in config.startup_check
    
    def test_agent_03_config(self):
        config = Agent03Config()
        assert config.meta.id == "03"
        assert config.meta.role == "creative"
        assert config.meta.tools["print"] == "nano-banana-pro"
    
    def test_agent_04_config(self):
        config = Agent04Config()
        assert config.meta.id == "04"
        assert config.meta.role == "collector"
        assert config.daily_routine["trigger"] == "每天 18:00"


class TestAgentRegistry:
    """Test Agent registry"""
    
    def test_predefined_agents(self):
        registry = AgentRegistry()
        agents = registry.list_agents()
        assert len(agents) >= 5  # 00-04
    
    def test_get_agent_by_id(self):
        registry = AgentRegistry()
        agent = registry.get_agent("00")
        assert agent is not None
        assert agent["role"] == "master"
    
    def test_get_agent_by_role(self):
        registry = AgentRegistry()
        agent = registry.get_agent_by_role("academic")
        assert agent is not None
        assert agent["id"] == "01"
    
    def test_is_predefined(self):
        registry = AgentRegistry()
        assert registry.is_predefined("00") is True
        assert registry.is_predefined("99") is False


class TestRequirementClarifier:
    """Test requirement clarifier"""
    
    def test_generate_clarification_questions(self):
        clarifier = RequirementClarifier()
        
        # Test with minimal requirement
        questions = clarifier.generate_clarification_questions("创建一个助手")
        assert len(questions) > 0
    
    def test_format_confirmation(self):
        clarifier = RequirementClarifier()
        spec = {
            "id": "05",
            "name": "测试助手",
            "role": "tester",
            "quota": "一般",
            "skills": {
                "required": ["test_skill"],
                "optional": []
            }
        }
        
        confirmation = clarifier.format_confirmation(spec)
        assert "测试助手" in confirmation
        assert "确认" in confirmation


class TestAgentCreator:
    """Test Agent creator"""
    
    def test_create_agent_spec_academic(self):
        creator = AgentCreator()
        spec = creator.create_agent_spec("我需要一个学术搜索助手")
        
        assert "id" in spec
        assert spec["name"] == "学术助手"
        assert spec["role"] == "academic"
    
    def test_create_agent_spec_developer(self):
        creator = AgentCreator()
        spec = creator.create_agent_spec("帮我写代码")
        
        assert spec["name"] == "编程助手"
        assert spec["role"] == "developer"
    
    def test_create_agent_spec_creative(self):
        creator = AgentCreator()
        spec = creator.create_agent_spec("需要一个写文案的")
        
        assert spec["name"] == "创意助手"
        assert spec["role"] == "creative"


class TestAgentManager:
    """Test Agent manager"""
    
    def test_list_agents(self):
        manager = AgentManager()
        agents = manager.list_agents()
        assert isinstance(agents, list)
    
    def test_get_all_status(self):
        manager = AgentManager()
        status = manager.get_all_status()
        
        assert "total" in status
        assert "active" in status
        assert "agents" in status
