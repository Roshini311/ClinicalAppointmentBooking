import logging
import time
from sqlalchemy.orm import Session
from memory.persistent_memory import AppointmentRecord

logger = logging.getLogger("AppointmentEngine")

class AppointmentEngine:
    def __init__(self, db: Session):
        self.db = db
        # Simulating external database of booked slots for dynamic logic
        self.booked_slots = ["10 AM", "10:00 AM", "10:00"] 

    def check_availability(self, doctor: str, date: str, time_req: str, language: str = "English") -> tuple[bool, str, dict]:
        start = time.time()
        
        # Multilingual Conflict Logic
        conflict_msg = {
            "English": f"{time_req} is already booked. Available slots: 2 PM, 4 PM.",
            "Hindi": f"{time_req} पहले से बुक है। उपलब्ध स्लॉट: दोपहर 2 बजे, शाम 4 बजे।",
            "Tamil": f"{time_req} முன்பதிவு செய்யப்பட்டுள்ளது. நேரம்: 2 PM, 4 PM."
        }
        
        success_msg = {
            "English": f"The {doctor} is available at {time_req} on {date}.",
            "Hindi": f"{doctor} {date} को {time_req} बजे उपलब्ध हैं।",
            "Tamil": f"{date} அன்று {time_req} மணிக்கு {doctor} கிடைக்கும்."
        }
        
        # Explicit Conflict Handling Trigger
        if time_req and time_req in self.booked_slots:
            lat = time.time() - start
            return False, conflict_msg.get(language, conflict_msg["English"]), {"type": "tool", "name": "check_availability", "status": "slot_conflict", "latency": f"{lat*1000:.2f}ms", "conflict_slot": time_req}
            
        lat = time.time() - start
        return True, success_msg.get(language, success_msg["English"]), {"type": "tool", "name": "check_availability", "status": "success", "latency": f"{lat*1000:.2f}ms"}

    def book_appointment(self, user_id: int, doctor: str, date: str, time_req: str, language: str = "English") -> tuple[bool, str, dict]:
        start = time.time()
        
        # Fallbacks to prevent "None" appearing in the AI speech
        safe_doc = doctor if doctor else "doctor"
        safe_date = date if date else "a later date"
        safe_time = time_req if time_req else "a later time"
        
        record = AppointmentRecord(
            user_id=user_id,
            doctor_specialty=safe_doc,
            date=safe_date,
            time=safe_time,
            status="booked"
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        
        # Notice we explain IF we auto-selected a slot
        explanation = " (first available slot)" if "10:00 AM" == safe_time else ""
        
        book_msg = {
            "English": f"Your appointment with the {safe_doc} is confirmed for {safe_date} at {safe_time}{explanation}. ID is {record.id}.",
            "Hindi": f"{safe_doc} के साथ आपकी नियुक्ति {safe_date} को {safe_time}{explanation} पर पक्की हो गई है। आईडी {record.id} है।",
            "Tamil": f"{safe_doc} உடனான உங்கள் சந்திப்பு {safe_date} அன்று {safe_time}{explanation} மணிக்கு உறுதி செய்யப்பட்டது. ID {record.id}."
        }
        
        lat = time.time() - start
        return True, book_msg.get(language, book_msg["English"]), {"type": "tool", "name": "book_appointment", "status": "success", "latency": f"{lat*1000:.2f}ms", "appointment_id": record.id}

    def cancel_appointment(self, app_id: int, user_id: int, language: str = "English") -> tuple[bool, str, dict]:
        start = time.time()
        record = self.db.query(AppointmentRecord).filter(
            AppointmentRecord.id == app_id, 
            AppointmentRecord.user_id == user_id
        ).first()
        
        if not record:
            return False, "Could not find that appointment.", {"type": "tool", "name": "cancel_appointment", "status": "failed_not_found"}
            
        record.status = "cancelled"
        self.db.commit()
        
        cancel_msg = {
            "English": f"Your appointment ID {app_id} has been cancelled.",
            "Hindi": f"आपकी अपॉइंटमेंट आईडी {app_id} रद्द कर दी गई है।",
            "Tamil": f"உங்கள் சந்திப்பு ஐடி {app_id} ரத்துசெய்யப்பட்டது."
        }
        
        lat = time.time() - start
        return True, cancel_msg.get(language, cancel_msg["English"]), {"type": "tool", "name": "cancel_appointment", "status": "success", "latency": f"{lat*1000:.2f}ms"}
