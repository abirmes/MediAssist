import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent / "ml"

RAW = BASE_DIR / "data/raw"
PROC = BASE_DIR / "data/processed"
MODELS = BASE_DIR / "models"
LOGS = BASE_DIR / "logs"

for p in [PROC, MODELS, LOGS]:
    p.mkdir(parents=True, exist_ok=True)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOGS / f"etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
    ],
)
log = logging.getLogger(__name__)


def step_extract():
    files = [
        "trainings.csv",
        "testing.csv",
        "Symptom-severity.csv",
        "symptom_Description.csv",
        "symptom_precaution.csv",
    ]

    report = {}

    for f in files:
        path = RAW / f
        if not path.exists():
            raise FileNotFoundError(path)

        report[f] = {
            "path": str(path),
            "size": path.stat().st_size,
        }

        log.info(f"{f} OK")

    return report


def step_clean():
    def clean_cols(df):
        df.columns = [c.replace("\xa0", " ").replace("\n", " ").strip() for c in df.columns]
        return df

    train = pd.read_csv(RAW / "trainings.csv", encoding="latin-1")
    test = pd.read_csv(RAW / "testing.csv", encoding="latin-1")

    train, test = clean_cols(train), clean_cols(test)

    df = pd.concat([train, test], ignore_index=True)

    before = len(df)
    df.drop_duplicates(inplace=True)

    nulls = int(df.isnull().sum().sum())
    df.fillna(0, inplace=True)

    symptoms = [c for c in df.columns if c != "Prognosis"]

    report = {
        "rows": len(df),
        "duplicates_removed": before - len(df),
        "nulls": nulls,
        "diseases": int(df["Prognosis"].nunique()),
        "symptoms": len(symptoms),
        "time": datetime.now().isoformat(),
    }

    df.to_csv(PROC / "dataset_clean.csv", index=False)

    with open(LOGS / "quality.json", "w") as f:
        json.dump(report, f, indent=2)

    return report


def step_mapping():
    path = PROC / "disease_orientation.json"

    if path.exists():
        with open(path) as f:
            raw = json.load(f)

        flat = {}
        for k, v in raw.items():
            if isinstance(v, list):
                for d in v:
                    flat[d.strip()] = k
            else:
                flat[v.strip()] = k
    else:
        df = pd.read_csv(PROC / "dataset_clean.csv")
        flat = {d: "medecin" for d in df["Prognosis"].unique()}

    out = PROC / "disease_orientation_flat.json"

    with open(out, "w") as f:
        json.dump(flat, f, indent=2, ensure_ascii=False)

    return {"count": len(flat)}


def step_features():
    df = pd.read_csv(PROC / "dataset_clean.csv")
    severity = pd.read_csv(RAW / "Symptom-severity.csv")

    with open(PROC / "disease_orientation_flat.json") as f:
        mapping = json.load(f)

    symptoms = [c for c in df.columns if c != "Prognosis"]

    weights = dict(zip(
        severity["Symptom"].str.strip().str.lower().str.replace("_", " "),
        severity["weight"]
    ))

    base = {"urgences": 85, "medecin": 65, "surveillance": 30}

    def score(row):
        active = [c for c in symptoms if row[c] == 1]

        if not active:
            return float(base.get(row["orientation"], 30))

        w = [weights.get(s.lower(), 3) for s in active]
        val = (base.get(row["orientation"], 65) * 0.6) + ((np.mean(w) / 7 * 100) * 0.4)

        return round(float(np.clip(val + np.random.uniform(-3, 3), 0, 100)), 1)

    df["orientation"] = df["Prognosis"].map(lambda x: mapping.get(x, "medecin"))
    df["severity_score"] = df.apply(score, axis=1)

    df["risk_level"] = df["severity_score"].apply(
        lambda x: "critical" if x >= 80 else "high" if x >= 60 else "medium" if x >= 40 else "low"
    )

    df.to_csv(PROC / "dataset_final.csv", index=False)

    with open(PROC / "symptom_cols.json", "w") as f:
        json.dump(symptoms, f)

    joblib.dump(symptoms, MODELS / "symptom_cols.joblib")

    return {
        "rows": len(df),
        "distribution": df["orientation"].value_counts().to_dict(),
    }


def step_train():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
    from sklearn.preprocessing import LabelEncoder

    df = pd.read_csv(PROC / "dataset_final.csv")

    exclude = {"Prognosis", "orientation", "severity_score", "risk_level"}
    cols = [c for c in df.columns if c not in exclude]

    X = df[cols].values

    le = LabelEncoder()
    y = le.fit_transform(df["orientation"])
    joblib.dump(le, MODELS / "label_encoder.joblib")

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
        "time": datetime.now().isoformat(),
    }

    joblib.dump(model, MODELS / "orientation_model.joblib")

    with open(MODELS / "evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    return report


STEPS = {
    "extract": step_extract,
    "clean": step_clean,
    "mapping": step_mapping,
    "features": step_features,
    "train": step_train,
}


def run_all():
    results = {}

    for name, fn in STEPS.items():
        log.info(f"RUN {name}")
        results[name] = fn()

    with open(LOGS / "run.json", "w") as f:
        json.dump({
            "time": datetime.now().isoformat(),
            "steps": list(results.keys()),
        }, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--step", choices=STEPS.keys())

    args = parser.parse_args()

    if args.step:
        STEPS[args.step]()
    else:
        run_all()