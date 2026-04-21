import asyncio
import logging

logger = logging.getLogger("STT_Service")

async def speech_to_text(audio_bytes: bytes) -> str:
    """
    Simulates Speech-to-Text via a fast provider (e.g. Groq Whisper).
    Expected latency: ~120ms.
    """
    # Simulate API latency (~80ms streaming simulation)
    await asyncio.sleep(0.08)
    
    # Mock behavior. If audio_bytes is string encoded for testing, we just return it.
    try:
        text = audio_bytes.decode('utf-8')
        # Simple mock scenarios based on text
        return text
    except:
        return "Book appointment with cardiologist tomorrow"
