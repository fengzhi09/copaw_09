# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
import json
import logging
import os
import re
from pathlib import Path

from agentscope.mcp import StdIOStatefulClient
from agentscope.pipeline import stream_printing_messages
from agentscope_runtime.engine.runner import Runner
from agentscope_runtime.engine.schemas.agent_schemas import AgentRequest
from dotenv import load_dotenv

from .session import SafeJSONSession
from .utils import build_env_context
from ..channels.schema import DEFAULT_CHANNEL
from ...agents.memory import MemoryManager
from ...agents.react_agent import CoPawAgent
from ...constant import WORKING_DIR

logger = logging.getLogger(__name__)


def _expand_env_vars(config: dict) -> dict:
    """Recursively expand ${VAR} and $VAR patterns in config values."""
    if isinstance(config, dict):
        return {k: _expand_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [_expand_env_vars(item) for item in config]
    elif isinstance(config, str):
        # Replace ${VAR} and $VAR with environment variables
        def replacer(match):
            var_name = match.group(1) or match.group(2)
            return os.getenv(var_name, match.group(0))
        return re.sub(r'\$\{(\w+)\}|\$(\w+)', replacer, config)
    return config


class AgentRunner(Runner):
    def __init__(self) -> None:
        super().__init__()
        self.framework_type = "agentscope"
        self._chat_manager = None  # Store chat_manager reference
        self._mcp_clients = {}  # Store all MCP clients by name
        self.memory_manager: MemoryManager | None = None

    def set_chat_manager(self, chat_manager):
        """Set chat manager for auto-registration.

        Args:
            chat_manager: ChatManager instance
        """
        self._chat_manager = chat_manager

    def _load_mcp_config(self) -> dict:
        """Load MCP servers configuration from config.json."""
        config_path = WORKING_DIR / "config.json"
        if not config_path.exists():
            logger.debug(f"Config file not found: {config_path}")
            return {}
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            mcp_config = config.get("mcpServers", {})
            # Expand environment variables
            return _expand_env_vars(mcp_config)
        except Exception as e:
            logger.warning(f"Failed to load MCP config: {e}")
            return {}

    async def _init_mcp_clients(self):
        """Initialize MCP clients from config."""
        mcp_config = self._load_mcp_config()
        
        if not mcp_config:
            logger.debug("No MCP servers configured")
            # Fallback to old tavily-mcp
            await self._init_tavily_mcp()
            return

        for name, config in mcp_config.items():
            if not config.get("enabled", True):
                logger.info(f"MCP server '{name}' is disabled, skipping")
                continue
            
            command = config.get("command", "npx")
            args = config.get("args", [])
            env = config.get("env", {})
            
            # Skip if command is empty
            if not command:
                logger.warning(f"MCP server '{name}' has no command, skipping")
                continue
            
            try:
                logger.info(f"Initializing MCP server: {name}")
                client = StdIOStatefulClient(
                    name=f"{name}_mcp",
                    command=command,
                    args=args,
                    env=env,
                )
                await client.connect()
                self._mcp_clients[name] = client
                logger.info(f"MCP server '{name}' connected successfully")
            except Exception as e:
                logger.warning(f"MCP server '{name}' connect failed: {e}")

    async def _init_tavily_mcp(self):
        """Legacy: Initialize tavily-mcp (for backward compatibility)."""
        tavily_key = os.getenv("TAVILY_API_KEY", "")
        if not tavily_key:
            logger.debug("TAVILY_API_KEY not set, skipping tavily-mcp")
            return
        
        try:
            client = StdIOStatefulClient(
                name="tavily_mcp",
                command="npx",
                args=["-y", "tavily-mcp@latest"],
                env={"TAVILY_API_KEY": tavily_key},
            )
            await client.connect()
            self._mcp_clients["tavily"] = client
            logger.info("tavily-mcp connected successfully")
        except Exception as e:
            logger.debug(f"tavily-mcp connect failed: {e}")

    async def query_handler(
        self,
        msgs,
        request: AgentRequest = None,
        **kwargs,
    ):
        """
        Handle agent query.
        """
        session_id = request.session_id
        user_id = request.user_id
        channel = getattr(request, "channel", DEFAULT_CHANNEL)

        logger.info(
            "Handle agent query:\n%s",
            json.dumps(
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "channel": channel,
                    "msgs_len": len(msgs) if msgs else 0,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )

        env_context = build_env_context(
            session_id=session_id,
            user_id=user_id,
            channel=channel,
            working_dir=str(WORKING_DIR),
        )
        
        # Collect all MCP clients
        mcp_clients = list(self._mcp_clients.values())

        agent = CoPawAgent(
            env_context=env_context,
            mcp_clients=mcp_clients,
            memory_manager=self.memory_manager,
        )
        await agent.register_mcp_clients()
        agent.set_console_output_enabled(enabled=False)

        try:
            logger.debug(
                f"Agent Query msgs {msgs}",
            )

            name = "New Chat"
            if len(msgs) > 0:
                content = msgs[0].get_text_content()
                if content:
                    name = content[:10]
                else:
                    name = "多媒体消息"

            if self._chat_manager is not None:
                chat = await self._chat_manager.get_or_create_chat(
                    session_id,
                    user_id,
                    channel,
                    name=name,
                )

            await self.session.load_session_state(
                session_id=session_id,
                user_id=user_id,
                agent=agent,
            )

            # Rebuild system prompt so it always reflects the latest
            # AGENTS.md / SOUL.md / PROFILE.md, not the stale one saved
            # in the session state.
            agent.rebuild_sys_prompt()

            async for msg, last in stream_printing_messages(
                agents=[agent],
                coroutine_task=agent(msgs),
            ):
                yield msg, last

            await self.session.save_session_state(
                session_id=session_id,
                user_id=user_id,
                agent=agent,
            )

            if self._chat_manager is not None:
                await self._chat_manager.update_chat(chat)
        except Exception as e:
            logger.exception("Error in query handler: %s", e)
            raise

    async def init_handler(self, *args, **kwargs):
        """
        Init handler.
        """
        # Load environment variables from .env file
        env_path = Path(__file__).resolve().parents[4] / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            logger.debug(f"Loaded environment variables from {env_path}")
        else:
            logger.debug(
                f".env file not found at {env_path}, "
                "using existing environment variables",
            )

        session_dir = str(WORKING_DIR / "sessions")
        self.session = SafeJSONSession(save_dir=session_dir)

        # Initialize MCP clients from config
        await self._init_mcp_clients()

        try:
            if self.memory_manager is None:
                self.memory_manager = MemoryManager(
                    working_dir=str(WORKING_DIR),
                )
            await self.memory_manager.start()
        except Exception as e:
            logger.exception(f"MemoryManager start failed: {e}")

    async def shutdown_handler(self, *args, **kwargs):
        """
        Shutdown handler.
        """

        for name, client in self._mcp_clients.items():
            try:
                await client.close()
                logger.info(f"MCP server '{name}' closed")
            except Exception as e:
                logger.error(f"Error closing MCP client '{name}': {e}")
        self._mcp_clients.clear()

        try:
            await self.memory_manager.close()
        except Exception as e:
            logger.warning(f"MemoryManager stop failed: {e}")
