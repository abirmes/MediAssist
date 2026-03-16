from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.consultation import Consultation, Analysis
from schemas.consultation import DashboardStats
from services.auth_service import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retourne les statistiques de l'utilisateur."""
    consultations = db.query(Consultation).filter(
        Consultation.user_id == current_user.id
    ).all()
    total = len(consultations)

    consultation_ids = [c.id for c in consultations]
    analyses = db.query(Analysis).filter(
        Analysis.consultation_id.in_(consultation_ids)
    ).all() if consultation_ids else []

    urgences_count    = sum(1 for a in analyses if a.orientation == "urgences")
    medecin_count     = sum(1 for a in analyses if a.orientation == "medecin")
    surveillance_count = sum(1 for a in analyses if a.orientation == "surveillance")
    avg_score = (
        sum(a.severity_score for a in analyses) / len(analyses)
        if analyses else 0.0
    )

    return DashboardStats(
        total_consultations=total,
        urgences_count=urgences_count,
        medecin_count=medecin_count,
        surveillance_count=surveillance_count,
        avg_severity_score=round(avg_score, 1)
    )