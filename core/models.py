from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    fullname = Column(String(200))
    email = Column(String(200))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cards = relationship("Card", back_populates="user")


class CardRequest(Base):
    __tablename__ = "card_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fio = Column(String(400))
    phone = Column(String(80))
    comments = Column(Text)
    status = Column(String(50), default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", backref="card_requests")


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime(timezone=True), server_default=func.now())
    level = Column(String(20))
    event = Column(String(200))
    source_ip = Column(String(50))
    user = Column(String(80))
    details = Column(Text)


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    card_number = Column(String(16), nullable=False, unique=True)
    card_type = Column(String(50), nullable=False)
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default="RUB")
    expiry_date = Column(Date, nullable=False)
    cvv = Column(String(3), nullable=False)

    user = relationship("User", back_populates="cards")
