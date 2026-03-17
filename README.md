# ClinicAnalytics

Sistema web de análise gerencial para clínicas de saúde e estética.

---

## Arquitetura

```
clinic-analytics/
├── backend/          # FastAPI + SQLAlchemy + Python
├── frontend/         # Next.js + Tailwind CSS + Recharts
├── supabase/         # Migrations SQL para o Supabase
└── docker-compose.yml
```

---

## Stack

| Camada     | Tecnologia                       |
|------------|----------------------------------|
| Backend    | Python 3.12 + FastAPI            |
| ORM        | SQLAlchemy 2.0                   |
| Banco      | Supabase (PostgreSQL)            |
| Frontend   | Next.js 15 + Tailwind CSS        |
| Gráficos   | Recharts                         |
| Deploy     | Render.com                       |

---

## Níveis de Análise

| Nível | Descrição                            |
|-------|--------------------------------------|
| 1     | Visão geral: receita, gastos, lucro  |
| 2-A   | Faturamento detalhado por produto    |
| 2-B   | Gastos detalhados por categoria      |
| 3     | Margem de contribuição               |
| 4     | Carteira de pacientes com RFM        |

---

## Setup Local

### 1. Backend

```bash
cd backend
cp .env.example .env
# Edite .env com sua connection string do Supabase

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload
# API disponível em: http://localhost:8000
# Docs interativas: http://localhost:8000/docs
```

### 2. Banco de Dados (Supabase)

1. Crie um projeto em [supabase.com](https://supabase.com)
2. Acesse **SQL Editor** e execute o arquivo:
   ```
   supabase/migrations/001_initial_schema.sql
   ```
3. Copie a **Connection String** e cole no `.env` do backend

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edite NEXT_PUBLIC_API_URL e NEXT_PUBLIC_CLINIC_ID

npm run dev
# Disponível em: http://localhost:3000
```

---

## Deploy no Render.com

### Backend
1. Novo serviço → **Web Service**
2. Repositório: este repo, pasta `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT`
5. Adicione as variáveis de ambiente do `.env.example`

### Frontend
1. Novo serviço → **Static Site** ou **Web Service**
2. Repositório: este repo, pasta `frontend`
3. Build Command: `npm install && npm run build`
4. Start Command: `npm start`
5. Variável: `NEXT_PUBLIC_API_URL=https://sua-api.onrender.com/api/v1`

---

## Endpoints principais

| Método | Endpoint                        | Descrição                    |
|--------|---------------------------------|------------------------------|
| GET    | /api/v1/dashboard/summary       | Nível 1 — visão geral        |
| GET    | /api/v1/dashboard/revenue       | Nível 2-A — faturamento      |
| GET    | /api/v1/dashboard/expenses      | Nível 2-B — gastos           |
| GET    | /api/v1/dashboard/contribution  | Nível 3 — margem             |
| GET    | /api/v1/dashboard/trend         | Evolução mensal              |
| GET    | /api/v1/patients                | Carteira com status RFM      |
| POST   | /api/v1/transactions            | Registrar venda              |
| POST   | /api/v1/expenses                | Registrar gasto              |
| POST   | /api/v1/goals                   | Cadastrar meta               |
| GET    | /docs                           | Documentação interativa      |
