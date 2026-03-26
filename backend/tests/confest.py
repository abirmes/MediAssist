"""
Configuration globale pytest — Mock du modèle ML
"""
import os
import numpy as np
from unittest.mock import MagicMock

# Variables d'environnement pour les tests
os.environ.setdefault("DATABASE_URL",    "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY",      "test-secret-key")
os.environ.setdefault("GROQ_API_KEY",    "test-key")
os.environ.setdefault("ALGORITHM",       "HS256")
os.environ.setdefault("APP_ENV",         "test")

# Mock du modèle ML avant import
import services.ml_service as ml_service

# Faux modèle ML
fake_model = MagicMock()
fake_model.predict.return_value = np.array([0])
fake_model.predict_proba.return_value = np.array([[0.6, 0.2, 0.2]])

fake_encoder = MagicMock()
fake_encoder.classes_ = np.array(['medecin', 'surveillance', 'urgences'])
fake_encoder.inverse_transform.return_value = ['medecin']

fake_symptom_cols = [f'symptom_{i}' for i in range(1326)]

# Injecter les mocks
ml_service._model        = fake_model
ml_service._encoder      = fake_encoder
ml_service._symptom_cols = fake_symptom_cols