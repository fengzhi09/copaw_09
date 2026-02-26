# -*- coding: utf-8 -*-
import logging
import os
from typing import Optional, Type, List, Sequence, Tuple, Any

from agentscope.agent import ReActAgent
from agentscope.agent._react_agent import _MemoryMark
from agentscope.formatter import OpenAIChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg, TextBlock
from agentscope.model import OpenAIChatModel
from agentscope.tool import Toolkit
from pydantic import BaseModel

from .prompt import (
    build_system_prompt_from_working_dir,
    build_bootstrap_guidance,
)
from .skills_manager import (
    ensure_skills_initialized,
    get_working_skills_dir,
    list_available_skills,
)
from .tools import (
    execute_shell_command,
    read_file,
    write_file,
    edit_file,
    send_file_to_user,
    desktop_screenshot,
    browser_use,
    create_memory_search_tool,
    get_current_time,
)
from .utils import (
    process_file_and_media_blocks_in_message,
    count_message_tokens,
    check_valid_messages,
    extract_tool_ids,
    is_first_user_interaction,
    prepend_to_message_content,
)
from ..agents.memory import MemoryManager
from ..config import load_config
from ..constant import (
    MEMORY_COMPACT_THRESHOLD,
    MEMORY_COMPACT_KEEP_RECENT,
    WORKING_DIR,
)
from ..providers import get_active_llm_config

logger = logging.getLogger(__name__)


def _reorder_tool_results(msgs: list) -> list:
    """Move tool_result messages right after their corresponding tool_use.

    Handles duplicate tool_call_ids by consuming results FIFO.
    """
    results_by_id: dict[str, list[object]] = {}
    result_msg_ids: set[int] = set()
    for msg in msgs:
        if isinstance(msg.content, list):
            for block in msg.content:
                if (
                    isinstance(block, dict)
                    and block.get("type") == "tool_result"
                    and block.get("id")
                ):
                    results_by_id.setdefault(block["id"], []).append(msg)
                    result_msg_ids.add(id(msg))

    consumed: dict[str, int] = {}
    reordered: list = []
    placed: set[int] = set()
    for msg in msgs:
        if id(msg) in result_msg_ids:
            continue
        reordered.append(msg)
        if not isinstance(msg.content, list):
            continue
        for block in msg.content:
            if not (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("id")
            ):
                continue
            bid = block["id"]
            candidates = results_by_id.get(bid, [])
            ci = consumed.get(bid, 0)
            if ci >= len(candidates):
                continue
            rm = candidates[ci]
            consumed[bid] = ci + 1
            if id(rm) not in placed:
                reordered.append(rm)
                placed.add(id(rm))

    return reordered


def _remove_unpaired_tool_messages(msgs: list) -> list:
    """Remove tool_use/tool_result messages that aren't properly paired.

    Each tool_use must be immediately followed by tool_results for all
    its IDs.  Unpaired messages and orphaned results are removed.
    """
    to_remove: set[int] = set()

    i = 0
    while i < len(msgs):
        use_ids, _ = extract_tool_ids(msgs[i])
        if not use_ids:
            i += 1
            continue
        required = set(use_ids)
        j = i + 1
        result_indices: list[int] = []
        while j < len(msgs) and required:
            _, r = extract_tool_ids(msgs[j])
            if not r:
                break
            required -= r
            result_indices.append(j)
            j += 1
        if required:
            to_remove.add(i)
            to_remove.update(result_indices)
            i += 1
        else:
            i = j  # skip past matched results

    surviving_use_ids: set[str] = set()
    for idx, msg in enumerate(msgs):
        if idx not in to_remove:
            u, _ = extract_tool_ids(msg)
            surviving_use_ids |= u
    for idx, msg in enumerate(msgs):
        if idx in to_remove:
            continue
        _, r = extract_tool_ids(msg)
        if r and not r.issubset(surviving_use_ids):
            to_remove.add(idx)

    return [msg for idx, msg in enumerate(msgs) if idx not in to_remove]


