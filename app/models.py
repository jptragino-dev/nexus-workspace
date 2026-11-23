from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    description: Mapped[str] = mapped_column(String(300), default="")
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    active: Mapped[bool] = mapped_column(default=True)


class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    person_type: Mapped[str] = mapped_column(String(2))  # PF | PJ
    name: Mapped[str] = mapped_column(String(160))
    document: Mapped[str] = mapped_column(String(14), unique=True)
    email: Mapped[str] = mapped_column(String(160), default="")
    phone: Mapped[str] = mapped_column(String(30), default="")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    contracts: Mapped[list["Contract"]] = relationship(back_populates="client")


class Contract(Base):
    __tablename__ = "contracts"
    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    start_date: Mapped[date]
    due_day: Mapped[int]
    status: Mapped[str] = mapped_column(String(12), default="active")
    client: Mapped[Client] = relationship(back_populates="contracts")
    plan: Mapped[Plan] = relationship()
    charges: Mapped[list["Charge"]] = relationship(back_populates="contract")


class Charge(Base):
    __tablename__ = "charges"
    __table_args__ = (UniqueConstraint("contract_id", "due_date"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id"))
    due_date: Mapped[date]
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(12), default="pending")  # pending | paid | cancelled
    contract: Mapped[Contract] = relationship(back_populates="charges")
    payment: Mapped["Payment | None"] = relationship(back_populates="charge", uselist=False)


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    charge_id: Mapped[int] = mapped_column(ForeignKey("charges.id"), unique=True)
    transaction_id: Mapped[str] = mapped_column(String(80), unique=True)
    method: Mapped[str] = mapped_column(String(20))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    paid_at: Mapped[date]
    charge: Mapped[Charge] = relationship(back_populates="payment")
