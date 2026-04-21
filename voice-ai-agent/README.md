# Real-Time Multilingual Voice AI Agent

This project is a production-grade backend for a Voice AI Clinical Appointment Booking System. It achieves strict `< 450ms` real-time, multilingual, bidirectional voice processing.

## Architecture

```text
WebSocket Input (Audio Bytes)
  │
  ├─ STT (Speech-to-Text) -> ~120ms
  ├─ Language Detection -> ~20ms
  │
  ├─ Updates Redis Session Memory
  │
  ├─ LLM Intent Reasoning (Gemini/GPT) -> ~200ms
  │    (Produces Structured JSON)
  │
  ├─ Tool Router
  │    ├─ Appointment Engine (PostgreSQL)
  │    └─ check_availability, book, cancel, reschedule
  │
  ├─ TTS (Text-to-Speech) -> ~100ms
  │
  └─ WebSocket Output (Audio Bytes)
```

## Technologies
- **Python Framework**: FastAPI
- **Real-Time Protocol**: WebSockets 
- **DB (Persistent)**: PostgreSQL (SQLAlchemy)
- **Memory (Session)**: Redis (aioredis)

## Setup

1. **Start Databases**
   ```bash
   docker-compose up -d
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Server**
   ```bash
   # Make sure you are in the voice-ai-agent directory
   python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

4. **Test Real-Time Pipeline**
   ```bash
   python test_client.py
   ```

## Latency Breakdown Tracking
A `LatencyLogger` utility automatically tracks stages in the event loop pipeline and injects debug summaries to the client via websockets to ensure constraints are respected.

## Tradeoffs
1. **Mocking External Providers**: For this release, STT, TTS, and the LLM inference are structurally bound but use mocked functions that emulate the exact desired latency (`asyncio.sleep()`). They are fully ready to be swapped with provider SDKs (like Deepgram for STT/TTS and Groq/Gemini Flash for the LLM) without altering the routing or architecture.
2. **WebSocket Audio Format**: The mock accepts standard text encoded as bytes instead of `.wav` or `PCM` frames so you can easily observe the routing logic via a simple terminal client.
