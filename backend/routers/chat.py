from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional
from groq import Groq
from models.user import User
from services.auth_service import get_current_user
from config import get_settings
from services.metrics_service import track_chat_message


settings = get_settings()
router   = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatMessageSchema(BaseModel):
    role:    str
    content: str


class ChatRequest(BaseModel):
    message:         str
    history:         List[ChatMessageSchema] = []
    symptoms:        Optional[List[str]]     = []
    analysis_result: Optional[dict]          = None


class ChatResponse(BaseModel):
    response: str


@router.post("/message", response_model=ChatResponse)
def send_message(
    data: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    client  = Groq(api_key=settings.GROQ_API_KEY)
    context = ""
    if data.symptoms:
        context += f"Symptômes : {', '.join(data.symptoms)}. "
    if data.analysis_result:
        context += f"Orientation : {data.analysis_result.get('orientation', '')}. "
        context += f"Score : {data.analysis_result.get('severity_score', '')}/100."

    messages = [{
        "role":    "system",
        "content": f"Tu es MediAssist, assistant médical bienveillant. "
                   f"Tu réponds en français. Tu ne poses PAS de diagnostic. "
                   f"Contexte patient : {context}"
    }]
    for msg in data.history[-10:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": data.message})

    response = client.chat.completions.create(
        model       = settings.GROQ_MODEL,
        messages    = messages,
        temperature = 0.5,
        max_tokens  = 400
    )


    return ChatResponse(response=response.choices[0].message.content)


@router.post("/initial", response_model=ChatResponse)
def initial_message(
    data: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    client      = Groq(api_key=settings.GROQ_API_KEY)
    orientation = data.analysis_result.get("orientation", "medecin") if data.analysis_result else "medecin"
    score       = data.analysis_result.get("severity_score", 50)     if data.analysis_result else 50
    symptoms    = data.symptoms or []

    prompt = f"""Symptômes : {', '.join(symptoms)}.
Orientation : {orientation}. Score : {score}/100.
Génère un message d'accueil court (2-3 phrases) en français qui :
1. Résume l'orientation
2. Propose de répondre aux questions
Ne pose pas de diagnostic."""

    response = client.chat.completions.create(
        model       = settings.GROQ_MODEL,
        messages    = [{"role": "user", "content": prompt}],
        temperature = 0.4,
        max_tokens  = 200
    )

    track_chat_message()

    return ChatResponse(response=response.choices[0].message.content)