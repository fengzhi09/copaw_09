# -*- coding: utf-8 -*-
"""Built-in provider definitions and registry."""

from __future__ import annotations

from typing import List, Optional

from .models import ModelInfo, ProviderDefinition

# ---------------------------------------------------------------------------
# Built-in LLM model lists
# ---------------------------------------------------------------------------

MODELSCOPE_MODELS: List[ModelInfo] = [
    ModelInfo(
        id="Qwen/Qwen3-235B-A22B-Instruct-2507",
        name="Qwen3-235B-A22B-Instruct-2507",
    ),
    ModelInfo(id="deepseek-ai/DeepSeek-V3.2", name="DeepSeek-V3.2"),
]

DASHSCOPE_MODELS: List[ModelInfo] = [
    ModelInfo(id="qwen3-max", name="Qwen3 Max"),
    ModelInfo(
        id="qwen3-235b-a22b-thinking-2507",
        name="Qwen3 235B A22B Thinking",
    ),
    ModelInfo(id="deepseek-v3.2", name="DeepSeek-V3.2"),
    ModelInfo(id="qwen-turbo", name="Qwen Turbo"),
    ModelInfo(id="qwen-plus", name="Qwen Plus"),
    ModelInfo(id="qwen-max-longcontext", name="Qwen Max LongContext"),
]

MINIMAX_MODELS: List[ModelInfo] = [
    ModelInfo(id="MiniMax-M2.5-long", name="MiniMax M2.5 Long"),
    ModelInfo(id="MiniMax-M2.5-highspeed", name="MiniMax M2.5 Highspeed"),
    ModelInfo(id="MiniMax-M2.1", name="MiniMax M2.1"),
    ModelInfo(id="abab6.5s-chat", name="ABAB6.5S Chat"),
    ModelInfo(id="abab6.5g-chat", name="ABAB6.5G Chat"),
]

ZHIPU_MODELS: List[ModelInfo] = [
    ModelInfo(id="glm-5", name="GLM-5"),
    ModelInfo(id="glm-4-flash", name="GLM-4 Flash"),
    ModelInfo(id="glm-4-plus", name="GLM-4 Plus"),
    ModelInfo(id="glm-4", name="GLM-4"),
    ModelInfo(id="glm-3-turbo", name="GLM-3 Turbo"),
    ModelInfo(id="glm-4v-flash", name="GLM-4V Flash"),
    ModelInfo(id="glm-4v-plus", name="GLM-4V Plus"),
]

OPENROUTER_MODELS: List[ModelInfo] = [
    ModelInfo(id="openai/gpt-4o", name="GPT-4O"),
    ModelInfo(id="openai/gpt-4o-mini", name="GPT-4O Mini"),
    ModelInfo(id="anthropic/claude-3.5-sonnet", name="Claude 3.5 Sonnet"),
    ModelInfo(id="google/gemini-2.0-flash-exp", name="Gemini 2.0 Flash"),
    ModelInfo(id="meta-llama/llama-3.3-70b-instruct", name="Llama 3.3 70B"),
    ModelInfo(id="deepseek/deepseek-chat", name="DeepSeek Chat"),
]

NVIDIA_MODELS: List[ModelInfo] = [
    ModelInfo(id="nvidia/llama-3.3-70b-instruct", name="Llama 3.3 70B Instruct"),
    ModelInfo(id="nvidia/nemotron-70b-instruct", name="Nemotron 70B Instruct"),
    ModelInfo(id="nvidia/llama-3.1-70b-instruct", name="Llama 3.1 70B Instruct"),
    ModelInfo(id="nvidia/mistral-7b-instruct-v2", name="Mistral 7B Instruct V2"),
]

