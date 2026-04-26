"""TTS 路由 - /api/v1/tts"""

from fastapi import APIRouter, Query
from fastapi.responses import Response

from app.services.tts import synthesize

router = APIRouter(prefix="/tts", tags=["tts"])


@router.get("")
async def tts_endpoint(
    text: str = Query(..., max_length=500),
    emotion: str = Query("neutral"),
):
    audio = await synthesize(text, emotion)
    if audio:
        return Response(content=audio, media_type="audio/mpeg")
    return Response(status_code=204)
