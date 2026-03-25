import os
import json
import joblib
import mlflow
import mlflow.sklearn

MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "sqlite:////app/mlruns/mlflow.db")
MODELS_PATH = "/app/ml/models/"


def log_existing_model():
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment("mediassist-symptoms")

    with open(f"{MODELS_PATH}evaluation_report.json") as f:
        report = json.load(f)

    model = joblib.load(f"{MODELS_PATH}orientation_model.joblib")
    label_encoder = joblib.load(f"{MODELS_PATH}label_encoder.joblib")
    symptom_cols = joblib.load(f"{MODELS_PATH}symptom_cols.joblib")

    with mlflow.start_run(run_name=f"{report['best_model']}_v1"):

        mlflow.log_param("model_type", report["best_model"])
        mlflow.log_param("n_features", report["n_features"])
        mlflow.log_param("n_train", report.get("n_train", "N/A"))
        mlflow.log_param("n_test", report.get("n_test", "N/A"))
        mlflow.log_param("n_diseases", report.get("n_diseases", 391))
        mlflow.log_param("class_weight", "balanced")
        mlflow.log_param("classes", str(report["classes"]))

        mlflow.log_metric("accuracy", report["accuracy"])
        mlflow.log_metric("cv_score", report["cv_score"])

        for name, metrics in report.get("models_compared", {}).items():
            mlflow.log_metric(f"{name}_accuracy", metrics["accuracy"])
            mlflow.log_metric(f"{name}_cv", metrics["cv"])

        mlflow.sklearn.log_model(
            model,
            artifact_path="orientation_model",
            registered_model_name="MediAssist-Orientation",
        )

        print("Model logged in MLflow")
        print(f"Model      : {report['best_model']}")
        print(f"Accuracy   : {report['accuracy']:.4f}")
        print(f"CV Score   : {report['cv_score']:.4f}")
        print(f"Features   : {report['n_features']}")
        print(f"Classes    : {report['classes']}")
        print(f"\nMLflow UI  : {MLFLOW_URI}")


if __name__ == "__main__":
    log_existing_model()