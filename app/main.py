import csv
import io
from calendar import monthrange
from collections import defaultdict
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .models import Charge, Client, Contract, Payment, Plan
from .validators import only_digits, valid_cnpj, valid_cpf

Base.metadata.create_all(engine)  # em produção: Alembic
app = FastAPI(title="Connect Liberdade — gestão de coworking")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


def add_months(d: date, n: int, day: int) -> date:
    m = d.month - 1 + n
    y, m = d.year + m // 12, m % 12 + 1
    return date(y, m, min(day, monthrange(y, m)[1]))


def charge_status(c: Charge) -> str:
    return "overdue" if c.status == "pending" and c.due_date < date.today() else c.status


class PlanIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = ""
    price: Decimal = Field(gt=0)


class ClientIn(BaseModel):
    person_type: str = Field(pattern="^(PF|PJ)$")
    name: str = Field(min_length=2)
    document: str
    email: str = ""
    phone: str = ""


class ContractIn(BaseModel):
    client_id: int
    plan_id: int
    start_date: date
    due_day: int = Field(ge=1, le=28)
    months: int = Field(default=12, ge=1, le=36)


class PaymentIn(BaseModel):
    transaction_id: str = Field(min_length=3)  # id confirmado do banco/PIX
    method: str = Field(pattern="^(pix|boleto|card|transfer|cash)$")
    amount: Decimal
    paid_at: date | None = None


@app.post("/plans", status_code=201)
def create_plan(p: PlanIn, db: Session = Depends(get_db)):
    plan = Plan(**p.model_dump())
    db.add(plan)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Já existe um plano com esse nome")
    return {"id": plan.id, "name": plan.name, "price": float(plan.price)}



@app.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    stmt = (
        select(Plan)
        .where(Plan.active.is_(True))
        .order_by(Plan.name)
    )

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": float(p.price),
            "active": p.active,
        }
        for p in db.scalars(stmt)
    ]


@app.post("/clients", status_code=201)
def create_client(c: ClientIn, db: Session = Depends(get_db)):
    doc = only_digits(c.document)
    ok = valid_cpf(doc) if c.person_type == "PF" else valid_cnpj(doc)
    if not ok:
        raise HTTPException(422, f"{'CPF' if c.person_type == 'PF' else 'CNPJ'} inválido")
    if db.scalar(select(Client).where(Client.document == doc)):
        raise HTTPException(409, "Cliente já cadastrado com este documento")
    client = Client(**{**c.model_dump(), "document": doc})
    db.add(client)
    db.commit()
    return {"id": client.id, "name": client.name}


def client_row(c: Client):
    contract = next((k for k in c.contracts if k.status == "active"), None)
    overdue = sum(1 for k in c.contracts for ch in k.charges if charge_status(ch) == "overdue")
    return {"id": c.id, "person_type": c.person_type, "name": c.name, "document": c.document,
            "email": c.email, "phone": c.phone, "active": c.active,
            "plan": contract.plan.name if contract else None, "overdue_charges": overdue}


@app.get("/clients")
def list_clients(q: str = "", active: bool | None = None, db: Session = Depends(get_db)):
    stmt = select(Client).order_by(Client.name)
    if active is not None:
        stmt = stmt.where(Client.active == active)
    if q:
        stmt = stmt.where(Client.name.ilike(f"%{q}%") | Client.document.contains(only_digits(q) or "~"))
    return [client_row(c) for c in db.scalars(stmt)]


@app.patch("/clients/{cid}/active")
def set_active(cid: int, active: bool, db: Session = Depends(get_db)):
    c = db.get(Client, cid)
    if not c:
        raise HTTPException(404, "Cliente não encontrado")
    c.active = active
    db.commit()
    return client_row(c)


