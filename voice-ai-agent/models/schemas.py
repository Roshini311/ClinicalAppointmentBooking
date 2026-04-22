from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class AppointmentRequest(BaseModel):
    intent: str = Field(description="The generic intent, e.g., 'book', 'reschedule', 'cancel', 'check_availability', 'unknown'")
    doctor: Optional[str] = Field(None, description="Type of doctor, e.g., 'cardiologist', 'dentist'")
    hospital: Optional[str] = None
    date: Optional[str] = Field(None, description="Requested date")
    time: Optional[str] = Field(None, description="Requested time")
    appointment_id: Optional[int] = Field(None, description="Required for reschedule or cancel")

class AgentResponse(BaseModel):
    intent: str
    action_taken: str
    system_message: str
    tool_logs: List[Dict[str, Any]] = []
    memory_logs: List[Dict[str, Any]] = []

class Appointment(BaseModel):
    id: int
    patient_id: int
    doctor_specialty: str
    date: str
    time: str
    status: str
