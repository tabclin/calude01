/**
 * Cliente centralizado da API.
 * Todas as chamadas ao backend passam por aqui.
 */
import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const api = axios.create({ baseURL: BASE_URL });

// ── Tipos ────────────────────────────────────────────────────────────────────

export interface Level1Summary {
  revenue: number;
  expenses: number;
  profit: number;
  profit_goal: number;
  profit_goal_pct: number;
  profit_margin_pct: number;
  revenue_goal: number;
  revenue_goal_pct: number;
}

export interface ProductRanking {
  product_id: string;
  product_name: string;
  quantity_sold: number;
  revenue: number;
  revenue_goal: number | null;
  revenue_goal_pct: number | null;
}

export interface Level2Revenue {
  total_revenue: number;
  revenue_goal: number;
  revenue_goal_pct: number;
  top_products: ProductRanking[];
}

export interface ExpenseCategorySummary {
  category_id: string;
  category_name: string;
  type: "fixed" | "variable";
  actual: number;
  goal: number | null;
  efficiency_pct: number | null;
}

export interface Level2Expenses {
  total_expenses: number;
  fixed_expenses: number;
  variable_expenses: number;
  fixed_goal: number;
  variable_goal: number;
  fixed_efficiency_pct: number | null;
  variable_efficiency_pct: number | null;
  by_category: ExpenseCategorySummary[];
}

export interface ProductContribution {
  product_id: string;
  product_name: string;
  revenue: number;
  variable_cost: number;
  contribution_margin: number;
  contribution_margin_pct: number;
}

export interface Level3ContributionMargin {
  revenue: number;
  total_variable_cost: number;
  contribution_margin: number;
  contribution_margin_pct: number;
  by_product: ProductContribution[];
}

export interface PatientWithStatus {
  id: string;
  name: string;
  phone: string | null;
  date_of_birth: string | null;
  last_appointment_date: string | null;
  age_years: number | null;
  recency_days: number | null;
  frequency: number;
  monetary: number;
  status: "OK" | "ATENÇÃO" | "PERIGO" | "NOVO";
  days_overdue: number;
}

export interface MonthlyTrend {
  year: number;
  month: number;
  revenue: number;
  expenses: number;
  profit: number;
}

// ── Funções de API ────────────────────────────────────────────────────────────

export const dashboardApi = {
  getSummary: (clinicId: string, year?: number, month?: number) =>
    api.get<Level1Summary>("/dashboard/summary", { params: { clinic_id: clinicId, year, month } }),

  getRevenue: (clinicId: string, year?: number, month?: number) =>
    api.get<Level2Revenue>("/dashboard/revenue", { params: { clinic_id: clinicId, year, month } }),

  getExpenses: (clinicId: string, year?: number, month?: number) =>
    api.get<Level2Expenses>("/dashboard/expenses", { params: { clinic_id: clinicId, year, month } }),

  getContribution: (clinicId: string, year?: number, month?: number) =>
    api.get<Level3ContributionMargin>("/dashboard/contribution", { params: { clinic_id: clinicId, year, month } }),

  getTrend: (clinicId: string, months = 12) =>
    api.get<MonthlyTrend[]>("/dashboard/trend", { params: { clinic_id: clinicId, months } }),
};

export const patientsApi = {
  list: (clinicId: string, status?: string) =>
    api.get<PatientWithStatus[]>("/patients", { params: { clinic_id: clinicId, status } }),
};
