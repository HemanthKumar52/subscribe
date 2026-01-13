from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    subscriptions = relationship("Subscription", back_populates="user")
    entitlements = relationship("Entitlement", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(String)
    purchase_token = Column(String)
    expiry_time = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    status = Column(String) # ACTIVE, EXPIRED, CANCELED

    user = relationship("User", back_populates="subscriptions")

class Entitlement(Base):
    __tablename__ = "entitlements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    feature_key = Column(String)
    enabled = Column(Boolean, default=False)

    user = relationship("User", back_populates="entitlements")
