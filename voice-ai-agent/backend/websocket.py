import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from services.stt import speech_to_text
from services.tts import text_to_speech
from services.language_detection import detect_language
from agent.reasoning import ReasoningAgent
from agent.tool_router import ToolRouter
from memory.session_memory import SessionMemory
from utils.latency_logger import LatencyLogger

logger = logging.getLogger("WebSocket")
router = APIRouter()

# Outbound Trigger Example Route
@router.post("/outbound_call")
async def trigger_outbound():
    # In a real app this uses background tasks and initiates call via Twilio/etc
    return {"message": "Outbound call triggered in background"}

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"Session {session_id} connected")
    user_id = 1 

    try:
        while True:
            data = await websocket.receive_bytes()
            # If the UI sends a magic byte string to kick off outbound mock
            if data == b"TRIGGER_OUTBOUND":
                await websocket.send_json({
                    "type": "outbound_log", 
                    "message": "[Outbound] Calling patient... \nAgent: 'Reminder: You have an appointment tomorrow with the Dentist.'"
                })
                continue
                
            latency = LatencyLogger()
            latency.start()
            
            # 1. STT
            user_text = await speech_to_text(data)
            latency.mark("STT")
            
            # 2. Language Detection 
            lang = await detect_language(data)
            await websocket.send_json({"type": "language_detected", "language": lang})
            await SessionMemory.set_language(session_id, lang)
            latency.mark("LanguageDetection")
            
            await SessionMemory.add_message(session_id, "user", user_text)
            
            # 3. Intent Parser
            intent_json = await ReasoningAgent.parse_intent(user_text)
            latency.mark("IntentParser")
            
            # Send full logic trace to UI
            await websocket.send_json({"type": "reasoning_trace", "data": {
                "detected": intent_json.get("intent", "unknown"),
                "extracted": f"{intent_json.get('doctor')} on {intent_json.get('date')}",
                "action": "evaluating tool dependencies"
            }})
            
            # 4. Tool Router 
            # Note: route_intent is now async to pull from real dynamic cache!
            agent_response = await ToolRouter.route_intent(intent_json, session_id=session_id, user_id=user_id, language=lang)
            latency.mark("ToolRouting")
            
            await websocket.send_json({"type": "reasoning_trace", "data": {
                "detected": intent_json.get("intent", "unknown"),
                "extracted": f"{intent_json.get('doctor')} on {intent_json.get('date')}",
                "action": agent_response.action_taken,
                "status": "decision finalized"
            }})
            
            await SessionMemory.add_message(session_id, "system", agent_response.system_message)
            
            # Flush Logs to UI
            for tlog in agent_response.tool_logs:
                await websocket.send_json({"type": "tool_log", "data": tlog})
            for mlog in agent_response.memory_logs:
                await websocket.send_json({"type": "memory_log", "data": mlog})
            
            # 5. TTS
            audio_response = await text_to_speech(agent_response.system_message, lang)
            latency.mark("TTS")
            
            await websocket.send_bytes(audio_response)
            
            # Metrics
            summary = latency.get_summary()
            summary["Action"] = agent_response.action_taken
            summary["Text"] = agent_response.system_message
            await websocket.send_json({"type": "debug_latency", "summary": summary})
            latency.log_summary()

    except WebSocketDisconnect:
        logger.info(f"Session {session_id} disconnected")
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass
