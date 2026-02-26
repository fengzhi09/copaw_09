# -*- coding: utf-8 -*-
"""
00 号管理高手 单元测试
"""

import pytest
import sys
import json
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, '/home/ace09/bots')
from copaw_09.agents.agent_00_管理高手.manager import (
    AgentCreator,
    AgentManager,
    RequirementClarifier,
)


class TestAgentCreator:
    """Agent 创建器测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        tmp = tempfile.mkdtemp()
        yield Path(tmp)
        shutil.rmtree(tmp)
    
    def test_create_agent_spec_academic(self, temp_dir):
        """测试学术 Agent 规格生成"""
        creator = AgentCreator(str(temp_dir))
        spec = creator.create_agent_spec("创建一个学术助手")
        
        assert spec["name"] == "学术助手"
        assert spec["role"] == "academic"
        assert "academic_search" in spec["skills"]["required"]
    
    def test_create_agent_spec_coder(self, temp_dir):
        """测试编程 Agent 规格生成"""
        creator = AgentCreator(str(temp_dir))
        spec = creator.create_agent_spec("需要一个编程助手")
        
        assert spec["name"] == "编程助手"
        assert spec["role"] == "developer"
        assert "code_analysis" in spec["skills"]["required"]
    
    def test_create_agent_spec_creative(self, temp_dir):
        """测试创意 Agent 规格生成"""
        creator = AgentCreator(str(temp_dir))
        spec = creator.create_agent_spec("创意写作助手")
        
        assert spec["name"] == "创意助手"
        assert spec["role"] == "creative"
        assert "text_creative" in spec["skills"]["required"]
    
    def test_create_agent_spec_general(self, temp_dir):
        """测试通用 Agent 规格生成"""
        creator = AgentCreator(str(temp_dir))
        spec = creator.create_agent_spec("随便一个助手")
        
        assert spec["name"] == "通用助手"
        assert spec["role"] == "general"
    
    def test_generate_agent_id(self, temp_dir):
        """测试生成 Agent ID"""
        creator = AgentCreator(str(temp_dir))
        agent_id = creator._generate_agent_id()
        
        assert isinstance(agent_id, str)
        assert len(agent_id) == 2
    
    def test_create_agent_directory(self, temp_dir):
        """测试创建 Agent 目录"""
        creator = AgentCreator(str(temp_dir))
        
        spec = {
            "id": "99",
            "name": "测试助手",
            "role": "test",
            "skills": {"required": [], "optional": []},
            "quota": "一般",
            "channels": ["feishu"]
        }
        
        agent_dir = creator.create_agent_directory(spec)
        
        assert agent_dir.exists()
        assert (agent_dir / ".meta.json").exists()
        assert (agent_dir / "memory" / "short_term").exists()
        assert (agent_dir / "memory" / "long_term").exists()


class TestAgentManager:
    """Agent 管理器测试"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        tmp = tempfile.mkdtemp()
        yield Path(tmp)
        shutil.rmtree(tmp)
    
    def test_list_agents_empty(self, temp_dir):
        """测试列出空列表"""
        manager = AgentManager(str(temp_dir))
        agents = manager.list_agents()
        
        assert agents == []
    
    def test_list_agents_with_data(self, temp_dir):
        """测试列出 Agent"""
        # 创建测试 Agent
        agent_dir = temp_dir / "agent_01_测试"
        agent_dir.mkdir()
        
        meta = {
            "id": "01",
            "name": "测试",
            "role": "test",
            "status": "active"
        }
        
        with open(agent_dir / ".meta.json", "w") as f:
            json.dump(meta, f)
        
        manager = AgentManager(str(temp_dir))
        agents = manager.list_agents()
        
        assert len(agents) == 1
        assert agents[0]["id"] == "01"
    
    def test_get_agent_status(self, temp_dir):
        """测试获取单个 Agent 状态"""
        agent_dir = temp_dir / "agent_01_测试"
        agent_dir.mkdir()
        
        meta = {
            "id": "01",
            "name": "测试",
            "role": "test",
            "status": "active"
        }
        
        with open(agent_dir / ".meta.json", "w") as f:
            json.dump(meta, f)
        
        manager = AgentManager(str(temp_dir))
        status = manager.get_agent_status("01")
        
        assert status is not None
        assert status["id"] == "01"
    
    def test_get_all_status(self, temp_dir):
        """测试获取所有状态"""
        manager = AgentManager(str(temp_dir))
        status = manager.get_all_status()
        
        assert "total" in status
        assert "active" in status
        assert "agents" in status


class TestRequirementClarifier:
    """需求确认器测试"""
    
    def test_generate_clarification_questions_role(self):
        """测试生成角色问题"""
        questions = RequirementClarifier.generate_clarification_questions("创建一个助手")
        
        # 应该有确认问题
        assert len(questions) > 0
    
    def test_generate_clarification_questions_skills(self):
        """测试生成技能问题"""
        questions = RequirementClarifier.generate_clarification_questions("创建一个 Agent")
        
        # 应该有技能确认问题
        assert any("技能" in q or "能力" in q for q in questions)
    
    def test_generate_clarification_questions_quota(self):
        """测试生成配额问题"""
        questions = RequirementClarifier.generate_clarification_questions("创建一个 Agent")
        
        # 应该有配额确认问题
        assert any("配额" in q or "资源" in q for q in questions)
    
    def test_generate_clarification_questions_max_3(self):
        """测试最多返回3个问题"""
        questions = RequirementClarifier.generate_clarification_questions("创建一个 Agent")
        
        assert len(questions) <= 3
    
    def test_format_confirmation(self):
        """测试格式化确认"""
        spec = {
            "id": "05",
            "name": "测试助手",
            "role": "test",
            "skills": {
                "required": ["skill1"],
                "optional": ["skill2"]
            },
            "quota": "中等"
        }
        
        confirmation = RequirementClarifier.format_confirmation(spec)
        
        assert "05" in confirmation
        assert "测试助手" in confirmation
        assert "确认" in confirmation
        assert "skill1" in confirmation


class TestAgent00Integration:
    """集成测试"""
    
    def test_full_create_flow(self):
        """测试完整创建流程"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            
            # 1. 分析需求
            creator = AgentCreator(tmp_path)
            spec = creator.create_agent_spec("创建一个学术助手")
            
            # 2. 确认问题
            questions = RequirementClarifier.generate_clarification_questions("创建一个学术助手")
            
            # 3. 创建目录
            agent_dir = creator.create_agent_directory(spec)
            
            # 4. 验证
            assert agent_dir.exists()
            assert (agent_dir / ".meta.json").exists()
            
            # 5. 列出 Agent
            manager = AgentManager(tmp_path)
            agents = manager.list_agents()
            assert len(agents) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
