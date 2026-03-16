import joblib
import numpy as np
from typing import List
from config import get_settings

settings = get_settings()

# Chargement des modèles au démarrage
_model = None
_encoder = None
_symptom_cols = None


def load_models():
    global _model, _encoder, _symptom_cols
    try:
        _model       = joblib.load(settings.MODEL_PATH)
        _encoder     = joblib.load(settings.ENCODER_PATH)
        _symptom_cols = joblib.load(settings.SYMPTOMS_PATH)
        print(f"✅ Modèle ML chargé — {len(_symptom_cols)} symptômes")
    except Exception as e:
        print(f"⚠️ Erreur chargement modèle : {e}")


def get_symptom_list() -> List[str]:
    if _symptom_cols is None:
        load_models()
    return _symptom_cols


def predict_orientation(symptoms: List[str]) -> dict:
    """
    Prédit l'orientation médicale depuis une liste de symptômes.
    """
    if _model is None:
        load_models()

    # Vecteur binaire
    vector = np.zeros(len(_symptom_cols))
    matched = []
    for i, col in enumerate(_symptom_cols):
        for symptom in symptoms:
            if symptom.lower() in col.lower() or col.lower() in symptom.lower():
                vector[i] = 1
                matched.append(col)
                break

    # Prédiction
    pred  = _model.predict([vector])[0]
    proba = _model.predict_proba([vector])[0]
    orientation = _encoder.inverse_transform([pred])[0]
    confidence  = round(float(proba.max()) * 100, 1)

    # Score de gravité
    base_scores = {"urgences": 85, "medecin": 65, "surveillance": 30}
    severity_score = round(
        base_scores.get(orientation, 65) + np.random.uniform(-5, 5), 1
    )
    severity_score = float(np.clip(severity_score, 0, 100))

    # Niveau de risque
    if severity_score >= 80:
        risk_level = "critical"
    elif severity_score >= 60:
        risk_level = "high"
    elif severity_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "orientation":    orientation,
        "confidence":     confidence,
        "severity_score": severity_score,
        "risk_level":     risk_level,
        "matched_symptoms": matched,
    }