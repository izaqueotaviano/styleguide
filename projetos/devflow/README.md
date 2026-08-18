# DevFlow

Sistema de gestão de projetos e tarefas para times de desenvolvimento de
software — leve, rápido e focado em devs (estilo Linear/Height), construído
com **Django 5 + Django REST Framework + PostgreSQL**.

## Arquitetura

```
devflow/
├── manage.py
├── requirements.txt
├── frontend/                   # SPA React + Vite (board, home, painel de tarefa)
├── config/                     # Projeto Django (sem lógica de negócio)
│   ├── settings/               # base / development / production / test
│   ├── urls.py                 # Rotas da API v1
│   ├── asgi.py                 # Pronto para Django Channels no futuro
│   └── wsgi.py
└── apps/
    ├── core/                   # Bases compartilhadas (sem models concretos)
    │   ├── models.py           #   TimeStampedUUIDModel, SoftDeleteModel
    │   ├── permissions.py      #   require_member / require_role
    │   ├── pagination.py
    │   └── exceptions.py       #   ValidationError de domínio → HTTP 400
    ├── accounts/               # User customizado + auth
    ├── workspaces/             # Workspace (tenant) + memberships/papéis
    ├── projects/               # Project, TaskStatus, Section, Label
    ├── tasks/                  # Task (issues), subtasks, Comment
    ├── activities/             # Activity log imutável
    └── notifications/          # Notificações in-app
```

**Camadas** — cada app segue o mesmo padrão:

| Camada | Arquivo | Responsabilidade |
|---|---|---|
| Models | `models.py` | Estrutura e integridade dos dados |
| Services | `services.py` | **Toda a regra de negócio** (transações, side effects) |
| Serializers | `serializers.py` | Entrada/saída da API |
| Views | `views.py` | Autorização + orquestração fina (sem lógica de negócio) |

## Frontend (React + Vite)

Interface web no estilo Asana/Linear em `frontend/`: página inicial com
"Minhas tarefas" e grade de projetos, board Kanban com drag-and-drop,
list view, painel lateral de detalhes (campos, subtarefas e comentários
com menções), busca global e login/registro com JWT.

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 (proxy /api → localhost:8000)
```

O dev server do Vite faz proxy de `/api` para o backend em
`localhost:8000`, então basta a API estar rodando (Docker ou local).
Build de produção: `npm run build` (TypeScript estrito + Vite).

## Rodando com Docker (recomendado)

```bash
docker compose up
```

Sobe o PostgreSQL, aplica as migrations, popula os dados de demonstração e
inicia a API em `http://localhost:8000`. Logins de demonstração:
`demo / devflow123` (admin) e `dev / devflow123`.

- **Swagger UI**: http://localhost:8000/api/docs/
- **Schema OpenAPI**: http://localhost:8000/api/schema/
- **Django Admin**: http://localhost:8000/admin/

## Rodando localmente (sem Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # ajuste o Postgres se necessário
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo        # opcional: dados de demonstração
python manage.py runserver
```

Testes (usam SQLite em memória, não precisam de Postgres):

```bash
python manage.py test --settings=config.settings.test
```

O CI (GitHub Actions, `.github/workflows/devflow-tests.yml` na raiz do
repositório) roda `check`, `makemigrations --check` e a suíte de testes a
cada push/PR que tocar em `projetos/devflow/`.

## API (v1)

Autenticação: JWT (SimpleJWT). Obtenha o token em `POST /api/v1/auth/token/`
e envie `Authorization: Bearer <token>`.

| Recurso | Rota | Observações |
|---|---|---|
| Registro / Eu | `POST /auth/register/` · `GET /me/` | |
| Workspaces | `/workspaces/` | Criador vira Admin automaticamente |
| Membros | `/memberships/?workspace=` | Papéis: `admin`, `member`, `guest` |
| Projetos | `/projects/?workspace=` | Criados já com fluxo de status padrão |
| Status | `/statuses/?project=` | Configuráveis por projeto (Admin) |
| Seções | `/sections/?project=` | Colunas/agrupamentos do board |
| Labels | `/labels/?workspace=` | Compartilhadas entre projetos |
| Tarefas | `/tasks/` | Filtros: `project`, `status`, `status_category`, `section`, `assignee`, `reviewer`, `unassigned`, `type`, `priority`, `label`, `parent`, `top_level`, `due_before/after`, `search`, `ordering` |
| My Tasks | `GET /tasks/my/` | Atribuídas ao usuário autenticado |
| Mover tarefa | `POST /tasks/{id}/move/` | `{status?, section?, order?}` |
| Atribuir | `POST /tasks/{id}/assign/` | `{assignee: id \| null}` |
| Comentários | `/comments/?task=` | Menções via `@username` |
| Activity log | `GET /activities/?task=` | Somente leitura |
| Notificações | `/notifications/?unread=1` | `POST {id}/read/` · `POST read-all/` |

**Board (Kanban) e List View** usam os mesmos endpoints: o front busca
`/tasks/?project=X` e agrupa por `status`/`section`, usando `move` para
drag-and-drop. Não há endpoint separado por visão.

### Permissões

| Ação | Admin | Member | Guest |
|---|---|---|---|
| Ler tudo do workspace | ✅ | ✅ | ✅ |
| Criar/editar/mover/excluir tarefas | ✅ | ✅ | ❌ |
| Comentar | ✅ | ✅ | ✅ |
| Gerenciar projetos, seções e labels | ✅ | ✅ | ❌ |
| Configurar status, membros e workspace | ✅ | ❌ | ❌ |

## Plano de implementação por fases

- **Semana 1 — Fundação**: setup do projeto, User customizado, JWT,
  workspaces + memberships, permissões por papel, CI com testes.
- **Semana 2 — Núcleo de trabalho**: projects com status configuráveis,
  sections, labels, tasks com numeração sequencial, subtasks, My Tasks,
  filtros de board/list.
- **Semana 3 — Colaboração**: comments com menções, activity log,
  notificações in-app, soft delete/restauração, hardening de permissões.
- **Semana 4 — Qualidade e entrega**: cobertura de testes (services e API),
  documentação OpenAPI (drf-spectacular), seeds de demonstração, deploy
  (gunicorn/uvicorn + Postgres gerenciado), observabilidade básica.
- **Pós-MVP (preparado, não implementado)**: Django Channels para board em
  tempo real (ASGI já configurado), Celery para notificações por e-mail e
  digests, busca avançada, integração com GitHub.
