import asyncio
import logging
import time

logger = logging.getLogger("LanguageDetection")

async def detect_language(audio_bytes: bytes) -> str:
    """
    Lightweight deterministic language classification based on Unicode script blocks. 
    This avoids massive LLM token overhead during initial request categorization.
    """
    start = time.time()
    
    # Simulating standard buffer processing latency
    await asyncio.sleep(0.02)
    
    try:
        text = audio_bytes.decode('utf-8')
    except:
        return "English" # fallback

    language = "English"
    for char in text:
        code = ord(char)
        # Devanagari block (Hindi)
        if 0x0900 <= code <= 0x097F:
            language = "Hindi"
            break
        # Tamil block
        elif 0x0B80 <= code <= 0x0BFF:
            language = "Tamil"
            break

    latency = time.time() - start
    logger.info(f"Language detection latency: {latency*1000:.2f}ms")
    return language
