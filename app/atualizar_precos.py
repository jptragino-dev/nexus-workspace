
from decimal import Decimal

from app.db import SessionLocal
from app.models import Plan


# Tabela de preços CONNECT LIBERDADE
PRECOS = [
    ("Estação de Trabalho - Diária", "Utilização diária", "60.00"),
    ("Estação de Trabalho - Semanal", "Utilização semanal", "200.00"),
    ("Estação de Trabalho - Mensal", "Utilização mensal", "700.00"),

    ("Sala Privativa - Diária", "Utilização diária", "120.00"),
    ("Sala Privativa - Mensal (4 horas)", "Plano mensal de 4 horas", "650.00"),
    ("Sala Privativa - Mensal (8 horas)", "Plano mensal de 8 horas", "900.00"),

    ("Sala de Reunião - 2 horas", "Reserva de 2 horas", "120.00"),
    ("Sala de Reunião - 4 horas", "Reserva de 4 horas", "200.00"),
    ("Sala de Reunião - 8 horas", "Reserva de 8 horas", "380.00"),

    ("Sala de Treinamento - 2 horas", "Reserva de 2 horas", "60.00"),
    ("Sala de Treinamento - 4 horas", "Reserva de 4 horas", "200.00"),
    ("Sala de Treinamento - 8 horas", "Reserva de 8 horas", "700.00"),

    ("Endereço Fiscal - Caixa Postal", "Serviço mensal de caixa postal", "105.00"),
]


def atualizar():
    db = SessionLocal()

    try:
        nomes_corretos = {nome for nome, _, _ in PRECOS}

        # Criar ou atualizar planos oficiais
        for nome, descricao, valor in PRECOS:
            plano = db.query(Plan).filter(Plan.name == nome).first()

            if plano:
                plano.description = descricao
                plano.price = Decimal(valor)
                plano.active = True
                print(f"Atualizado: {nome} - R$ {valor}")
            else:
                plano = Plan(
                    name=nome,
                    description=descricao,
                    price=Decimal(valor),
                    active=True,
                )
                db.add(plano)
                print(f"Criado: {nome} - R$ {valor}")

        # Desativar planos antigos sem excluir registros
        antigos = db.query(Plan).all()

        for plano in antigos:
            if plano.name not in nomes_corretos:
                plano.active = False
                print(f"Desativado: {plano.name}")

        db.commit()

        print("\nPreços atualizados com sucesso!")

    except Exception as erro:
        db.rollback()
        print(f"Erro ao atualizar preços: {erro}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    atualizar()
