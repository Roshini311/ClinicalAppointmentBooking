import asyncio
import logging
import time
import re

logger = logging.getLogger("LLM_Reasoning")

class ReasoningAgent:
    @staticmethod
    async def parse_intent(user_text: str) -> dict:
        """
        Lightweight deterministic intent parser replacing a heavy LLM 
        for extreme latency optimization and strict tool execution SLA.
        """
        start = time.time()
        
        # Simulating external NLP service/regex inference computation delay
        await asyncio.sleep(0.05)
        
        text_lower = user_text.lower()
        
        intent = "unknown"
        doctor = None
        date = None
        time_req = None
        app_id = None
        
        # Regex / Keyword Extraction replacing LLM tokenization
        # Expanded to cover transliterated (roman) Hindi and Tamil phrases
        cancel_keywords = ["cancel", "रद्द", "ரத்து", "cancel pannanum"]
        book_keywords = ["book", "मिलना", "பார்க்க", "vendum", "appointment", "chahiye"]
        
        if any(k in text_lower for k in cancel_keywords):
            intent = "cancel"
            app_id = 1
        elif any(k in text_lower for k in book_keywords):
            intent = "book"
            
        doctor_keywords = ["doctor", "चिकित्सक", "மருத்துவர்"]
        if "dentist" in text_lower or "दंत" in text_lower or "பல்" in text_lower:
            doctor = "dentist"
        elif "cardio" in text_lower:
            doctor = "cardiologist"
        elif any(k in text_lower for k in doctor_keywords):
            doctor = "doctor"
            
        # Date Extraction via Regex (e.g. 28th april, tomorrow)
        if "tomorrow" in text_lower or "कल" in text_lower or "நாளை" in text_lower:
            date = "tomorrow"
        elif "today" in text_lower or "aaj" in text_lower or "இன்று" in text_lower:
            date = "today"
        elif "friday" in text_lower or "शुक्रवार" in text_lower or "வெள்ளிக்" in text_lower:
            date = "friday"
        else:
            # Match formats like '28th april', '15 may', 'april 28'
            date_match = re.search(r'(\d{1,2}(?:st|nd|rd|th)?\s*[a-z]+|[a-z]+\s*\d{1,2}(?:st|nd|rd|th)?)', text_lower)
            if date_match:
                date = date_match.group(1).strip()
            
        # Time Extraction via Regex (e.g. 10 am, 2:30 pm)
        time_match = re.search(r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))', text_lower)
        if time_match:
            time_req = time_match.group(1).strip().upper()
        elif "10" in text_lower:
            time_req = "10:00 AM"

        result = {
            "intent": intent,
            "doctor": doctor,
            "date": date,
            "time": time_req,
            "appointment_id": app_id
        }
        
        end_time = time.time()
        latency = end_time - start
        logger.info(f"Intent Parser computation latency: {latency*1000:.2f}ms")
        
        return result
