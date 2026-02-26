# -*- coding: utf-8 -*-
"""
Pytest 配置 - 测试前设置环境变量和路径
"""

import os
import sys
import pytest
from pathlib import Path

# 添加 cp9 目录到 sys.path
COPAW_DIR = Path(__file__).parent.parent.absolute()
if str(COPAW_DIR) not in sys.path:
    sys.path.insert(0, str(COPAW_DIR))

# 设置测试配置路径
TEST_CONFIG_DIR = COPAW_DIR / "tests" / "test_config"
TEST_CONFIG_FILE = TEST_CONFIG_DIR / "config.yaml"

# 确保测试配置目录存在
TEST_CONFIG_DIR.mkdir(exist_ok=True)

# 创建测试配置文件（如果没有）
if not TEST_CONFIG_FILE.exists():
    test_config = """# 测试配置文件
app:
  name: cp9_test
  version: "1.0"

config:
  channel:
    feishu:
      enabled: true
      app_id: "cli_test123"
      app_secret: "test_secret"
      bot_prefix: "/ai"
      encrypt_key: ""
      verification_token: ""
      media_dir: "~/.cp9/media"
      filters:
        ignore_events: []
        ignore_users: []
        ignore_keywords: []
    
    dingtalk:
      enabled: false
      app_key: ""
      app_secret: ""
      agent_id: ""
      bot_prefix: "/ai"
      filters: {}
    
    qq:
      enabled: false
      qq_id: ""
      token: ""
      secret: ""
      filters: {}
    
    discord:
      enabled: false
      bot_token: ""
      filters: {}
    
    telegram:
      enabled: false
      bot_token: ""
      filters: {}
"""
    TEST_CONFIG_FILE.write_text(test_config, encoding="utf-8")

# 设置环境变量
os.environ["COPAW_CONFIG_PATH"] = str(TEST_CONFIG_FILE)


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    """测试前设置配置"""
    # 确保环境变量已设置
    os.environ["COPAW_CONFIG_PATH"] = str(TEST_CONFIG_FILE)
    
    # 确保正确的 sys.path
    cp9_dir = Path(__file__).parent.parent.absolute()
    if str(cp9_dir) not in sys.path:
        sys.path.insert(0, str(cp9_dir))
    
    yield
