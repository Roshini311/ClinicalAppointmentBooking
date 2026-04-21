import asyncio
import logging

logger = logging.getLogger("TTS_Service")

async def text_to_speech(text: str, language: str = "English") -> bytes:
    """
    Simulates Text-to-Speech via a fast provider (e.g. Deepgram/Cartesia).
    Expected latency to first byte: < 100ms.
    """
    # Simulate API latency (~80ms first byte)
    await asyncio.sleep(0.08)
    
    # Mock behavior: return the text encoded as bytes instead of actual mp3/wav
    # For a real pipeline, you would stream audio bytes
    return f"[AUDIO BYTE STREAM for: {text}]".encode('utf-8')
