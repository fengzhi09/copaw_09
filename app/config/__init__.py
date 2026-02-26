# -*- coding: utf-8 -*-
"""
Config Module - 配置管理
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import os


def get_config_path() -> Path:
    """获取配置文件路径"""
    # 优先使用环境变量
    config_path = os.getenv("COPAW_CONFIG_PATH")
    if config_path:
        return Path(config_path)
    
    # 默认路径
    default_path = Path.home() / ".copaw_mgr.yaml"
    if default_path.exists():
        return default_path
    
    return Path("/opt/ai_works/copaw/config.yaml")


# 尝试加载 YAML 配置
try:
    import yaml
    CONFIG_PATH = get_config_path()
    
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _config_data = yaml.safe_load(f) or {}
    else:
        _config_data = {}
except Exception:
    _config_data = {}


def get_app_config() -> dict:
    """获取应用配置"""
    return _config_data.get("app", {})


def get_channel_config(channel: str) -> dict:
    """获取渠道配置"""
    return _config_data.get("config", {}).get("channel", {}).get(channel, {})


# ========== Channel Config Classes ==========

@dataclass
class FeishuChannelConfig:
    """飞书频道配置"""
    enabled: bool = False
    app_id: str = ""
    app_secret: str = ""
    bot_prefix: str = "/ai"
    encrypt_key: str = ""
    verification_token: str = ""
    media_dir: str = "~/.copaw/media"
    filters: dict = field(default_factory=dict)


@dataclass
class DingTalkChannelConfig:
    """钉钉频道配置"""
    enabled: bool = False
    app_key: str = ""
    app_secret: str = ""
    agent_id: str = ""
    bot_prefix: str = "/ai"
    filters: dict = field(default_factory=dict)


@dataclass
class QQChannelConfig:
    """QQ 频道配置"""
    enabled: bool = False
    qq_id: str = ""
    token: str = ""
    secret: str = ""
    filters: dict = field(default_factory=dict)


@dataclass
class DiscordChannelConfig:
    """Discord 频道配置"""
    enabled: bool = False
    bot_token: str = ""
    filters: dict = field(default_factory=dict)


@dataclass
class TelegramChannelConfig:
    """Telegram 频道配置"""
    enabled: bool = False
    bot_token: str = ""
    filters: dict = field(default_factory=dict)


__all__ = [
    "get_config_path",
    "get_app_config",
    "get_channel_config",
    "FeishuChannelConfig",
    "DingTalkChannelConfig",
    "QQChannelConfig",
    "DiscordChannelConfig",
    "TelegramChannelConfig",
]
