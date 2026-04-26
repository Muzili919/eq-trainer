"""DeepSeek LLM 调用封装 - 统一接口，便于切换模型/Mock 测试"""

import json
import re
from typing import Any

from openai import AsyncOpenAI, OpenAI

from app.core.config import settings


class LLMClient:
    """同步调用，简单 service 用"""

    def __init__(self):
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    def chat_json(self, system: str, user: str, temperature: float = 0.7) -> dict[str, Any]:
        """要求 LLM 输出 JSON。带容错 - DeepSeek V4 偶尔输出多余文本"""
        resp = self._client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or "{}"
        return _extract_json(text)

    def chat_text(self, system: str, user: str, temperature: float = 0.7) -> str:
        resp = self._client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""


class AsyncLLMClient:
    """异步调用，FastAPI 路由直接 await"""

    def __init__(self):
        self._client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

    async def chat_json(self, system: str, user: str, temperature: float = 0.7) -> dict[str, Any]:
        resp = await self._client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or "{}"
        return _extract_json(text)


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