def _dedup_tool_blocks(msgs: list) -> list:
    """Remove duplicate tool_use blocks (same ID) within a single message."""
    changed = False
    result: list = []
    for msg in msgs:
        if not isinstance(msg.content, list):
            result.append(msg)
            continue
        seen_ids: set[str] = set()
        new_blocks: list = []
        deduped = False
        for block in msg.content:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("id")
            ):
                if block["id"] in seen_ids:
                    deduped = True
                    continue
                seen_ids.add(block["id"])
            new_blocks.append(block)
        if deduped:
            msg.content = new_blocks
            changed = True
        result.append(msg)
    return result if changed else msgs


def _sanitize_tool_messages(msgs: list) -> list:
    """Ensure tool_use/tool_result messages are properly paired and ordered.

    Returns the original list unchanged if no fix is needed.
    """
    msgs = _dedup_tool_blocks(msgs)

    # Fast check: single pass using counters to detect issues.
    pending: dict[str, int] = {}
    needs_fix = False
    for msg in msgs:
        msg_uses, msg_results = extract_tool_ids(msg)
        for rid in msg_results:
            if pending.get(rid, 0) <= 0:
                needs_fix = True
                break
            pending[rid] -= 1
            if pending[rid] == 0:
                del pending[rid]
        if needs_fix:
            break
        if pending and not msg_results:
            needs_fix = True
            break
        for uid in msg_uses:
            pending[uid] = pending.get(uid, 0) + 1
    if not needs_fix and not pending:
        return msgs

    logger.debug("Sanitizing tool messages: fixing order/pairing issues")
    return _remove_unpaired_tool_messages(_reorder_tool_results(msgs))


def create_file_block_support_formatter(base_formatter_class):
    """Factory function to add file block support to any Formatter class."""

    class FileBlockSupportFormatter(base_formatter_class):
        async def _format(self, msgs):
            """Override to sanitize tool messages before formatting,
            preventing OpenAI API errors."""
            msgs = _sanitize_tool_messages(msgs)
            return await super()._format(msgs)

        @staticmethod
        def convert_tool_result_to_string(
            output: str | List[dict],
        ) -> tuple[str, Sequence[Tuple[str, dict]]]:
            """Extend parent class to support file blocks.

            Uses try-first strategy for compatibility.
            """
            if isinstance(output, str):
                return output, []

            # Try parent class method first
            try:
                return base_formatter_class.convert_tool_result_to_string(
                    output,
                )
            except ValueError as e:
                if "Unsupported block type: file" not in str(e):
                    raise

                # Handle output containing file blocks
                textual_output = []
                multimodal_data = []

                for block in output:
                    if not isinstance(block, dict) or "type" not in block:
                        raise ValueError(
                            f"Invalid block: {block}, "
                            "expected a dict with 'type' key",
                        ) from e

                    if block["type"] == "file":
                        file_path = block.get("path", "") or block.get(
                            "url",
                            "",
                        )
                        file_name = block.get("name", file_path)

                        textual_output.append(
                            f"The returned file '{file_name}' "
                            f"can be found at: {file_path}",
                        )
                        multimodal_data.append((file_path, block))
                    else:
                        # Delegate other block types to parent class
                        (
                            text,
                            data,
                        ) = base_formatter_class.convert_tool_result_to_string(
                            [block],
                        )
                        textual_output.append(text)
                        multimodal_data.extend(data)

                if len(textual_output) == 0:
                    return "", multimodal_data
                elif len(textual_output) == 1:
                    return textual_output[0], multimodal_data
                else:
                    return (
                        "\n".join("- " + _ for _ in textual_output),
                        multimodal_data,
                    )

    FileBlockSupportFormatter.__name__ = (
        f"FileBlockSupport{base_formatter_class.__name__}"
    )
    return FileBlockSupportFormatter


