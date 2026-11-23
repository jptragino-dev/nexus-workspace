# 🚀 NEXUS WORKSPACE

### Sistema Web de Gestão Administrativa

O **Nexus Workspace** é um projeto de aplicação web desenvolvido para explorar a organização e a centralização de processos administrativos em uma única plataforma.

O projeto reúne conceitos de desenvolvimento back-end, interface web, persistência de dados e organização de sistemas.

## 🎯 Objetivo

Desenvolver uma solução web que facilite o gerenciamento de informações administrativas, oferecendo uma interface organizada e uma estrutura preparada para evolução e implementação de novas funcionalidades.

## 🛠️ Tecnologias utilizadas

- 🐍 **Python** — Desenvolvimento back-end.
- ⚡ **FastAPI** — Construção da API.
- 🌐 **HTML** — Estrutura da interface.
- 🎨 **CSS** — Estilização da aplicação.
- 💻 **JavaScript** — Interatividade.
- 🗄️ **SQLite** — Banco de dados utilizado no desenvolvimento.
- 🐳 **Docker** — Configuração de ambiente em contêineres.
- 🧪 **Pytest** — Estrutura de testes automatizados.

## 📂 Estrutura do projeto

```text
nexusAPP/
├── app/
│   ├── static/
│   │   └── index.html
│   ├── main.py
│   ├── db.py
│   ├── models.py
│   ├── seed.py
│   ├── validators.py
│   └── atualizar_precos.py
├── tests/
│   └── test_app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 💡 Funcionalidades e conceitos

O projeto foi estruturado para trabalhar com:

- Organização de informações administrativas.
- Interface web para interação com o sistema.
- API para comunicação entre os componentes.
- Persistência e manipulação de dados.
- Validação de informações.
- Estrutura de testes e execução em contêineres.

*As funcionalidades estão sujeitas à implementação e evolução do projeto.*

## ⚙️ Instalação

Clone o repositório:

```bash
git clone https://github.com/jptragino-dev/nexus-workspace.git
```

Acesse a pasta:

```bash
cd nexus-workspace
```

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
```

No Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

A inicialização da aplicação deve seguir a configuração definida em `app/main.py` ou `docker-compose.yml`.

## 📸 Demonstração

Espaço reservado para imagens da interface do Nexus Workspace.

*Dashboard e demais telas poderão ser adicionados futuramente.*

## 🔒 Dados de demonstração

O projeto é destinado a fins educacionais e de portfólio. Os dados de demonstração devem ser fictícios, sem informações confidenciais de pessoas ou empresas.

## 📈 Próximas melhorias

- Aprimoramento da interface.
- Expansão das funcionalidades administrativas.
- Melhoria das validações.
- Ampliação dos testes automatizados.
- Evolução da documentação técnica.

## 👨‍💻 Desenvolvedor

**João Pedro Moreira da Silva Tragino**

Estudante de Análise e Desenvolvimento de Sistemas (ADS).

GitHub: [@jptragino-dev](https://github.com/jptragino-dev)

---

⭐ Projeto desenvolvido para aprendizado, prática e evolução profissional em desenvolvimento de software.
