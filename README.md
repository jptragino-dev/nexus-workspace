# Connect Liberdade — gestão de coworking (projeto de portfólio)

Sistema web para gerir clientes, planos, contratos e cobranças de um coworking, substituindo planilhas por um banco relacional.
Inspirado em um caso real de negócio; **todos os dados de demonstração são fictícios** (`python -m app.seed`).

## O que já funciona
- Cadastro de clientes PF/PJ com **validação de CPF/CNPJ** e bloqueio de duplicidade
- Planos e contratos; geração automática de cobranças mensais (sem duplicar vencimentos)
- **Baixa de cobrança só com ID de transação confirmado e valor exato**; transação repetida é recusada
- Inadimplência calculada a partir do vencimento
- Dashboard com indicadores calculados direto do banco; exportação de clientes em CSV
- Testes automatizados (`pytest`)

## Stack
Python · FastAPI · SQLAlchemy · PostgreSQL (SQLite em dev) · HTML/CSS/JS · Docker Compose

## Como rodar
```bash
pip install -r requirements.txt
python -m app.seed            # opcional: dados fictícios
uvicorn app.main:app --reload # http://localhost:8000  (docs da API em /docs)
pytest
```
Com Postgres: `docker compose up --build`

## Decisões de projeto
- Valores monetários em `Numeric`, nunca `float` no banco
- Unicidade (`document`, `transaction_id`, `contract+due_date`) garantida por constraints, não só por código
- Integrações bancárias (PIX/boleto/webhook) ficam de fora de propósito: exigem contrato e credenciais. Próximo passo: camada de "adaptadores" por banco

## Roadmap
Login e perfis · Alembic · importação de Excel/OFX · conciliação bancária · contas a pagar · notificações (e-mail/WhatsApp) · automações com n8n · relatórios em PDF/Excel · React/Next.js
