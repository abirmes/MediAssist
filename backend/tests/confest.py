
import pytest
import os

os.environ.setdefault("DATABASE_URL",    "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY",      "test-secret-key")
os.environ.setdefault("GROQ_API_KEY",    "test-key")
os.environ.setdefault("ALGORITHM",       "HS256")
os.environ.setdefault("APP_ENV",         "test")