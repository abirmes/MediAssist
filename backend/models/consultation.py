from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Consultation(Base):
    __tablename__ = "consultations"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    date       = Column(DateTime(timezone=True), server_default=func.now())
    status     = Column(String(50), default="pending")
    raw_input  = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user     = relationship("User", back_populates="consultations")
    analysis = relationship("Analysis", back_populates="consultation",
                             uselist=False, cascade="all, delete-orphan")
    messages = relationship("ChatMessage", back_populates="consultation",
                             cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id              = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id",
                                                  ondelete="CASCADE"), unique=True)
    severity_score  = Column(Float)
    risk_level      = Column(String(50))
    orientation     = Column(String(100))
    explanation     = Column(Text)
    model_version   = Column(String(50), default="1.0.0")
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    consultation = relationship("Consultation", back_populates="analysis")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id              = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id",
                                                  ondelete="CASCADE"))
    sender          = Column(String(50), nullable=False)
    message         = Column(Text, nullable=False)
    timestamp       = Column(DateTime(timezone=True), server_default=func.now())

    consultation = relationship("Consultation", back_populates="messages")