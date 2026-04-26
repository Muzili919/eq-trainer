"""豆包 TTS 服务 - 火山引擎语音合成 HTTP API"""

import base64
import logging
import uuid

import httpx

from app.core.config import settings

log = logging.getLogger(__name__)

TTS_URL = "https://openspeech.bytedance.com/api/v1/tts"

# 应用 emotion → 豆包 emotion
EMOTION_MAP: dict[str, str] = {
    "neutral": "",
    "annoyed": "annoyed",
    "sad": "sad",
    "warm": "comfort",
    "cold": "serious",
    "anxious": "scare",
    "smug": "tsundere",
    "angry": "angry",
    "happy": "happy",
    "surprised": "surprise",
}


async def synthesize(text: str, emotion: str = "neutral") -> bytes | None:
    """调用豆包 TTS，返回 mp3 bytes。失败返回 None。"""
    if not settings.volcengine_tts_appid or not settings.volcengine_tts_token:
        return None

    emo = EMOTION_MAP.get(emotion, "")
    audio_cfg: dict = {
        "voice_type": settings.volcengine_tts_voice,
        "encoding": "mp3",
        "speed_ratio": 1.05,
    }
    if emo:
        audio_cfg["emotion"] = emo

    payload = {
        "app": {
            "appid": settings.volcengine_tts_appid,
            "token": settings.volcengine_tts_token,
            "cluster": settings.volcengine_tts_cluster,
        },
        "user": {"uid": "eq-trainer"},
        "audio": audio_cfg,
        "request": {
            "reqid": uuid.uuid4().hex,
            "text": text[:500],
            "text_type": "plain",
            "operation": "query",
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                TTS_URL,
                json=payload,
                headers={"Authorization": f"Bearer;{settings.volcengine_tts_token}"},
            )
            data = resp.json()
            if data.get("code") == 3000 and data.get("data"):
                return base64.b64decode(data["data"])
            log.warning("TTS error: code=%s msg=%s", data.get("code"), data.get("message"))
    except Exception as e:
        log.warning("TTS call failed: %s", e)
    return None
