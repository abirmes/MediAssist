from services.metrics import (
    predictions_total,
    severity_score_histogram,
    consultations_total,
    chat_messages_total,
)

def track_prediction(orientation: str, severity_score: float):
    predictions_total.labels(orientation=orientation).inc()
    severity_score_histogram.observe(severity_score)

def track_consultation():
    consultations_total.inc()

def track_chat_message():
    chat_messages_total.inc()