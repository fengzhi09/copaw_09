# -*- coding: utf-8 -*-
"""
Tests for Cp9 memory module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from memory import MemoryStore, MemorySystem


class TestMemoryStore:
    """Test file-based memory store"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.store = MemoryStore(self.temp_dir)
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_short_term(self):
        content = {"task": "test", "result": "ok"}
        self.store.save_short_term("01", "session-001", content)
        
        loaded = self.store.load_short_term("01", "session-001")
        assert loaded == content
    
    def test_load_short_term_empty(self):
        loaded = self.store.load_short_term("01", "nonexistent")
        assert loaded is None
    
    def test_clear_short_term(self):
        content = {"task": "test"}
        self.store.save_short_term("01", "session-001", content)
        
        self.store.clear_short_term("01", "session-001")
        loaded = self.store.load_short_term("01", "session-001")
        assert loaded is None
    
    def test_save_long_term(self):
        filename = self.store.save_long_term(
            "01",
            "测试记忆",
            "这是测试内容",
            ["test", "demo"]
        )
        
        assert filename is not None
        assert Path(self.store._get_long_term_path("01") / filename).exists()
    
    def test_list_long_term(self):
        self.store.save_long_term("01", "记忆1", "内容1")
        self.store.save_long_term("01", "记忆2", "内容2")
        
        memories = self.store.list_long_term("01")
        assert len(memories) == 2
    
    def test_get_long_term(self):
        filename = self.store.save_long_term("01", "测试", "测试内容")
        
        content = self.store.get_long_term("01", filename)
        assert "测试内容" in content


class TestMemorySystem:
    """Test memory system"""
    
    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.memory = MemorySystem("01")
        self.memory.file_store = MemoryStore(self.temp_dir)
        self.memory.use_db = False
    
    def teardown_method(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_short_term(self):
        self.memory.save_short_term("session-001", {"task": "test"})
        
        loaded = self.memory.load_short_term("session-001")
        assert loaded["task"] == "test"
    
    def test_save_long_term(self):
        filename = self.memory.save_long_term(
            "测试记忆",
            "这是测试内容",
            ["test"]
        )
        
        assert filename is not None
    
    def test_list_long_term(self):
        self.memory.save_long_term("记忆1", "内容1")
        self.memory.save_long_term("记忆2", "内容2")
        
        memories = self.memory.list_long_term()
        assert len(memories) >= 2
    
    def test_search_long_term(self):
        self.memory.save_long_term("关于Python", "Python是一种编程语言")
        self.memory.save_long_term("关于Java", "Java是另一种语言")
        
        results = self.memory.search_long_term("Python")
        assert len(results) >= 1
