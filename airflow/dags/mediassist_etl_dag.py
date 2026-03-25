from datetime import datetime, timedelta
import os
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

DEFAULT_ARGS = {
    "owner": "abir_meskini",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

BASE_DIR = os.getenv("MEDIASSIST_BASE_DIR", "/opt/airflow/ml")

RAW_PATH = os.path.join(BASE_DIR, "data/raw")
PROC_PATH = os.path.join(BASE_DIR, "data/processed")
MODELS_PATH = os.path.join(BASE_DIR, "models")
LOGS_PATH = os.path.join(BASE_DIR, "logs")


def extract_raw_data(**context):
    import pandas as pd
    import json

    logger = logging.getLogger(__name__)

    for path in [PROC_PATH, MODELS_PATH, LOGS_PATH]:
        os.makedirs(path, exist_ok=True)

    files = {
        "train": "trainings.csv",
        "test": "testing.csv",
        "severity": "Symptom-severity.csv",
        "desc": "symptom_Description.csv",
        "precaution": "symptom_precaution.csv",
    }

    report = {}

    for name, fname in files.items():
        path = os.path.join(RAW_PATH, fname)

        if not os.path.exists(path):
            raise FileNotFoundError(path)

        df = pd.read_csv(path, nrows=5, encoding="latin-1")

        report[name] = {
            "path": path,
            "columns": list(df.columns),
            "size": os.path.getsize(path),
        }

        logger.info(f"{fname} OK")

    context["ti"].xcom_push(key="extraction_report", value=report)
    return report


def clean_and_normalize(**context):
    import pandas as pd
    import json

    logger = logging.getLogger(__name__)

    def clean_cols(df):
        df.columns = [c.replace("\xa0", " ").replace("\n", " ").strip() for c in df.columns]
        return df

    train = pd.read_csv(os.path.join(RAW_PATH, "trainings.csv"), encoding="latin-1")
    test = pd.read_csv(os.path.join(RAW_PATH, "testing.csv"), encoding="latin-1")

    train, test = clean_cols(train), clean_cols(test)

    df = pd.concat([train, test], ignore_index=True)
    before = len(df)

    df.drop_duplicates(inplace=True)
    removed = before - len(df)

    symptom_cols = [c for c in df.columns if c != "Prognosis"]

    report = {
        "rows": len(df),
        "duplicates_removed": removed,
        "nulls": int(df.isnull().sum().sum()),
        "diseases": int(df["Prognosis"].nunique()),
        "symptoms": len(symptom_cols),
        "time": datetime.now().isoformat(),
    }

    df.to_csv(os.path.join(PROC_PATH, "dataset_clean.csv"), index=False)

    with open(os.path.join(LOGS_PATH, "quality_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    context["ti"].xcom_push(key="symptom_cols", value=symptom_cols)
    context["ti"].xcom_push(key="quality_report", value=report)

    return report


def generate_orientation_mapping(**context):
    import pandas as pd
    import json

    logger = logging.getLogger(__name__)

    mapping_path = os.path.join(PROC_PATH, "disease_orientation.json")

    if os.path.exists(mapping_path):
        with open(mapping_path) as f:
            raw = json.load(f)

        flat = {}
        for k, v in raw.items():
            if isinstance(v, list):
                for d in v:
                    flat[d.strip()] = k
            else:
                flat[v.strip()] = k

    else:
        df = pd.read_csv(os.path.join(PROC_PATH, "dataset_clean.csv"))
        flat = {d: "medecin" for d in df["Prognosis"].unique()}

    path = os.path.join(PROC_PATH, "disease_orientation_flat.json")

    with open(path, "w") as f:
        json.dump(flat, f, indent=2, ensure_ascii=False)

    context["ti"].xcom_push(key="mapping_count", value=len(flat))

    return {"count": len(flat), "path": path}


def feature_engineering(**context):
    import pandas as pd
    import numpy as np
    import json
    import joblib

    logger = logging.getLogger(__name__)

    df = pd.read_csv(os.path.join(PROC_PATH, "dataset_clean.csv"))
    severity = pd.read_csv(os.path.join(RAW_PATH, "Symptom-severity.csv"))

    with open(os.path.join(PROC_PATH, "disease_orientation_flat.json")) as f:
        mapping = json.load(f)

    symptom_cols = [c for c in df.columns if c != "Prognosis"]

    severity_dict = dict(zip(
        severity["Symptom"].str.strip().str.lower().str.replace("_", " "),
        severity["weight"]
    ))

    base = {"urgences": 85, "medecin": 65, "surveillance": 30}

    def score(row):
        active = [c for c in symptom_cols if row[c] == 1]

        if not active:
            return float(base.get(row["orientation"], 30))

        weights = [severity_dict.get(s.lower(), 3) for s in active]
        val = (base.get(row["orientation"], 65) * 0.6) + ((np.mean(weights) / 7 * 100) * 0.4)

        return round(float(np.clip(val + np.random.uniform(-3, 3), 0, 100)), 1)

    def risk(x):
        if x >= 80:
            return "critical"
        if x >= 60:
            return "high"
        if x >= 40:
            return "medium"
        return "low"

    df["orientation"] = df["Prognosis"].map(lambda x: mapping.get(x, "medecin"))
    df["severity_score"] = df.apply(score, axis=1)
    df["risk_level"] = df["severity_score"].apply(risk)

    df.to_csv(os.path.join(PROC_PATH, "dataset_final.csv"), index=False)

    with open(os.path.join(PROC_PATH, "symptom_cols.json"), "w") as f:
        json.dump(symptom_cols, f)

    joblib.dump(symptom_cols, os.path.join(MODELS_PATH, "symptom_cols.joblib"))

    stats = {
        "rows": len(df),
        "distribution": df["orientation"].value_counts().to_dict(),
        "avg_score": float(df["severity_score"].mean()),
        "time": datetime.now().isoformat(),
    }

    context["ti"].xcom_push(key="feature_stats", value=stats)

    return stats


def train_model(**context):
    import json
    import joblib
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.metrics import accuracy_score
    from sklearn.preprocessing import LabelEncoder

    logger = logging.getLogger(__name__)

    model_path = os.path.join(MODELS_PATH, "orientation_model.joblib")
    report_path = os.path.join(MODELS_PATH, "evaluation_report.json")

    df = pd.read_csv(os.path.join(PROC_PATH, "dataset_final.csv"))

    exclude = {"Prognosis", "orientation", "severity_score", "risk_level"}
    cols = [c for c in df.columns if c not in exclude]

    X = df[cols].values
    le = LabelEncoder()
    y = le.fit_transform(df["orientation"])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    acc = float(accuracy_score(y_test, model.predict(X_test)))
    cv = cross_val_score(model, X, y, cv=StratifiedKFold(5))

    report = {
        "model": "RandomForest",
        "accuracy": round(acc, 4),
        "cv": round(float(cv.mean()), 4),
        "classes": le.classes_.tolist(),
        "time": datetime.now().isoformat(),
    }

    joblib.dump(model, model_path)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    context["ti"].xcom_push(key="accuracy", value=acc)

    return report


def validate_model(**context):
    import json

    logger = logging.getLogger(__name__)
    ACCURACY_THRESHOLD = 0.70

    # Lire depuis evaluation_report.json directement (plus fiable que XCom)
    report_path = os.path.join(MODELS_PATH, "evaluation_report.json")
    with open(report_path) as f:
        report = json.load(f)
    
    accuracy = report.get("accuracy", 0.0)
    status = "PASSED" if accuracy >= ACCURACY_THRESHOLD else "DEGRADED"

    validation_log = {
        "timestamp": datetime.now().isoformat(),
        "accuracy": accuracy,
        "threshold": ACCURACY_THRESHOLD,
        "status": status,
    }
    
    with open(os.path.join(LOGS_PATH, "validation_log.json"), "w") as f:
        json.dump(validation_log, f, indent=2)

    logger.info(f"✅ Validation {status} — accuracy={accuracy:.4f}")
    return validation_log


with DAG(
    dag_id="mediassist_pipeline",
    default_args=DEFAULT_ARGS,
    schedule_interval="0 2 * * 0",
    start_date=days_ago(1),
    catchup=False,
    params={"force_retrain": False},
) as dag:

    t1 = PythonOperator(task_id="extract", python_callable=extract_raw_data)
    t2 = PythonOperator(task_id="clean", python_callable=clean_and_normalize)
    t3 = PythonOperator(task_id="mapping", python_callable=generate_orientation_mapping)
    t4 = PythonOperator(task_id="features", python_callable=feature_engineering)
    t5 = PythonOperator(task_id="train", python_callable=train_model)
    t6 = PythonOperator(task_id="validate", python_callable=validate_model)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6