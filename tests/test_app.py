import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/t.db"

from datetime import date, timedelta  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402
from app.validators import valid_cnpj, valid_cpf  # noqa: E402

api = TestClient(app)


def test_validators():
    assert valid_cpf("529.982.247-25") and not valid_cpf("111.111.111-11")
    assert valid_cnpj("11.222.333/0001-81") and not valid_cnpj("11.222.333/0001-82")


def test_full_flow():
    plan = api.post("/plans", json={"name": "Flex", "price": 500}).json()
    assert api.post("/plans", json={"name": "Flex", "price": 500}).status_code == 409
    bad = api.post("/clients", json={"person_type": "PF", "name": "Ana", "document": "123"})
    assert bad.status_code == 422
    body = {"person_type": "PF", "name": "Ana Lima", "document": "52998224725"}
    cid = api.post("/clients", json=body).json()["id"]
    assert api.post("/clients", json=body).status_code == 409  # duplicidade

    start = (date.today() - timedelta(days=40)).isoformat()
    r = api.post("/contracts", json={"client_id": cid, "plan_id": plan["id"],
                                     "start_date": start, "due_day": 10, "months": 3})
    assert r.json()["charges_created"] == 3
    charges = api.get("/charges").json()
    assert any(c["status"] == "overdue" for c in charges)

    first = charges[0]["id"]
    pay = {"transaction_id": "E2E-123", "method": "pix", "amount": 500}
    assert api.post(f"/charges/{first}/payments", json={**pay, "amount": 1}).status_code == 422
    assert api.post(f"/charges/{first}/payments", json=pay).status_code == 201
    assert api.post(f"/charges/{first}/payments", json=pay).status_code == 409
    second = charges[1]["id"]
    assert api.post(f"/charges/{second}/payments", json=pay).status_code == 409  # id repetido

    d = api.get("/dashboard").json()
    assert d["received_total"] == 500 and d["clients"]["total"] == 1
    assert "Ana Lima" in api.get("/clients/export.csv").text
