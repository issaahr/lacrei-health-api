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

Para este desafio, optei pelo Render porque permite montar staging e produção rapidamente, sem custo e sem a complexidade operacional da AWS. A arquitetura é portável e, caso a API migre para AWS no futuro, o pipeline continua o mesmo (Docker + CI/CD).

### Por que API Key (e não JWT ou outra opção)?

- **Simplicidade**: Requisito do desafio é "autenticação básica"
- **Stateless**: Não requer banco para sessões
- **Fácil integração**: Header único em todas as requisições
- **Escalável**: Pode evoluir para JWT posteriormente sem quebrar contratos

### Por que SQLite nos testes?

- **Velocidade**: Testes rodam em memória (`:memory:`)
- **Isolamento**: Cada execução começa limpa
- **CI/CD**: Não requer PostgreSQL no GitHub Actions
- **Django ORM**: Abstrai diferenças entre bancos

---

## Índice

- [Rodar Local](#rodar-local)
- [Rodar via Docker](#rodar-via-docker)
- [Rodar Testes](#rodar-testes)
- [Endpoints da API](#endpoints-da-api)
- [Autenticação (API Key)](#autenticação-api-key)
- [Exemplos de Uso (curl)](#exemplos-de-uso-curl)
- [Códigos de Erro](#códigos-de-erro)
- [Segurança e Boas Práticas](#segurança-e-boas-práticas)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Deploy no Render](#deploy-no-render)

---

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

---

## Rodar Testes

### Local (com Poetry)

```bash
# Rodar todos os testes
poetry run pytest -v

# Rodar por domínio
poetry run pytest professionals/ -v
poetry run pytest appointments/ -v

# Rodar com cobertura
poetry run pytest -v --cov=. --cov-report=term-missing
```

### Via Docker

```bash
# Rodar todos os testes
docker-compose exec web pytest -v

# Rodar por domínio
docker-compose exec web pytest professionals/ -v
docker-compose exec web pytest appointments/ -v
```

### Estrutura dos Testes

```
professionals/tests/test_api.py   → Testes de /api/professionals/
appointments/tests/test_api.py    → Testes de /api/appointments/
tests/test_api.py                 → Testes de rotas públicas
```

Cada endpoint testa na ordem: **Auth (401) → Validação (400) → Sucesso (2xx)**

**professionals/tests/** - Testes de `/api/professionals/`

- `ListProfessionalsTest` - GET (listar)
- `CreateProfessionalTest` - POST (criar)
- `RetrieveProfessionalTest` - GET by ID (detalhar)
- `UpdateProfessionalTest` - PUT (atualizar)
- `DeleteProfessionalTest` - DELETE (excluir)

**appointments/tests/** - Testes de `/api/appointments/`

- `ListAppointmentsTest` - GET (listar)
- `CreateAppointmentTest` - POST (criar)
- `RetrieveAppointmentTest` - GET by ID (detalhar)
- `DeleteAppointmentTest` - DELETE (excluir)
- `ListAppointmentsByProfessionalTest` - GET por profissional

**tests/** - Rotas públicas

- `PublicRoutesTest` - swagger, redoc, health (sem auth)

---

## Lint

```bash
# Verificar
poetry run ruff check .

# Auto-corrigir
poetry run ruff check . --fix
```

---

## Endpoints da API

### Profissionais

| Método | Endpoint                     | Descrição              |
|--------|------------------------------|------------------------|
| GET    | `/api/professionals/`        | Listar profissionais   |
| POST   | `/api/professionals/`        | Criar profissional     |
| GET    | `/api/professionals/{id}/`   | Detalhar profissional  |
| PUT    | `/api/professionals/{id}/`   | Atualizar profissional |
| PATCH  | `/api/professionals/{id}/`   | Atualizar parcialmente |
| DELETE | `/api/professionals/{id}/`   | Excluir profissional   |

### Consultas

| Método | Endpoint                               | Descrição                  |
|--------|----------------------------------------|----------------------------|
| GET    | `/api/appointments/`                   | Listar consultas           |
| POST   | `/api/appointments/`                   | Criar consulta             |
| GET    | `/api/appointments/{id}/`              | Detalhar consulta          |
| PUT    | `/api/appointments/{id}/`              | Atualizar consulta         |
| PATCH  | `/api/appointments/{id}/`              | Atualizar parcialmente     |
| DELETE | `/api/appointments/{id}/`              | Excluir consulta           |
| GET    | `/api/appointments/professional/{id}/` | Consultas por profissional |

### Utilidades

| Método | Endpoint     | Descrição            | Autenticação |
|--------|--------------|----------------------|--------------|
| GET    | `/health/`   | Health check         | Não          |
| GET    | `/swagger/`  | Documentação Swagger | Não          |
| GET    | `/redoc/`    | Documentação ReDoc   | Não          |

---

## Autenticação (API Key)

### Como Funciona

Todas as rotas `/api/*` requerem o header `X-API-KEY` quando a variável de ambiente `API_KEY` está configurada.

```
X-API-KEY: sua-chave-secreta-aqui
```

### Rotas Públicas (sem autenticação)

- `/swagger/` - Documentação Swagger UI
- `/redoc/` - Documentação ReDoc
- `/health/` - Health check
- `/static/*` - Arquivos estáticos

### Geração da API Key

A API Key deve ser uma string aleatória e segura. Recomendações:

```bash
# Gerar uma chave segura (Linux/Mac)
openssl rand -hex 32

# Ou via Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Exemplo de chave gerada:**

```
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### Boas Práticas para API Key

1. **Nunca commitar a chave** no repositório
2. **Usar variáveis de ambiente** para configurar
3. **Rotacionar periodicamente** (ex: a cada 90 dias)
4. **Usar chaves diferentes** para staging e produção
5. **Mínimo 32 caracteres** para segurança adequada
6. **Transmitir apenas via HTTPS** em produção

---

## Exemplos de Uso (curl)

### Configuração Inicial

```bash
# Definir variáveis para facilitar os exemplos
export API_URL="http://localhost:8000"
export API_KEY="sua-chave-aqui"
```

### Profissionais

#### Criar Profissional

```bash
curl -X POST "$API_URL/api/professionals/" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "social_name": "Dra. Maria Silva",
    "profession": "Cardiologista",
    "address": "Rua das Flores, 123",
    "email": "maria.silva@email.com",
    "phone": "(11) 99999-9999"
  }'
```

**Resposta (201 Created):**

```json
{
  "id": 1,
  "social_name": "Dra. Maria Silva",
  "profession": "Cardiologista",
  "address": "Rua das Flores, 123",
  "email": "maria.silva@email.com",
  "phone": "+5511999999999",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Listar Profissionais

```bash
curl -X GET "$API_URL/api/professionals/" \
  -H "X-API-KEY: $API_KEY"
```

#### Buscar Profissional por ID

```bash
curl -X GET "$API_URL/api/professionals/1/" \
  -H "X-API-KEY: $API_KEY"
```

#### Atualizar Profissional

```bash
curl -X PUT "$API_URL/api/professionals/1/" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "social_name": "Dra. Maria Santos",
    "profession": "Cardiologista",
    "address": "Av. Paulista, 1000",
    "email": "maria.santos@email.com",
    "phone": "(11) 98888-8888"
  }'
```

#### Excluir Profissional

```bash
curl -X DELETE "$API_URL/api/professionals/1/" \
  -H "X-API-KEY: $API_KEY"
```

### Consultas

#### Criar Consulta

```bash
curl -X POST "$API_URL/api/appointments/" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "date": "2024-12-20T14:30:00Z",
    "professional": 1
  }'
```

**Resposta (201 Created):**

```json
{
  "id": 1,
  "date": "2024-12-20T14:30:00Z",
  "professional": 1,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Listar Consultas

```bash
curl -X GET "$API_URL/api/appointments/" \
  -H "X-API-KEY: $API_KEY"
```

#### Listar Consultas de um Profissional

```bash
curl -X GET "$API_URL/api/appointments/professional/1/" \
  -H "X-API-KEY: $API_KEY"
```

#### Atualizar Data da Consulta

```bash
curl -X PATCH "$API_URL/api/appointments/1/" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $API_KEY" \
  -d '{
    "date": "2024-12-21T15:00:00Z"
  }'
```

#### Excluir Consulta

```bash
curl -X DELETE "$API_URL/api/appointments/1/" \
  -H "X-API-KEY: $API_KEY"
```

### Health Check

```bash
curl -X GET "$API_URL/health/"
```

**Resposta:**

```json
{"status": "ok"}
```

---

## Códigos de Erro

### 400 Bad Request - Erro de Validação

```json
{
  "social_name": ["Mínimo 3 caracteres"],
  "email": ["Email já cadastrado"],
  "phone": ["Telefone inválido"]
}
```

**Erros comuns de validação:**

| Campo         | Erro                      | Descrição                                 |
|---------------|---------------------------|-------------------------------------------|
| `social_name` | Mínimo 3 caracteres       | Nome muito curto                          |
| `social_name` | Nome inválido             | Contém números ou símbolos                |
| `profession`  | Mínimo 3 caracteres       | Profissão muito curta                     |
| `address`     | Mínimo 5 caracteres       | Endereço muito curto                      |
| `email`       | Email já cadastrado       | Já existe no sistema                      |
| `phone`       | Telefone inválido         | Número inválido para o Brasil             |
| `phone`       | Formato de telefone inválido | Não foi possível interpretar o número  |
| `date`        | Data não pode ser no passado | Consulta deve ser futura               |
| `date`        | Mínimo 30 minutos de antecedência | Muito em cima da hora            |
| `date`        | Máximo 365 dias no futuro | Data muito distante                       |
| `date`        | Conflito de horário       | Intervalo mínimo de 60 min entre consultas |
| `professional`| Profissional não encontrado | ID não existe no sistema                |

### 401 Unauthorized - Não Autenticado

```json
{
  "erro": "API Key inválida ou ausente"
}
```

### 404 Not Found - Não Encontrado

```json
{
  "detail": "Não encontrado."
}
```

### 500 Internal Server Error

```json
{
  "detail": "Erro interno do servidor"
}
```

---

## Segurança e Boas Práticas

### CORS (Cross-Origin Resource Sharing)

A API utiliza `django-cors-headers` para controle de CORS. Configure as origens permitidas:

```env
# env/api.env
CORS_ALLOWED_ORIGINS=https://seu-frontend.com,https://admin.seu-frontend.com
```

**Em desenvolvimento:**

```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Headers de Segurança Recomendados

Para produção, considere adicionar um proxy reverso (nginx) com:

```nginx
# Headers de segurança
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Melhorias de Segurança Futuras

| Melhoria             | Descrição                          | Prioridade |
|----------------------|------------------------------------|------------|
| Rate Limiting        | Limitar requisições por IP/API Key | Alta       |
| JWT                  | Migrar para tokens JWT com refresh | Média      |
| Criptografia de dados| Campos sensíveis criptografados    | Média      |

### Checklist de Segurança para Deploy

- [ ] `DEBUG=False` em produção
- [ ] `SECRET_KEY` única e segura (64+ caracteres)
- [ ] `API_KEY` diferente para cada ambiente
- [ ] HTTPS obrigatório (certificado SSL)
- [ ] `ALLOWED_HOSTS` configurado corretamente
- [ ] `CORS_ALLOWED_ORIGINS` restrito às origens necessárias
- [ ] Logs de erro configurados (sem expor dados sensíveis)
- [ ] Banco de dados com senha forte
- [ ] Variáveis de ambiente não commitadas

---

## Variáveis de Ambiente

Copie os arquivos `.env.example` e configure conforme seu ambiente.

### api.env

| Variável               | Descrição                        | Exemplo                      |
|------------------------|----------------------------------|------------------------------|
| `SECRET_KEY`           | Chave secreta Django (64+ chars) | `django-insecure-abc123...`  |
| `DEBUG`                | Modo debug (True/False)          | `False`                      |
| `ALLOWED_HOSTS`        | Hosts permitidos                 | `localhost,api.exemplo.com`  |
| `API_KEY`              | Chave de autenticação da API     | `sua-chave-segura-32-chars`  |
| `CORS_ALLOWED_ORIGINS` | Origens CORS permitidas          | `https://frontend.com`       |
| `LOG_LEVEL`            | Nível de log                     | `INFO`                       |

### postgres.env

| Variável            | Descrição        | Exemplo           |
|---------------------|------------------|-------------------|
| `POSTGRES_USER`     | Usuário do banco | `lacrei_user`     |
| `POSTGRES_PASSWORD` | Senha do banco   | `senha-segura-123`|
| `POSTGRES_DB`       | Nome do banco    | `lacrei_health`   |
| `DATABASE_PORT`     | Porta do banco   | `5432`            |

---

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

| Secret                     | Descrição                          |
|----------------------------|------------------------------------|
| `DOCKERHUB_USERNAME`       | Usuário do Docker Hub              |
| `DOCKERHUB_TOKEN`          | Token de acesso do Docker Hub      |
| `RENDER_DEPLOY_HOOK_STAGE` | Webhook de deploy staging          |
| `RENDER_DEPLOY_HOOK_PROD`  | Webhook de deploy produção         |
| `STAGING_URL`              | URL do staging (para health check) |
| `PRODUCTION_URL`           | URL da produção (para health check)|

**Fluxo:**

```
feature → PR stage → merge → build → Docker Hub → deploy staging
stage → PR production → merge → build → Docker Hub → deploy produção
```

**Tags de imagem geradas:**

- `stage` / `production` → branch atual
- `<sha>` → hash do commit (para histórico)

---

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

---

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

| Método | Endpoint               | Descrição                    |
|--------|------------------------|------------------------------|
| POST   | `/api/payments/`       | Criar cobrança para consulta |
| GET    | `/api/payments/{id}/`  | Status do pagamento          |
| POST   | `/api/webhooks/asaas/` | Receber confirmações         |

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

> **Obs**: Essa integração não foi implementada, apenas sugerida conforme o desafio. A arquitetura é baseada na documentação oficial do Assas e pode ser
evoluída para o fluxo real caso necessário.

---

## Licença

Este projeto foi desenvolvido como parte de um desafio técnico.
