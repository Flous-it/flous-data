"""SQLAlchemy session + ORM models for the bundled SQLite database."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, relationship

from . import get_db_path


class Base(DeclarativeBase):
    pass


class Bank(Base):
    __tablename__ = "banks"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    bic = Column(String, nullable=False)
    abi = Column(String, nullable=False)
    mec_code = Column(String, nullable=False)
    country = Column(String, nullable=False, default="IT")

    accounts: list[Account] = relationship("Account", back_populates="bank")


class Feature(Base):
    __tablename__ = "features"

    code = Column(String, primary_key=True)
    label_it = Column(String, nullable=False)
    category = Column(String, nullable=False)
    product_type = Column(String, nullable=False)
    value_type = Column(String, nullable=False)
    unit = Column(String)
    display_order = Column(Integer, nullable=False)


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True)
    bank_id = Column(String, ForeignKey("banks.id"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    product_type = Column(String, nullable=False)
    source_url = Column(String, nullable=False)
    last_updated = Column(String, nullable=False)

    bank: Bank = relationship("Bank", back_populates="accounts")
    features: list[AccountFeature] = relationship("AccountFeature", back_populates="account")


class AccountFeature(Base):
    __tablename__ = "account_features"

    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    feature_code = Column(String, ForeignKey("features.code"), nullable=False)
    value_money = Column(Float)
    value_bool = Column(Boolean)
    value_text = Column(Text)
    free_quota = Column(Integer)
    unit_cost = Column(Float)
    percentage = Column(Float)
    notes = Column(Text)
    effective_from = Column(String, nullable=False)
    effective_to = Column(String)

    account: Account = relationship("Account", back_populates="features")
    conditions: list[FeaturePrice] = relationship("FeaturePrice", back_populates="account_feature")


class FeaturePrice(Base):
    __tablename__ = "feature_prices"

    id = Column(String, primary_key=True)
    account_feature_id = Column(String, ForeignKey("account_features.id"), nullable=False)
    condition_type = Column(String, nullable=False)
    condition_value = Column(Float)
    price_override = Column(Float, nullable=False)
    condition_label = Column(String, nullable=False)

    account_feature: AccountFeature = relationship("AccountFeature", back_populates="conditions")


def get_session() -> Session:
    """Open a read-only SQLAlchemy session on the bundled database."""
    engine = create_engine(f"sqlite:///{get_db_path()}", connect_args={"check_same_thread": False})
    return Session(engine)
