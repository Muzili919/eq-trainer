"""DeepSeek LLM 调用封装 - 统一接口，便于切换模型/Mock 测试"""

import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI, OpenAI

from app.core.config import settings

log = logging.getLogger(__name__)

MAX_RETRIES = 2


class LLMClient:
    """同步调用，简单 service 用"""

    def __init__(self):
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    def chat_json(self, system: str, user: str, temperature: float = 0.7) -> dict[str, Any]:
        """要求 LLM 输出 JSON。带重试 + 容错"""
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=max(0.3, temperature - attempt * 0.2),
                    response_format={"type": "json_object"},
                )
                text = resp.choices[0].message.content or "{}"
                result = _extract_json(text)
                if not result.get("_parse_error"):
                    return result
                log.warning("LLM JSON parse failed (attempt %d): %s", attempt + 1, text[:100])
            except Exception as e:
                log.warning("LLM call failed (attempt %d): %s", attempt + 1, e)
        return {}

    def chat_text(self, system: str, user: str, temperature: float = 0.7) -> str:
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=max(0.3, temperature - attempt * 0.2),
                )
                text = resp.choices[0].message.content or ""
                if text.strip():
                    return text
            except Exception as e:
                log.warning("LLM chat_text failed (attempt %d): %s", attempt + 1, e)
        return ""


class AsyncLLMClient:
    """异步调用，FastAPI 路由直接 await"""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    async def chat_json(self, system: str, user: str, temperature: float = 0.7) -> dict[str, Any]:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=max(0.3, temperature - attempt * 0.2),
                    response_format={"type": "json_object"},
                )
                text = resp.choices[0].message.content or "{}"
                result = _extract_json(text)
                if not result.get("_parse_error"):
                    return result
                log.warning("Async LLM JSON parse failed (attempt %d): %s", attempt + 1, text[:100])
            except Exception as e:
                log.warning("Async LLM call failed (attempt %d): %s", attempt + 1, e)
        return {}

    async def chat_text(self, system: str, user: str, temperature: float = 0.7) -> str:
        for attempt in range(MAX_RETRIES):
            try:
                resp = await self._client.chat.completions.create(
                    model=settings.deepseek_model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=max(0.3, temperature - attempt * 0.2),
                )
                text = resp.choices[0].message.content or ""
                if text.strip():
                    return text
            except Exception as e:
                log.warning("Async LLM chat_text failed (attempt %d): %s", attempt + 1, e)
        return ""


def _extract_json(text: str) -> dict[str, Any]:
    """从 LLM 输出中提取 JSON。先尝试整体 parse，失败则提取 {...} 块"""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 兜底
    return {"_raw": text, "_parse_error": True}


# 单例
_sync_client: LLMClient | None = None
_async_client: AsyncLLMClient | None = None


def get_sync_llm() -> LLMClient:
    global _sync_client
    if _sync_client is None:
        _sync_client = LLMClient()
    return _sync_client


def get_async_llm() -> AsyncLLMClient:
    global _async_client
    if _async_client is None:
        _async_client = AsyncLLMClient()
    return _async_client
