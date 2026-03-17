-- ============================================================
-- ClinicAnalytics — Schema Inicial
-- Execute no SQL Editor do Supabase (ou via migration)
-- ============================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "pgcrypto";


-- ============================================================
-- CLÍNICAS
-- ============================================================
CREATE TABLE IF NOT EXISTS clinics (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(255) NOT NULL,
    cnpj        VARCHAR(20),
    phone       VARCHAR(20),
    email       VARCHAR(255),
    address     TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- USUÁRIOS DA CLÍNICA (integra com Supabase Auth)
-- ============================================================
CREATE TABLE IF NOT EXISTS clinic_users (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id  UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name       VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    role       VARCHAR(20)  NOT NULL DEFAULT 'staff',  -- admin | manager | staff
    is_active  BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ  DEFAULT NOW()
);

-- ============================================================
-- PACIENTES
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id             UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name                  VARCHAR(255) NOT NULL,
    date_of_birth         DATE,
    phone                 VARCHAR(20),
    email                 VARCHAR(255),
    cpf                   VARCHAR(14),
    gender                VARCHAR(20),
    address               TEXT,
    notes                 TEXT,
    last_appointment_date DATE,   -- atualizado automaticamente a cada nova transação
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patients_clinic   ON patients(clinic_id);
CREATE INDEX idx_patients_last_appt ON patients(last_appointment_date);

-- ============================================================
-- REGRAS DE STATUS DE PACIENTE (configuráveis por clínica)
-- ============================================================
CREATE TABLE IF NOT EXISTS patient_status_rules (
    id                       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id                UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name                     VARCHAR(255) NOT NULL,
    min_age_years            INTEGER,        -- NULL = sem mínimo
    max_age_years            INTEGER,        -- NULL = sem máximo
    return_interval_days     INTEGER NOT NULL,
    attention_threshold_days INTEGER NOT NULL,
    danger_threshold_days    INTEGER NOT NULL,
    is_active                BOOLEAN NOT NULL DEFAULT TRUE,
    created_at               TIMESTAMPTZ DEFAULT NOW()
);

-- Regras padrão sugeridas (exemplos):
-- INSERT INTO patient_status_rules (name, max_age_years, return_interval_days, attention_threshold_days, danger_threshold_days)
-- VALUES
--   ('Bebês (< 1 ano)',   0,  30,  15,  30),
--   ('Crianças (1-5)',    5,  90,  30,  60),
--   ('Adultos',        NULL, 180,  30,  90);

-- ============================================================
-- PRODUTOS E SERVIÇOS
-- ============================================================
CREATE TABLE IF NOT EXISTS products (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id     UUID          NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name          VARCHAR(255)  NOT NULL,
    type          VARCHAR(20)   NOT NULL DEFAULT 'service',  -- product | service
    description   TEXT,
    price         NUMERIC(12,2) NOT NULL DEFAULT 0,
    variable_cost NUMERIC(12,2) NOT NULL DEFAULT 0,  -- custo variável unitário (p/ margem de contribuição)
    is_active     BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ   DEFAULT NOW(),
    updated_at    TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX idx_products_clinic ON products(clinic_id);

-- ============================================================
-- TRANSAÇÕES (FATURAMENTO)
-- ============================================================
CREATE TABLE IF NOT EXISTS transactions (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id      UUID          NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id     UUID          REFERENCES patients(id),
    date           DATE          NOT NULL,
    total_amount   NUMERIC(12,2) NOT NULL,
    payment_method VARCHAR(50),   -- dinheiro | cartão_crédito | cartão_débito | pix | convênio
    status         VARCHAR(20)   NOT NULL DEFAULT 'completed',  -- pending | completed | cancelled
    notes          TEXT,
    created_at     TIMESTAMPTZ   DEFAULT NOW(),
    updated_at     TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX idx_transactions_clinic ON transactions(clinic_id);
CREATE INDEX idx_transactions_date   ON transactions(date);
CREATE INDEX idx_transactions_patient ON transactions(patient_id);

-- ============================================================
-- ITENS DE TRANSAÇÃO
-- ============================================================
CREATE TABLE IF NOT EXISTS transaction_items (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID          NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    product_id     UUID          REFERENCES products(id),
    quantity       NUMERIC(10,2) NOT NULL DEFAULT 1,
    unit_price     NUMERIC(12,2) NOT NULL,
    discount       NUMERIC(12,2) NOT NULL DEFAULT 0,
    total_price    NUMERIC(12,2) NOT NULL,  -- (unit_price * qty) - discount
    variable_cost  NUMERIC(12,2) NOT NULL DEFAULT 0,  -- custo variável no momento da venda
    created_at     TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX idx_transaction_items_tx  ON transaction_items(transaction_id);
CREATE INDEX idx_transaction_items_prod ON transaction_items(product_id);

-- ============================================================
-- CATEGORIAS DE GASTO
-- ============================================================
CREATE TABLE IF NOT EXISTS expense_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id   UUID         NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    name        VARCHAR(255) NOT NULL,
    type        VARCHAR(20)  NOT NULL,  -- fixed | variable
    description TEXT,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX idx_expense_cat_clinic ON expense_categories(clinic_id);

-- Categorias sugeridas (remova o comentário para inserir):
-- INSERT INTO expense_categories (name, type) VALUES
--   ('Aluguel',           'fixed'),
--   ('Folha de Pagamento','fixed'),
--   ('Contabilidade',     'fixed'),
--   ('Energia / Água',    'fixed'),
--   ('Internet / Tel.',   'fixed'),
--   ('Marketing',         'variable'),
--   ('Materiais',         'variable'),
--   ('Comissões',         'variable'),
--   ('Manutenção',        'variable');

-- ============================================================
-- GASTOS / DESPESAS
-- ============================================================
CREATE TABLE IF NOT EXISTS expenses (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id      UUID          NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    category_id    UUID          REFERENCES expense_categories(id),
    description    VARCHAR(255),
    amount         NUMERIC(12,2) NOT NULL,
    date           DATE          NOT NULL,
    payment_method VARCHAR(50),
    status         VARCHAR(20)   NOT NULL DEFAULT 'paid',  -- pending | paid
    recurrent      BOOLEAN       NOT NULL DEFAULT FALSE,
    notes          TEXT,
    created_at     TIMESTAMPTZ   DEFAULT NOW(),
    updated_at     TIMESTAMPTZ   DEFAULT NOW()
);

CREATE INDEX idx_expenses_clinic ON expenses(clinic_id);
CREATE INDEX idx_expenses_date   ON expenses(date);

-- ============================================================
-- METAS
-- ============================================================
CREATE TABLE IF NOT EXISTS goals (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id   UUID          NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    type        VARCHAR(50)   NOT NULL,   -- revenue | profit | fixed_expenses | variable_expenses | product_revenue
    product_id  UUID          REFERENCES products(id),
    period_type VARCHAR(20)   NOT NULL DEFAULT 'monthly',  -- monthly | annual
    year        INTEGER       NOT NULL,
    month       INTEGER,                  -- 1-12; NULL se period_type = 'annual'
    amount      NUMERIC(12,2) NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT NOW(),
    updated_at  TIMESTAMPTZ   DEFAULT NOW(),
    UNIQUE (clinic_id, type, product_id, year, month)  -- evita duplicidade
);

CREATE INDEX idx_goals_clinic ON goals(clinic_id);

-- ============================================================
-- AGENDAMENTOS
-- ============================================================
CREATE TABLE IF NOT EXISTS appointments (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clinic_id    UUID        NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    patient_id   UUID        NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    product_id   UUID        REFERENCES products(id),
    scheduled_at TIMESTAMPTZ NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'scheduled',  -- scheduled | completed | cancelled | no_show
    notes        TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_appointments_clinic  ON appointments(clinic_id);
CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_date    ON appointments(scheduled_at);

-- ============================================================
-- FUNÇÃO: atualiza updated_at automaticamente
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Aplica o trigger em todas as tabelas com updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOREACH t IN ARRAY ARRAY[
        'clinics','patients','products','transactions',
        'expenses','goals','appointments'
    ] LOOP
        EXECUTE format(
            'CREATE TRIGGER trg_%s_updated_at
             BEFORE UPDATE ON %s
             FOR EACH ROW EXECUTE FUNCTION update_updated_at();', t, t
        );
    END LOOP;
END;
$$;

-- ============================================================
-- ROW LEVEL SECURITY (RLS) — habilita isolamento por clínica
-- ============================================================
ALTER TABLE clinics            ENABLE ROW LEVEL SECURITY;
ALTER TABLE clinic_users       ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients           ENABLE ROW LEVEL SECURITY;
ALTER TABLE products           ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions       ENABLE ROW LEVEL SECURITY;
ALTER TABLE transaction_items  ENABLE ROW LEVEL SECURITY;
ALTER TABLE expense_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE expenses           ENABLE ROW LEVEL SECURITY;
ALTER TABLE goals              ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments       ENABLE ROW LEVEL SECURITY;

-- Nota: configure as policies de acordo com sua lógica de autenticação.
-- Exemplo básico (usuários só veem dados da sua clínica):
-- CREATE POLICY "usuarios_da_clinica" ON patients
--     USING (clinic_id = (SELECT clinic_id FROM clinic_users WHERE id = auth.uid()));