# Create formatter with file block support
CoPawAgentFormatter = create_file_block_support_formatter(
    OpenAIChatFormatter,
)


class CoPawInMemoryMemory(InMemoryMemory):
    """bugfix"""

    async def get_memory(
        self,
        mark: str | None = None,
        exclude_mark: str | None = _MemoryMark.COMPRESSED,
        prepend_summary: bool = True,
        **kwargs: Any,
    ) -> list[Msg]:
        """Get the messages from the memory by mark (if provided)."""
        return await super().get_memory(
            mark=mark,
            exclude_mark=exclude_mark,
            prepend_summary=prepend_summary,
            **kwargs,
        )

    def get_compressed_summary(self) -> str:
        """Get the compressed summary of the memory."""
        return self._compressed_summary

    def state_dict(self) -> dict:
        """Get the state dictionary for serialization."""
        return {
            "content": [[msg.to_dict(), marks] for msg, marks in self.content],
            "_compressed_summary": self._compressed_summary,
        }

    def load_state_dict(self, state_dict: dict, strict: bool = True) -> None:
        """Load the state dictionary for deserialization."""
        if strict and "content" not in state_dict:
            raise KeyError(
                "The state_dict does not contain 'content' key required for "
                "InMemoryMemory.",
            )

        self.content = []
        for item in state_dict.get("content", []):
            if isinstance(item, (tuple, list)) and len(item) == 2:
                msg_dict, marks = item
                msg = Msg.from_dict(msg_dict)
                self.content.append((msg, marks))

            elif isinstance(item, dict):
                # For compatibility with older versions
                msg = Msg.from_dict(item)
                self.content.append((msg, []))

            else:
                raise ValueError(
                    "Invalid item format in state_dict for InMemoryMemory.",
                )

        self._compressed_summary = state_dict.get("_compressed_summary", "")


