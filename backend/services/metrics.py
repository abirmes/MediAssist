from prometheus_client import Counter, Histogram

predictions_total = Counter(
    "predictions_total",
    "Nombre total de prédictions",
    ["orientation"]
)

consultations_total = Counter(
    "consultations_total",
    "Nombre total de consultations"
)

chat_messages_total = Counter(
    "chat_messages_total",
    "Nombre total de messages chat"
)

severity_score_histogram = Histogram(
    "severity_score",
    "Distribution des scores de gravité"
)


DISEASE_COUNTER = Counter('disease_detected_total', 'Maladie prédite', ['disease_name'])

PREDICTION_LATENCY = Histogram('prediction_duration_seconds', 'Temps de réponse du modèle')

DISEASE_PREDICTIONS = Counter('mediassist_disease_total', 'Nombre de fois qu une maladie est predite', ['disease'])