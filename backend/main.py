from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import create_tables
from services.ml_service import load_models
from routers import auth, analysis, dashboard, chat



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Démarrage MediAssist AI...")
    create_tables()
    print("Tables créées")
    load_models()
    print("Modèle ML chargé")
    yield
    print("Arrêt MediAssist AI")


app = FastAPI(
    title="MediAssist AI",
    description=(
        "API d'orientation médicale basée sur l'IA. "
        "Ne remplace pas un avis médical professionnel."
    ),
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(chat.router)


@app.get("/", tags=["Health"])
def root():
    return {"app": "MediAssist AI", "version": "1.0.0", "status": "running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )