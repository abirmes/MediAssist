"""
Tests unitaires — Modèle ML
"""
import pytest
import numpy as np


def test_ml_service_predict():
    """Test service ML complet avec mock."""
    from services.ml_service import predict_orientation
    result = predict_orientation(["chest pain", "sweating"])
    assert "orientation"    in result
    assert "confidence"     in result
    assert "severity_score" in result
    assert "risk_level"     in result
    assert result["orientation"] in ["urgences", "medecin", "surveillance"]


def test_severity_score_range():
    """Test que le score de gravité est dans [0, 100]."""
    from services.scoring_service import calculate_severity_score
    for orientation in ["urgences", "medecin", "surveillance"]:
        score = calculate_severity_score(["fever", "cough"], orientation)
        assert 0 <= score <= 100


def test_risk_level():
    """Test niveaux de risque."""
    from services.scoring_service import get_risk_level
    assert get_risk_level(85) == "critical"
    assert get_risk_level(65) == "high"
    assert get_risk_level(45) == "medium"
    assert get_risk_level(20) == "low"


def test_symptom_cols_loaded():
    """Test que les symptômes sont chargés."""
    from services.ml_service import get_symptom_list
    symptoms = get_symptom_list()
    assert symptoms is not None
    assert len(symptoms) > 0