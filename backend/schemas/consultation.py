from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SymptomInput(BaseModel):
    symptoms: List[str]
    additional_info: Optional[str] = None


class AnalysisResponse(BaseModel):
    consultation_id: int
    severity_score: float
    risk_level: str
    orientation: str
    explanation: str
    disclaimer: str = (
        "⚠️ Ce résultat est une orientation non médicale. "
        "Consultez toujours un professionnel de santé."
    )

    class Config:
        from_attributes = True


class ConsultationResponse(BaseModel):
    id: int
    date: datetime
    status: str
    raw_input: Optional[str]
    analysis: Optional[AnalysisResponse]

    class Config:
        from_attributes = True


class ChatMessageInput(BaseModel):
    consultation_id: int
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_consultations: int
    urgences_count: int
    medecin_count: int
    surveillance_count: int
    avg_severity_score: float