@app.get("/clients/export.csv")
def export_clients(db: Session = Depends(get_db)):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["id", "tipo", "nome", "documento", "email", "telefone", "plano", "ativo"])
    for c in map(client_row, db.scalars(select(Client).order_by(Client.name))):
        w.writerow([c["id"], c["person_type"], c["name"], c["document"], c["email"],
                    c["phone"], c["plan"] or "", c["active"]])
    return Response(out.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=clientes.csv"})


@app.post("/contracts", status_code=201)
def create_contract(c: ContractIn, db: Session = Depends(get_db)):
    client, plan = db.get(Client, c.client_id), db.get(Plan, c.plan_id)

    if not client or not plan:
        raise HTTPException(
            404,
            "Cliente ou plano não encontrado"
        )

    if not plan.active:
        raise HTTPException(
            400,
            "Este plano está desativado e não pode ser contratado"
        )

    k = Contract(client_id=client.id, plan_id=plan.id, price=plan.price,
                 start_date=c.start_date, due_day=c.due_day)
    db.add(k)
    db.flush()
    for i in range(c.months):
        db.add(Charge(contract_id=k.id, amount=plan.price,
                      due_date=add_months(c.start_date, i, c.due_day)))
    db.commit()
    return {"id": k.id, "charges_created": c.months}


@app.get("/charges")
def list_charges(status: str | None = Query(None, pattern="^(pending|paid|overdue|cancelled)$"),
                 db: Session = Depends(get_db)):
    rows = []
    for ch in db.scalars(select(Charge).order_by(Charge.due_date)):
        st = charge_status(ch)
        if status and st != status:
            continue
        rows.append({"id": ch.id, "client": ch.contract.client.name, "plan": ch.contract.plan.name,
                     "due_date": ch.due_date.isoformat(), "amount": float(ch.amount), "status": st})
    return rows


@app.post("/charges/{chid}/payments", status_code=201)
def register_payment(chid: int, p: PaymentIn, db: Session = Depends(get_db)):
    """Só marca como paga com id de transação confirmado e valor exato."""
    ch = db.get(Charge, chid)
    if not ch:
        raise HTTPException(404, "Cobrança não encontrada")
    if ch.status != "pending":
        raise HTTPException(409, "Cobrança não está pendente")
    if p.amount != ch.amount:
        raise HTTPException(422, "Valor diferente do valor da cobrança")
    ch.status = "paid"
    db.add(Payment(charge_id=ch.id, transaction_id=p.transaction_id, method=p.method,
                   amount=p.amount, paid_at=p.paid_at or date.today()))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Transação já registrada (duplicidade evitada)")
    return {"charge_id": chid, "status": "paid"}


@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    clients = list(db.scalars(select(Client)))
    charges = list(db.scalars(select(Charge)))
    payments = list(db.scalars(select(Payment)))
    today = date.today()
    pend = [c for c in charges if charge_status(c) == "pending"]
    over = [c for c in charges if charge_status(c) == "overdue"]
    monthly = defaultdict(float)
    for p in payments:
        monthly[p.paid_at.strftime("%Y-%m")] += float(p.amount)
    by_plan = defaultdict(int)
    for k in db.scalars(select(Contract).where(Contract.status == "active")):
        by_plan[k.plan.name] += 1
    return {
        "clients": {"total": len(clients), "active": sum(c.active for c in clients),
                    "inactive": sum(not c.active for c in clients),
                    "delinquent": len({c.contract.client_id for c in over})},
        "received_total": sum(float(p.amount) for p in payments),
        "received_month": sum(float(p.amount) for p in payments
                              if (p.paid_at.year, p.paid_at.month) == (today.year, today.month)),
        "pending_total": sum(float(c.amount) for c in pend),
        "overdue_total": sum(float(c.amount) for c in over),
        "monthly_revenue": [{"month": m, "value": v} for m, v in sorted(monthly.items())][-12:],
        "clients_by_plan": [{"plan": k, "count": v} for k, v in by_plan.items()],
        "upcoming": [{"client": c.contract.client.name, "due_date": c.due_date.isoformat(),
                      "amount": float(c.amount)} for c in sorted(pend, key=lambda c: c.due_date)[:6]],
    }


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")