OPENAI_MODELS: List[ModelInfo] = [
    ModelInfo(id="gpt-4o", name="GPT-4O"),
    ModelInfo(id="gpt-4o-mini", name="GPT-4O Mini"),
    ModelInfo(id="gpt-4-turbo", name="GPT-4 Turbo"),
    ModelInfo(id="gpt-3.5-turbo", name="GPT-3.5 Turbo"),
    ModelInfo(id="o1", name="O1"),
    ModelInfo(id="o1-mini", name="O1 Mini"),
    ModelInfo(id="o3-mini", name="O3 Mini"),
]

DEEPSEEK_MODELS: List[ModelInfo] = [
    ModelInfo(id="deepseek-chat", name="DeepSeek Chat"),
    ModelInfo(id="deepseek-coder", name="DeepSeek Coder"),
]

# ---------------------------------------------------------------------------
# Provider definitions
# ---------------------------------------------------------------------------

PROVIDER_MODELSCOPE = ProviderDefinition(
    id="modelscope",
    name="ModelScope",
    default_base_url="https://api-inference.modelscope.cn/v1",
    api_key_prefix="ms",
    models=MODELSCOPE_MODELS,
)

PROVIDER_DASHSCOPE = ProviderDefinition(
    id="dashscope",
    name="DashScope",
    default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    api_key_prefix="sk",
    models=DASHSCOPE_MODELS,
)

PROVIDER_MINIMAX = ProviderDefinition(
    id="minimax",
    name="MiniMax",
    default_base_url="https://api.minimax.io/v1",
    api_key_prefix="sk",
    models=MINIMAX_MODELS,
)

PROVIDER_ZHIPU = ProviderDefinition(
    id="zhipu",
    name="Zhipu AI",
    default_base_url="https://open.bigmodel.cn/api/paas/v4",
    api_key_prefix="",
    models=ZHIPU_MODELS,
)

PROVIDER_OPENROUTER = ProviderDefinition(
    id="openrouter",
    name="OpenRouter",
    default_base_url="https://openrouter.ai/v1",
    api_key_prefix="sk-or-",
    models=OPENROUTER_MODELS,
)

PROVIDER_NVIDIA = ProviderDefinition(
    id="nvidia",
    name="NVIDIA",
    default_base_url="https://integrate.api.nvidia.com/v1",
    api_key_prefix="nv-",
    models=NVIDIA_MODELS,
)

PROVIDER_OPENAI = ProviderDefinition(
    id="openai",
    name="OpenAI",
    default_base_url="https://api.openai.com/v1",
    api_key_prefix="sk-",
    models=OPENAI_MODELS,
)

PROVIDER_DEEPSEEK = ProviderDefinition(
    id="deepseek",
    name="DeepSeek",
    default_base_url="https://api.deepseek.com/v1",
    api_key_prefix="sk-",
    models=DEEPSEEK_MODELS,
)

PROVIDER_CUSTOM = ProviderDefinition(
    id="custom",
    name="Custom",
    default_base_url="",
    api_key_prefix="",
    models=[],
    allow_custom_base_url=True,
)

# Registry: provider_id -> ProviderDefinition
PROVIDERS: dict[str, ProviderDefinition] = {
    PROVIDER_MODELSCOPE.id: PROVIDER_MODELSCOPE,
    PROVIDER_DASHSCOPE.id: PROVIDER_DASHSCOPE,
    PROVIDER_MINIMAX.id: PROVIDER_MINIMAX,
    PROVIDER_ZHIPU.id: PROVIDER_ZHIPU,
    PROVIDER_OPENROUTER.id: PROVIDER_OPENROUTER,
    PROVIDER_NVIDIA.id: PROVIDER_NVIDIA,
    PROVIDER_OPENAI.id: PROVIDER_OPENAI,
    PROVIDER_DEEPSEEK.id: PROVIDER_DEEPSEEK,
    PROVIDER_CUSTOM.id: PROVIDER_CUSTOM,
}


def get_provider(provider_id: str) -> Optional[ProviderDefinition]:
    """Return a provider definition by id, or None if not found."""
    return PROVIDERS.get(provider_id)


def list_providers() -> List[ProviderDefinition]:
    """Return all registered provider definitions."""
    return list(PROVIDERS.values())
