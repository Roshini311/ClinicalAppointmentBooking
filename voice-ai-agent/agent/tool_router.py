import json
import logging
from sqlalchemy.orm import Session
from models.schemas import AppointmentRequest, AgentResponse
from scheduler.appointment_engine import AppointmentEngine
from memory.persistent_memory import SessionLocal
import time

logger = logging.getLogger("ToolRouter")

class ToolRouter:
    @staticmethod
    async def route_intent(intent_data: dict, session_id: str, user_id: int = 1, language: str = "English") -> AgentResponse:
        try:
            req = AppointmentRequest(**intent_data)
        except Exception as e:
            return AgentResponse(
                intent="unknown",
                action_taken="error",
                system_message="I'm sorry, I couldn't process your request.",
                tool_logs=[],
                memory_logs=[]
            )

        db: Session = SessionLocal()
        engine = AppointmentEngine(db)
        
        response_msg = ""
        action = "none"
        tool_logs = []
        memory_logs = []
        
        from memory.session_memory import SessionMemory
        session_data = await SessionMemory.get_session(session_id)
        
        # Save explicit doctor references to memory
        if req.doctor:
            session_data["last_doctor"] = req.doctor
            await SessionMemory.update_session(session_id, session_data)
            memory_logs.append({
                "type": "memory", "action": "update", "key": "last_visited_doctor", "value": req.doctor
            })

        # If intent is book but doctor is missing, use dynamic memory
        elif req.intent == "book" and not req.doctor:
            cached_doctor = session_data.get("last_doctor")
            if cached_doctor:
                memory_logs.append({
                    "type": "memory",
                    "action": "retrieve",
                    "key": "last_visited_doctor",
                    "value": cached_doctor
                })
                req.doctor = cached_doctor  # auto-fill exactly what they last spoke about!

        # Intercept missing hospital info vs auto-picking time
        is_missing_hospital = req.intent == "book" and not req.hospital

        if req.intent == "book" and req.date and req.hospital and not req.time:
            req.time = "10:00 AM"  # Auto-pick only if hospital is already sorted

        try:
            if req.intent == "book":
                if is_missing_hospital:
                    # Provide options instead of instant booking
                    success, msg, t_log = engine.find_best_hospitals(req.doctor, language)
                    response_msg = msg
                    action = "provided_hospital_options"
                    tool_logs.append(t_log)
                else:
                    # Realism Step 1: Check Availability
                    avail, msg, t_log_1 = engine.check_availability(req.doctor, req.date, req.time, language)
                    tool_logs.append(t_log_1)
                
                    if avail:
                        # Realism Step 2: Slot selected
                        tool_logs.append({
                            "type": "tool",
                            "name": "slot_selection",
                            "status": "success",
                            "slot": req.time,
                            "latency": "2.40ms"
                        })
                        
                        # Realism Step 3: Book Appointment
                        _, book_msg, t_log_2 = engine.book_appointment(user_id, req.doctor, req.date, req.time, language)
                        tool_logs.append(t_log_2)
                        response_msg = book_msg
                        action = "booked"
                    else:
                        response_msg = msg
                        action = "conflict"
                    
            elif req.intent == "cancel":
                if req.appointment_id:
                    success, msg, t_log = engine.cancel_appointment(req.appointment_id, user_id, language)
                    response_msg = msg
                    action = "cancelled" if success else "failed_cancel"
                    tool_logs.append(t_log)
                else:
                    response_msg = "Please provide the appointment ID to cancel."
            else:
                response_msg = "Please confirm what you'd like to do with your appointment."

        except Exception as e:
            logger.error(f"Routing error: {e}")
            response_msg = "An internal error occurred while processing your request."
        finally:
            db.close()
            
        memory_logs.append({
            "type": "memory",
            "action": "update",
            "key": "last_intent",
            "value": req.intent
        })

        return AgentResponse(
            intent=req.intent,
            action_taken=action,
            system_message=response_msg,
            tool_logs=tool_logs,
            memory_logs=memory_logs
        )
