# Lacrei Health API

API REST para gerenciamento de profissionais de saúde e consultas médicas.

## Tecnologias

- Python 3.12
- Django 5.0 + Django REST Framework
- PostgreSQL
- Docker
- Gunicorn + Whitenoise
- Ruff (linting)
- GitHub Actions (CI/CD)

## Rodar Local

### Pré-requisitos

- Python 3.12+
- Poetry
- PostgreSQL

### Instalação

```bash
# Instalar dependências
poetry install

# Configurar variáveis de ambiente
cp env/api.env.example env/api.env
cp env/postgres.env.example env/postgres.env
# Editar os arquivos com suas configurações

# Rodar migrações
poetry run python manage.py migrate

# Iniciar servidor
poetry run python manage.py runserver
```

## Rodar via Docker

```bash
# Configurar variáveis de ambiente
cp env/api.env.example env/api.env
cp env/postgres.env.example env/postgres.env

# Subir containers
docker-compose up --build -d

# Rodar migrações
docker-compose exec web python manage.py migrate

# Verificar status
curl http://localhost:8000/health/
```

## Rodar Testes

```bash
# Local
poetry run pytest tests/ -v

# Docker
docker-compose exec web python -m pytest tests/ -v
```

## Lint

```bash
# Verificar
poetry run ruff check .

# Auto-corrigir
poetry run ruff check . --fix
```

## Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/professionals/` | Listar profissionais |
| POST | `/api/professionals/` | Criar profissional |
| GET | `/api/professionals/{id}/` | Detalhar profissional |
| PUT | `/api/professionals/{id}/` | Atualizar profissional |
| DELETE | `/api/professionals/{id}/` | Excluir profissional |
| GET | `/api/appointments/` | Listar consultas |
| POST | `/api/appointments/` | Criar consulta |
| GET | `/api/appointments/{id}/` | Detalhar consulta |
| PUT | `/api/appointments/{id}/` | Atualizar consulta |
| DELETE | `/api/appointments/{id}/` | Excluir consulta |
| GET | `/api/appointments/professional/{id}/` | Consultas por profissional |
| GET | `/health/` | Health check |
| GET | `/swagger/` | Documentação Swagger |
| GET | `/redoc/` | Documentação ReDoc |

## Autenticação (API Key)

Rotas `/api/*` requerem header `X-API-KEY` quando configurado.

```bash
curl -H "X-API-KEY: <sua-chave>" http://localhost:8000/api/professionals/
```

Rotas isentas: `/swagger/`, `/redoc/`, `/health/`, `/static/`

## Variáveis de Ambiente

Copie os arquivos `.env.example` e configure conforme seu ambiente.

### api.env

| Variável | Descrição |
|----------|-----------|
| SECRET_KEY | Chave secreta Django |
| DEBUG | Modo debug (True/False) |
| ALLOWED_HOSTS | Hosts permitidos (separados por vírgula) |
| API_KEY | Chave de autenticação da API |
| CORS_ALLOWED_ORIGINS | Origens CORS permitidas |
| LOG_LEVEL | Nível de log (DEBUG, INFO, WARNING, ERROR) |

### postgres.env

| Variável | Descrição |
|----------|-----------|
| POSTGRES_USER | Usuário do banco |
| POSTGRES_PASSWORD | Senha do banco |
| POSTGRES_DB | Nome do banco |
| DATABASE_PORT | Porta do banco |

## Deploy no Render

### 1. Criar Web Service

- New → Web Service → "Deploy an existing image"
- Image URL: `issahr/lacrei-health-api:stage` (ou `:production`)

### 2. Configurar Variáveis de Ambiente

No painel do Render, configurar todas as variáveis listadas acima.

### 3. Health Check

```
Settings → Health & Alerts → Health Check Path: /health/
```

### 4. Deploy Automático (CI/CD)

**Branches:**

- `stage` → Deploy para Staging
- `production` → Deploy para Produção

**Secrets necessários no GitHub:**

| Secret | Descrição |
|--------|-----------|
| DOCKERHUB_USERNAME | Usuário do Docker Hub |
| DOCKERHUB_TOKEN | Token de acesso do Docker Hub |
| RENDER_DEPLOY_HOOK_STAGE | Webhook de deploy staging |
| RENDER_DEPLOY_HOOK_PROD | Webhook de deploy produção |
| STAGING_URL | URL do staging (para health check) |
| PRODUCTION_URL | URL da produção (para health check) |

**Fluxo:**

```
feature → PR stage → merge → build → Docker Hub → deploy staging
stage → PR production → merge → build → Docker Hub → deploy produção
```

**Tags de imagem geradas:**

- `stage` / `production` → branch atual
- `<sha>` → hash do commit (para histórico)

## Estratégia de Rollback

### Arquitetura de Deploy

```
┌─────────────────────────────────────────────────────────────┐
│  1. CI/CD builda imagem e envia para Docker Hub             │
│     Tags: :production + :sha-abc123                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Render recebe webhook e inicia deploy                   │
│     - Inicia container NOVO (não derruba o atual)           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Health Check (GET /health/)                             │
│     - 8 tentativas com backoff exponencial (10s→60s)        │
└─────────────────────────────────────────────────────────────┘
                     ↓                    ↓
              [OK - 200]            [FALHA]
                   ↓                      ↓
┌──────────────────────────┐  ┌──────────────────────────────┐
│  4a. Troca tráfego       │  │  4b. Rollback automático     │
│      para container novo │  │      Mantém container        │
│      Destrói anterior    │  │      anterior ativo          │
└──────────────────────────┘  └──────────────────────────────┘
```

### Configuração do Health Check (Render)

```
Settings → Health & Alerts → Health Check Path: /health/
```

### Histórico de Versões (Docker Hub)

Cada deploy gera tags:

- `:production` / `:stage` - versão atual (sobrescrita)
- `:production-prev` / `:stage-prev` - versão anterior (backup)
- `:branch-sha` - versão específica

### Procedimentos de Rollback

#### Automático

Health check falha → CI/CD restaura versão anterior automaticamente.

#### Manual (Render Dashboard)

1. Render Dashboard → Deploys
2. Clicar "Rollback" no deploy anterior

#### Manual (Git)

```bash
git revert HEAD
git push origin production
```

### Prevenção de Falhas

| Camada | Mecanismo |
|--------|-----------|
| Pré-deploy | Testes automatizados no CI |
| Pré-merge | Preview environments (PRs) |
| Pós-deploy | Health check automático |
| Produção | Monitoramento `/health/` |

### Monitoramento

Endpoint `/health/` retorna:

```json
{"status": "ok"}
```

Pode ser integrado com:

- UptimeRobot (gratuito)
- Render Health Alerts
- Pingdom
