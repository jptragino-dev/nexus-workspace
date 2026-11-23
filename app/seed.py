
"""Popula um banco de demonstração com dados FICTÍCIOS.

Execute: python -m app.seed

ATENÇÃO: Não execute em um banco de produção.
"""

import random
from datetime import date

from .db import Base, SessionLocal, engine
from .main import add_months
from .models import Charge, Client, Contract, Payment, Plan


NAMES = [
    "Marina Alves",
    "Studio Fénix Ltda",
    "Rafael Tonelli",
    "Cláudia Reis",
    "Oficina Pixel ME",
    "Bruno Nakamura",
    "Helena Prado",
    "Vértice Contabilidade",
    "Diego Marques",
    "Lúcia Fontes",
    "Atlas Jurídico",
    "Tiago Braga",
]


def cpf():
    d = [random.randint(0, 9) for _ in range(9)]

    for n in (9, 10):
        d.append(
            (sum(v * (n + 1 - i) for i, v in enumerate(d)) * 10 % 11) % 10
        )

    return "".join(map(str, d))


def cnpj():
    d = [random.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
    w1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    for w in (w1, [6] + w1):
        r = sum(v * x for v, x in zip(d, w)) % 11
        d.append(0 if r < 2 else 11 - r)

    return "".join(map(str, d))


def run():
    random.seed(7)

    Base.metadata.create_all(engine)

    db = SessionLocal()

    try:
        # Proteção contra duplicação de dados fictícios
        if db.query(Client).count():
            print(
                "Banco já possui clientes. "
                "Nenhum dado foi alterado."
            )
            return

        # PREÇOS OFICIAIS CONNECT LIBERDADE
        plans = [
            # Estação de Trabalho
            Plan(
                name="Estação de Trabalho - Diária",
                description="Utilização diária",
                price=60,
            ),
            Plan(
                name="Estação de Trabalho - Semanal",
                description="Utilização semanal",
                price=200,
            ),
            Plan(
                name="Estação de Trabalho - Mensal",
                description="Utilização mensal",
                price=700,
            ),

            # Sala Privativa
            Plan(
                name="Sala Privativa - Diária",
                description="Utilização diária",
                price=120,
            ),
            Plan(
                name="Sala Privativa - Mensal (4 horas)",
                description="Plano mensal de 4 horas",
                price=650,
            ),
            Plan(
                name="Sala Privativa - Mensal (8 horas)",
                description="Plano mensal de 8 horas",
                price=900,
            ),

            # Sala de Reunião
            Plan(
                name="Sala de Reunião - 2 horas",
                description="Reserva de 2 horas",
                price=120,
            ),
            Plan(
                name="Sala de Reunião - 4 horas",
                description="Reserva de 4 horas",
                price=200,
            ),
            Plan(
                name="Sala de Reunião - 8 horas",
                description="Reserva de 8 horas",
                price=380,
            ),

            # Sala de Treinamento
            Plan(
                name="Sala de Treinamento - 2 horas",
                description="Reserva de 2 horas",
                price=60,
            ),
            Plan(
                name="Sala de Treinamento - 4 horas",
                description="Reserva de 4 horas",
                price=200,
            ),
            Plan(
                name="Sala de Treinamento - 8 horas",
                description="Reserva de 8 horas",
                price=700,
            ),

            # Endereço Fiscal
            Plan(
                name="Endereço Fiscal - Caixa Postal",
                description="Serviço mensal de caixa postal",
                price=105,
            ),
        ]

        db.add_all(plans)
        db.flush()

        today = date.today()

        # Clientes e contratos FICTÍCIOS
        for i, name in enumerate(NAMES):
            pj = any(
                x in name
                for x in (
                    "Ltda",
                    "ME",
                    "Contabilidade",
                    "Jurídico",
                )
            )

            client = Client(
                person_type="PJ" if pj else "PF",
                name=name,
                document=cnpj() if pj else cpf(),
                email=f"contato{i}@exemplo.com",
                active=i != 9,
            )

            db.add(client)
            db.flush()

            plan = random.choice(plans)

            start = add_months(
                today,
                -random.randint(3, 8),
                1,
            )

            contract = Contract(
                client_id=client.id,
                plan_id=plan.id,
                price=plan.price,
                start_date=start,
                due_day=random.choice([5, 10, 15]),
                status="active" if client.active else "ended",
            )

            db.add(contract)
            db.flush()

            late = i in (2, 6)

            # Cobranças e pagamentos FICTÍCIOS
            for m in range(10):
                due = add_months(
                    start,
                    m,
                    contract.due_day,
                )

                charge = Charge(
                    contract_id=contract.id,
                    due_date=due,
                    amount=plan.price,
                )

                db.add(charge)
                db.flush()

                if due < today and not (
                    late
                    and add_months(today, -1, 1) <= due
                ):
                    charge.status = "paid"

                    payment = Payment(
                        charge_id=charge.id,
                        transaction_id=f"DEMO-{charge.id:05d}",
                        method=random.choice(
                            ["pix", "boleto"]
                        ),
                        amount=charge.amount,
                        paid_at=due,
                    )

                    db.add(payment)

        db.commit()

        print(
            "Dados fictícios criados com "
            "13 planos e preços corretos."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run()
