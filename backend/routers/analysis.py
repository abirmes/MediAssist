from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.consultation import Consultation, Analysis
from schemas.consultation import SymptomInput, AnalysisResponse, ConsultationResponse
from services.auth_service import get_current_user
from services.ml_service import predict_orientation
from services.chat_service import generate_explanation
from typing import List
from services.metrics_service import track_prediction


router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_symptoms(
    data: SymptomInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyse les symptômes et retourne une orientation médicale."""
    if not data.symptoms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez fournir au moins un symptôme"
        )

    # Créer une consultation
    consultation = Consultation(
        user_id=current_user.id,
        raw_input=", ".join(data.symptoms),
        status="analyzing"
    )
    db.add(consultation)
    db.commit()
    db.refresh(consultation)

    # Prédiction ML
    ml_result = predict_orientation(data.symptoms)
    track_prediction(
    orientation=ml_result["orientation"],
    severity_score=ml_result["severity_score"]
)

    # Génération explication via Groq
    try:
        explanation = generate_explanation(
            ml_result["orientation"],
            data.symptoms,
            ml_result["severity_score"]
        )
    except Exception:
        explanation = get_default_explanation(ml_result["orientation"])

    # Sauvegarder l'analyse
    analysis = Analysis(
        consultation_id=consultation.id,
        severity_score=ml_result["severity_score"],
        risk_level=ml_result["risk_level"],
        orientation=ml_result["orientation"],
        explanation=explanation
    )
    db.add(analysis)
    consultation.status = "analyzed"
    db.commit()
    db.refresh(analysis)

    return AnalysisResponse(
        consultation_id=consultation.id,
        severity_score=ml_result["severity_score"],
        risk_level=ml_result["risk_level"],
        orientation=ml_result["orientation"],
        explanation=explanation
    )


@router.get("/symptoms", response_model=List[str])
def get_symptoms():
    """Retourne la liste de tous les symptômes disponibles."""
    from services.ml_service import get_symptom_list
    return get_symptom_list()


@router.get("/history", response_model=List[ConsultationResponse])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retourne l'historique des consultations de l'utilisateur."""
    consultations = db.query(Consultation).filter(
        Consultation.user_id == current_user.id
    ).order_by(Consultation.date.desc()).all()
    return consultations


def get_default_explanation(orientation: str) -> str:
    messages = {
        "urgences": (
            "Vos symptômes indiquent une situation potentiellement grave. "
            "Appelez le 15 (SAMU) ou rendez-vous immédiatement aux urgences. "
            "Ne conduisez pas vous-même si vous vous sentez mal. "
            "⚠️ Cette orientation est indicative et ne remplace pas un avis médical."
        ),
        "medecin": (
            "Vos symptômes nécessitent une évaluation médicale. "
            "Consultez un médecin généraliste dans les 24 à 48 heures. "
            "Si vos symptômes s'aggravent, consultez plus tôt. "
            "⚠️ Cette orientation est indicative et ne remplace pas un avis médical."
        ),
        "surveillance": (
            "Vos symptômes semblent modérés et peuvent être surveillés à domicile. "
            "Reposez-vous, hydratez-vous et surveillez l'évolution. "
            "Consultez un médecin si les symptômes persistent plus de 3 jours. "
            "⚠️ Cette orientation est indicative et ne remplace pas un avis médical."
        )
    }
    return messages.get(orientation, messages["medecin"])