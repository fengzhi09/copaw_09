# -*- coding: utf-8 -*-
from typing import Optional, List, Union
from pydantic import BaseModel, Field

from ..constant import (
    HEARTBEAT_DEFAULT_EVERY,
    HEARTBEAT_DEFAULT_TARGET,
)


class ChannelFiltersConfig(BaseModel):
    """Channel event filters configuration.
    
    Events matching these filters will be ignored (not processed).
    """
    # 忽略的事件类型
    ignore_events: List[str] = Field(
        default_factory=list,
        description="Event types to ignore"
    )
    # 忽略的用户 ID
    ignore_users: List[str] = Field(
        default_factory=list,
        description="User IDs to ignore"
    )
    # 忽略的关键词（消息内容包含这些词则忽略）
    ignore_keywords: List[str] = Field(
        default_factory=list,
        description="Keywords to ignore in message content"
    )


class BaseChannelConfig(BaseModel):
    """Base for channel config (read from config.json, no env)."""

    enabled: bool = False
    bot_prefix: str = ""
    # 事件过滤配置
    filters: ChannelFiltersConfig = Field(
        default_factory=ChannelFiltersConfig,
        description="Event filters"
    )


class IMessageChannelConfig(BaseChannelConfig):
    db_path: str = "~/Library/Messages/chat.db"
    poll_sec: float = 1.0


class DiscordConfig(BaseChannelConfig):
    bot_token: str = ""
    http_proxy: str = ""
    http_proxy_auth: str = ""


class DingTalkConfig(BaseChannelConfig):
    client_id: str = ""
    client_secret: str = ""


class FeishuConfig(BaseChannelConfig):
    """Feishu/Lark channel: app_id, app_secret; optional encrypt_key,
    verification_token for event handler. media_dir for received media.
    """

    app_id: str = ""
    app_secret: str = ""
    encrypt_key: str = ""
    verification_token: str = ""
    media_dir: str = "~/.cp9/media"
    
    # 默认飞书过滤配置
    filters: ChannelFiltersConfig = Field(
        default_factory=lambda: ChannelFiltersConfig(
            ignore_events=[
                "pin_added",
                "pin_removed", 
                "reaction_added",
                "reaction_removed",
                "message_created",
            ],
            ignore_keywords=["[表情]", "收到"]
        )
    )


class QQConfig(BaseChannelConfig):
    app_id: str = ""
    client_secret: str = ""


class ConsoleConfig(BaseChannelConfig):
    """Console channel: prints agent responses to stdout."""

    enabled: bool = True


class ChannelConfig(BaseModel):
    imessage: IMessageChannelConfig = IMessageChannelConfig()
    discord: DiscordConfig = DiscordConfig()
    dingtalk: DingTalkConfig = DingTalkConfig()
    feishu: FeishuConfig = FeishuConfig()
    qq: QQConfig = QQConfig()
    console: ConsoleConfig = ConsoleConfig()


class LastApiConfig(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None


class ActiveHoursConfig(BaseModel):
    """Optional active window for heartbeat (e.g. 08:00–22:00)."""

    start: str = "08:00"
    end: str = "22:00"


class HeartbeatConfig(BaseModel):
    """Heartbeat: run agent with HEARTBEAT.md as query at interval."""

    model_config = {"populate_by_name": True}

    every: str = Field(default=HEARTBEAT_DEFAULT_EVERY)
    target: str = Field(default=HEARTBEAT_DEFAULT_TARGET)
    active_hours: Optional[ActiveHoursConfig] = Field(
        default=None,
        alias="activeHours",
    )


class AgentsDefaultsConfig(BaseModel):
    heartbeat: Optional[HeartbeatConfig] = None


class AgentsConfig(BaseModel):
    defaults: AgentsDefaultsConfig = Field(
        default_factory=AgentsDefaultsConfig,
    )
    language: str = Field(
        default="zh",
        description="Language for agent MD files (en/zh)",
    )
    installed_md_files_language: Optional[str] = Field(
        default=None,
        description="Language of currently installed md files",
    )


class LastDispatchConfig(BaseModel):
    """Last channel/user/session that received a user-originated reply."""

    channel: str = ""
    user_id: str = ""
    session_id: str = ""


class Config(BaseModel):
    """Root config (config.json)."""

    channels: ChannelConfig = ChannelConfig()
    last_api: LastApiConfig = LastApiConfig()
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    last_dispatch: Optional[LastDispatchConfig] = None
    # When False, channel output hides tool call/result details (show "...").
    show_tool_details: bool = True


ChannelConfigUnion = Union[
    IMessageChannelConfig,
    DiscordConfig,
    DingTalkConfig,
    FeishuConfig,
    QQConfig,
    ConsoleConfig,
]
