# -*- coding: utf-8 -*-
"""
Tests for Copaw sensors module
"""

import pytest
from sensors import PrintSensor, DispatchSensor, RecorderSensor, SensorFactory


class TestDispatchSensor:
    """Test dispatch sensor"""
    
    def test_classify_intent_academic(self):
        sensor = DispatchSensor()
        result = sensor.classify_intent("帮我搜索论文", ["00", "01", "02", "03", "04"])
        
        assert result["agent_id"] == "01"  # 学霸
        assert "confidence" in result
    
    def test_classify_intent_developer(self):
        sensor = DispatchSensor()
        result = sensor.classify_intent("代码报错了", ["00", "01", "02", "03", "04"])
        
        assert result["agent_id"] == "02"  # 编程高手
    
    def test_classify_intent_creative(self):
        sensor = DispatchSensor()
        result = sensor.classify_intent("帮我写一段文案", ["00", "01", "02", "03", "04"])
        
        assert result["agent_id"] == "03"  # 创意青年
    
    def test_classify_intent_master(self):
        sensor = DispatchSensor()
        result = sensor.classify_intent("创建一个新的Agent", ["00", "01", "02", "03", "04"])
        
        assert result["agent_id"] == "00"  # 管理高手
    
    def test_classify_intent_default(self):
        sensor = DispatchSensor()
        result = sensor.classify_intent("你好", ["00", "01", "02", "03", "04"])
        
        # Default to 00 for unknown intent
        assert result["agent_id"] == "00"


class TestSensorFactory:
    """Test sensor factory"""
    
    def test_get_print_sensor(self):
        sensor = SensorFactory.get_print()
        assert isinstance(sensor, PrintSensor)
    
    def test_get_dispatch_sensor(self):
        sensor = SensorFactory.get_dispatch()
        assert isinstance(sensor, DispatchSensor)
    
    def test_get_recorder_sensor(self):
        sensor = SensorFactory.get_recorder()
        assert isinstance(sensor, RecorderSensor)
    
    def test_singleton(self):
        # Same instance should be returned
        sensor1 = SensorFactory.get_print()
        sensor2 = SensorFactory.get_print()
        assert sensor1 is sensor2


class TestRecorderSensor:
    """Test recorder sensor"""
    
    def test_recorder_not_implemented(self):
        sensor = RecorderSensor()
        
        with pytest.raises(NotImplementedError):
            sensor.generate("test prompt")
    
    def test_recorder_disabled_by_default(self):
        sensor = RecorderSensor()
        assert sensor.enabled is False
