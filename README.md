# Lacrei Health API

API REST para gerenciamento de profissionais de saúde e consultas médicas.

## Tecnologias

- Python 3.12
- Django 5.0 + Django REST Framework
- PostgreSQL
- Docker
- Poetry (gerenciamento de dependências)
- Gunicorn + Whitenoise
- Ruff (linting)
- GitHub Actions (CI/CD)
- Render (deploy staging + produção)
- drf-yasg (documentação Swagger/OpenAPI)

## Justificativas Técnicas

### Por que Render?

Para este desafio, optei pelo Render porque permite montar staging e produção rapidamente, sem custo e sem a complexidade operacional da AWS. A arquitetura é portável e, caso a Lacrei migre para AWS no futuro, o pipeline continua o mesmo (Docker + CI/CD).

### Por que API Key (não JWT)?

- **Simplicidade**: Requisito do desafio é "autenticação básica"
- **Stateless**: Não requer banco para sessões
- **Fácil integração**: Header único em todas as requisições
- **Escalável**: Pode evoluir para JWT posteriormente sem quebrar contratos

### Por que SQLite nos testes?

- **Velocidade**: Testes rodam em memória (`:memory:`)
- **Isolamento**: Cada execução começa limpa
- **CI/CD**: Não requer PostgreSQL no GitHub Actions
- **Django ORM**: Abstrai diferenças entre bancos

### Por que Ruff (não Black/Flake8)?

- **Performance**: 10-100x mais rápido que alternativas
- **All-in-one**: Linter + formatter em uma ferramenta
- **Compatível**: Suporta regras do Flake8, isort, pyupgrade
- **Moderno**: Escrito em Rust, mantido ativamente

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

## Proposta de Integração com Assas (Split de Pagamento)

### Arquitetura Proposta

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │───▶│   Health API    │────▶│    Assas API    │
│   (Paciente)    │     │ (Este projeto)  │     │  (Pagamentos)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │     Webhook     │
                        │  (Confirmação)  │
                        └─────────────────┘
```

### Fluxo de Pagamento com Split

```
1. Paciente agenda consulta
   POST /api/appointments/ { professional_id, date }

2. API cria cobrança no Assas com split
   POST https://api.asaas.com/v3/payments
   {
     "customer": "cus_xxx",
     "value": 150.00,
     "split": [
       { "walletId": "lacrei_wallet", "percentualValue": 20 },
       { "walletId": "professional_wallet", "percentualValue": 80 }
     ]
   }

3. Paciente paga (PIX, cartão, boleto)

4. Assas envia webhook de confirmação
   POST /api/webhooks/asaas/
   { "event": "PAYMENT_CONFIRMED", "payment": {...} }

5. API atualiza status da consulta
   Appointment.status = "confirmed"
```

### Modelo de Dados (Extensão Proposta)

```python
# professionals/models.py
class Professional(models.Model):
    # ... campos existentes ...
    asaas_wallet_id = models.CharField(max_length=50, null=True)
    split_percentage = models.DecimalField(default=80.0)  # 80% para profissional

# appointments/models.py
class Appointment(models.Model):
    # ... campos existentes ...
    status = models.CharField(choices=[
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
    ], default='pending')
    asaas_payment_id = models.CharField(max_length=50, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
```

### Endpoints Adicionais (Proposta)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/payments/` | Criar cobrança para consulta |
| GET | `/api/payments/{id}/` | Status do pagamento |
| POST | `/api/webhooks/asaas/` | Receber confirmações |

### Configuração de Ambiente

```env
# Adicionar ao api.env
ASAAS_API_KEY=sua-api-key-asaas
ASAAS_WALLET_ID=carteira-lacrei
ASAAS_ENVIRONMENT=sandbox  # ou production
LACREI_SPLIT_PERCENTAGE=20  # % que fica com Lacrei
```

### Segurança do Webhook

```python
# Validar token do webhook (conforme documentação Asaas)
from django.http import HttpResponseForbidden

def validate_asaas_webhook(request):
    token = request.headers.get('asaas-access-token')
    if token != settings.ASAAS_WEBHOOK_SECRET:
        return HttpResponseForbidden()
    return None  # Token válido
```

### Referências

- [Documentação Assas - Split](https://docs.asaas.com/reference/criar-nova-cobranca)
- [Webhooks Assas](https://docs.asaas.com/reference/webhooks)

> **Obs**: Essa integração não foi implementada, apenas sugerida conforme o desafio. A arquitetura é baseada na documentação oficial do Assas e pode ser evoluída para o fluxo real caso necessário.