class CoPawAgent(ReActAgent):
    def __init__(
        self,
        env_context: Optional[str] = None,
        enable_memory_manager: bool = True,
        mcp_clients: Optional[List[Any]] = None,
        memory_manager: MemoryManager | None = None,
        agent_id: str = "00",
    ):
        """Initialize CoPawAgent.

        Args:
            env_context: Optional environment context
            enable_memory_manager: Whether to enable memory manager
            agent_id: Agent ID for loading specific config
        """
        self.agent_id = agent_id
        
        toolkit = Toolkit()
        self._mcp_clients = mcp_clients or []
        self._env_context = env_context
        toolkit.register_tool_function(execute_shell_command)
        toolkit.register_tool_function(read_file)
        toolkit.register_tool_function(write_file)
        toolkit.register_tool_function(edit_file)
        toolkit.register_tool_function(browser_use)
        # toolkit.register_tool_function(append_file)
        toolkit.register_tool_function(desktop_screenshot)
        toolkit.register_tool_function(send_file_to_user)
        toolkit.register_tool_function(get_current_time)

        # Check skills initialization
        ensure_skills_initialized()

        working_skills_dir = get_working_skills_dir()
        available_skills = list_available_skills()

        for skill_name in available_skills:
            skill_dir = working_skills_dir / skill_name
            if skill_dir.exists():
                try:
                    toolkit.register_agent_skill(str(skill_dir))
                    logger.debug("Registered skill: %s", skill_name)
                except Exception as e:
                    logger.error(
                        "Failed to register skill '%s': %s",
                        skill_name,
                        e,
                    )

        sys_prompt = self._build_sys_prompt()

        # Resolve model / api_key / base_url from the active LLM slot
        llm_cfg = get_active_llm_config()
        if llm_cfg and llm_cfg.api_key:
            model_name = llm_cfg.model or "qwen3-max"
            api_key = llm_cfg.api_key
            base_url = llm_cfg.base_url
        else:
            logger.warning(
                "No active LLM configured — "
                "falling back to DASHSCOPE_API_KEY env var",
            )
            model_name = "qwen3-max"
            api_key = os.getenv("DASHSCOPE_API_KEY", "")
            base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"

        super().__init__(
            name="Friday",
            model=OpenAIChatModel(
                model_name,
                api_key=api_key,
                stream=True,
                client_kwargs={"base_url": base_url},
            ),
            sys_prompt=sys_prompt,
            toolkit=toolkit,
            memory=CoPawInMemoryMemory(),
            formatter=CoPawAgentFormatter(),
        )
        self.memory_manager = memory_manager

        # Register memory_search tool if memory_manager is available
        if self.memory_manager is not None:
            memory_search_tool = create_memory_search_tool(self.memory_manager)
            self.toolkit.register_tool_function(memory_search_tool)
            logger.debug("Registered memory_search tool")

        self.register_instance_hook(
            hook_type="pre_reasoning",
            hook_name="bootstrap_hook",
            hook=CoPawAgent._pre_reasoning_bootstrap_hook,
        )
        logger.debug("Registered bootstrap hook")

        if enable_memory_manager and self.memory_manager is not None:
            self.register_instance_hook(
                hook_type="pre_reasoning",
                hook_name="memory_compact_hook",
                hook=CoPawAgent._pre_reasoning_compact_hook,
            )
            logger.debug("Registered memory compaction hook")

        self._bootstrap_checked = False

    def _build_sys_prompt(self) -> str:
        """Build system prompt from working dir files and env context."""
        # 首先尝试加载 Agent 专属配置
        agent_sys_prompt = self._load_agent_prompt(self.agent_id)
        if agent_sys_prompt:
            sys_prompt = agent_sys_prompt
        else:
            sys_prompt = build_system_prompt_from_working_dir()
        
        if self._env_context is not None:
            sys_prompt = self._env_context + "\n\n" + sys_prompt
        return sys_prompt
    
    def _load_agent_prompt(self, agent_id: str) -> str:
        """Load agent-specific system prompt."""
        import os
        from pathlib import Path
        
        # Agent 配置目录
        agent_dirs = [
            Path(__file__).parent / f"agent_{agent_id}_" / "system_prompt.md",
            Path(WORKING_DIR) / ".." / "agents" / f"agent_{agent_id}_" / "system_prompt.md",
            Path.home() / ".copaw" / "agents" / f"agent_{agent_id}_" / "system_prompt.md",
        ]
        
        for agent_dir in agent_dirs:
            if agent_dir.exists():
                try:
                    with open(agent_dir, "r", encoding="utf-8") as f:
                        logger.info(f"Loaded agent {agent_id} prompt from {agent_dir}")
                        return f.read()
                except Exception as e:
                    logger.warning(f"Failed to load agent prompt from {agent_dir}: {e}")
        
        return ""

    def rebuild_sys_prompt(self) -> None:
        """Rebuild and replace the system prompt.

        Useful after load_session_state to ensure the prompt reflects
        the latest AGENTS.md / SOUL.md / PROFILE.md on disk.

        Updates both ``self._sys_prompt`` and the first system-role
        message stored in ``self.memory.content`` (if one exists).
        """
        self._sys_prompt = self._build_sys_prompt()

        # Also update the first system prompt message in memory
        for msg, _marks in self.memory.content:
            if msg.role == "system":
                msg.content = self.sys_prompt
            # Stop after inspecting the first message regardless
            break

    async def register_mcp_clients(self) -> None:
        """Register MCP clients on this agent's toolkit after construction."""
        for client in self._mcp_clients:
            await self.toolkit.register_mcp_client(client)

    async def _pre_reasoning_bootstrap_hook(  # pylint: disable=unused-argument
        self,
        kwargs: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Check and load BOOTSTRAP.md on first user interaction."""
        if self._bootstrap_checked:
            return None

        self._bootstrap_checked = True

        try:
            bootstrap_path = WORKING_DIR / "BOOTSTRAP.md"
            if not bootstrap_path.exists():
                return None

            messages = await self.memory.get_memory()
            if not is_first_user_interaction(messages):
                return None

            config = load_config()
            language = config.agents.language
            bootstrap_content = bootstrap_path.read_text(encoding="utf-8")
            bootstrap_guidance = build_bootstrap_guidance(
                bootstrap_content,
                language,
            )

            logger.debug(
                "Found BOOTSTRAP.md [%s], prepending guidance",
                language,
            )

            system_prompt_count = sum(
                1 for msg in messages if msg.role == "system"
            )
            for msg in messages[system_prompt_count:]:
                if msg.role == "user":
                    prepend_to_message_content(msg, bootstrap_guidance)
                    break

            logger.debug("Bootstrap guidance prepended to first user message")

        except Exception as e:
            logger.error(
                "Failed to process bootstrap: %s",
                e,
                exc_info=True,
            )

        return None

    async def _pre_reasoning_compact_hook(  # pylint: disable=unused-argument
        self,
        kwargs: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Pre-reasoning hook to check and compact memory if needed.

        This hook is called before each reasoning step. It extracts system
        prompt messages (consecutive system messages at the start) and recent
        messages, then counts tokens for the middle compactable messages only.
        If the token count exceeds the threshold, it triggers compaction.

        Memory structure:
            [System Prompt (preserved)] + [Compactable (counted)] +
            [Recent (preserved)]

        Args:
            kwargs: Input arguments to the _reasoning method (not modified)

        Returns:
            None
        """
        # Only compact if memory manager is enabled
        if self.memory_manager is None:
            return None

        try:
            messages = await self.memory.get_memory(
                exclude_mark=_MemoryMark.COMPRESSED,
                prepend_summary=False,
            )

            logger.debug(f"===last message===: {messages[-1]}")

            # Extract system prompt (consecutive system messages at start)
            system_prompt_messages = []
            for msg in messages:
                if msg.role == "system":
                    system_prompt_messages.append(msg)
                else:
                    break

            # Get remaining messages after system prompt
            remaining_messages = messages[len(system_prompt_messages) :]

            # Skip if not enough messages to compact
            if len(remaining_messages) <= MEMORY_COMPACT_KEEP_RECENT:
                return None

            # ensure the messages_to_keep is valid
            keep_length = MEMORY_COMPACT_KEEP_RECENT
            while keep_length > 0 and not check_valid_messages(
                remaining_messages[-keep_length:],
            ):
                keep_length -= 1

            # Split into compactable and recent messages
            if keep_length > 0:
                messages_to_compact = remaining_messages[:-keep_length]
                messages_to_keep = remaining_messages[-keep_length:]
            else:
                messages_to_compact = remaining_messages
                messages_to_keep = []

            # Count tokens for compactable messages only
            prompt = await self.formatter.format(msgs=messages_to_compact)
            try:
                estimated_tokens: int = await count_message_tokens(prompt)
            except Exception as e:
                estimated_tokens = len(str(prompt)) // 4
                logger.exception(
                    f"Failed to count tokens: {e}\n"
                    f"using estimated_tokens={estimated_tokens}",
                )

            # Check if the compactable part exceeds threshold
            if estimated_tokens > MEMORY_COMPACT_THRESHOLD:
                logger.info(
                    "Memory compaction triggered: estimated %d tokens "
                    "(threshold: %d), system_prompt_msgs: %d, "
                    "compactable_msgs: %d, keep_recent_msgs: %d",
                    estimated_tokens,
                    MEMORY_COMPACT_THRESHOLD,
                    len(system_prompt_messages),
                    len(messages_to_compact),
                    len(messages_to_keep),
                )

                self.memory_manager.add_async_summary_task(
                    messages=messages_to_compact,
                )

                compact_content = await self.memory_manager.compact_memory(
                    messages_to_summarize=messages_to_compact,
                    previous_summary=self.memory.get_compressed_summary(),
                )

                await self.memory.update_compressed_summary(compact_content)
                updated_count = await self.memory.update_messages_mark(
                    new_mark=_MemoryMark.COMPRESSED,
                    msg_ids=[msg.id for msg in messages_to_compact],
                )
                logger.info(f"Marked {updated_count} messages as compacted")

        except Exception as e:
            logger.error(
                "Failed to compact memory in pre_reasoning hook: %s",
                e,
                exc_info=True,
            )

        return None

    async def reply(
        self,
        msg: Msg | list[Msg] | None = None,
        structured_model: Type[BaseModel] | None = None,
    ) -> Msg:
        """Override reply to process file and media blocks."""
        if msg is not None:
            await process_file_and_media_blocks_in_message(msg)

        if isinstance(msg, list):
            query = msg[-1].get_text_content()
        elif isinstance(msg, Msg):
            query = msg.get_text_content()
        else:
            query = None

        if isinstance(query, str) and query.strip() in [
            "/compact",
            "/new",
            "/clear",
            "/history",
        ]:
            logger.info(f"Received command: {query}")
            return await self.system_process(query)

        return await super().reply(msg=msg, structured_model=structured_model)

    async def system_process(self, query: str):
        messages = await self.memory.get_memory(
            exclude_mark=_MemoryMark.COMPRESSED,
            prepend_summary=False,
        )

        async def get_msg(text: str):
            _msg = Msg(
                name=self.name,
                role="assistant",
                content=[TextBlock(type="text", text=text)],
            )
            logger.debug(f"return msg: {_msg}")
            await self.print(_msg)
            return _msg

        if not messages:
            return await get_msg(
                "**No messages to process.**\n\n"
                "- Current memory is empty\n"
                "- No action taken",
            )

        logger.debug(f"Enter received command: {query}")
        if query == "/compact":
            self.memory_manager.add_async_summary_task(messages=messages)

            compact_content: str = await self.memory_manager.compact_memory(
                messages_to_summarize=messages,
                previous_summary=self.memory.get_compressed_summary(),
            )

            await self.memory.update_compressed_summary(compact_content)
            updated_count = await self.memory.update_messages_mark(
                new_mark=_MemoryMark.COMPRESSED,
                msg_ids=[msg.id for msg in messages],
            )
            logger.info(
                f"Marked {updated_count} messages as compacted with:\n"
                f"{compact_content}",
            )
            return await get_msg(
                f"**Compact Complete!**\n\n"
                f"- Messages compacted: {updated_count}\n"
                f"**Compressed Summary:**\n{compact_content}\n"
                f"- Summary task started in background\n",
            )

        elif query == "/new":
            self.memory_manager.add_async_summary_task(messages=messages)
            await self.memory.update_compressed_summary("")
            updated_count = await self.memory.update_messages_mark(
                new_mark=_MemoryMark.COMPRESSED,
                msg_ids=[msg.id for msg in messages],
            )
            logger.info(f"Marked {updated_count} messages as compacted")
            return await get_msg(
                "**New Conversation Started!**\n\n"
                "- Summary task started in background\n"
                "- Ready for new conversation",
            )

        elif query == "/clear":
            self.memory.content.clear()
            await self.memory.update_compressed_summary("")
            return await get_msg(
                "**History Cleared!**\n\n"
                "- Compressed summary reset\n"
                "- Memory is now empty",
            )

        elif query.startswith("/history"):

            def format_msg(idx: int, msg: Msg) -> str:
                try:
                    text = msg.get_text_content() or ""
                    preview = text[:100] + "..." if len(text) > 100 else text
                    return f"[{idx}] **{msg.role}**: {preview}"
                except Exception as e:
                    return f"[{idx}] **{msg.role}**: <error: {e}>"

            return await get_msg(
                f"**Conversation History**\n\n"
                f"- Total messages: {len(messages)}\n\n"
                + "\n".join(
                    format_msg(i + 1, msg) for i, msg in enumerate(messages)
                ),
            )

        else:
            raise RuntimeError(f"Unknown command: {query}")
