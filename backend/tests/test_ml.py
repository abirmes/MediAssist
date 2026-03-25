"""
Tests unitaires — Modèle ML
"""
import pytest
import numpy as np
import joblib
import os


MODEL_PATH   = '/app/ml/models/orientation_model.joblib'
ENCODER_PATH = '/app/ml/models/label_encoder.joblib'
SYMPTOMS_PATH= '/app/ml/models/symptom_cols.joblib'


@pytest.fixture(scope="module")
def model():
    if not os.path.exists(MODEL_PATH):
        pytest.skip("Modèle ML non trouvé")
    return joblib.load(MODEL_PATH)


@pytest.fixture(scope="module")
def encoder():
    if not os.path.exists(ENCODER_PATH):
        pytest.skip("Encoder non trouvé")
    return joblib.load(ENCODER_PATH)


@pytest.fixture(scope="module")
def symptom_cols():
    if not os.path.exists(SYMPTOMS_PATH):
        pytest.skip("Symptom cols non trouvé")
    return joblib.load(SYMPTOMS_PATH)


def test_model_loaded(model):
    """Test que le modèle est chargé correctement."""
    assert model is not None


def test_model_classes(encoder):
    """Test que les classes sont correctes."""
    classes = encoder.classes_.tolist()
    assert "urgences"     in classes
    assert "medecin"      in classes
    assert "surveillance" in classes


def test_symptom_cols_count(symptom_cols):
    """Test nombre de symptômes."""
    assert len(symptom_cols) == 1326


def test_model_prediction(model, encoder, symptom_cols):
    """Test prédiction du modèle."""
    vector = np.zeros(len(symptom_cols))
    pred   = model.predict([vector])[0]
    orient = encoder.inverse_transform([pred])[0]
    assert orient in ["urgences", "medecin", "surveillance"]


def test_model_predict_proba(model, symptom_cols):
    """Test probabilités de prédiction."""
    vector = np.zeros(len(symptom_cols))
    proba  = model.predict_proba([vector])[0]
    assert len(proba) == 3
    assert abs(sum(proba) - 1.0) < 0.001



def test_ml_service_predict():
    """Test service ML complet."""
    from services.ml_service import predict_orientation
    result = predict_orientation(["chest pain", "sweating"])
    assert "orientation"    in result
    assert "confidence"     in result
    assert "severity_score" in result
    assert "risk_level"     in result
    assert result["orientation"] in ["urgences", "medecin", "surveillance"]