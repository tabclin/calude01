"use client";
/**
 * Dashboard Principal — Nível 1
 * Exibe os KPIs de alto nível e o gráfico de evolução financeira.
 */
import { useEffect, useState } from "react";
import { dashboardApi, Level1Summary, MonthlyTrend, Level2Revenue } from "@/lib/api";
import { KPICard } from "@/components/dashboard/KPICard";
import { RevenueChart } from "@/components/dashboard/RevenueChart";
import { TopProducts } from "@/components/dashboard/TopProducts";

// TODO: substituir pelo ID real da clínica (virá da autenticação)
const CLINIC_ID = process.env.NEXT_PUBLIC_CLINIC_ID ?? "demo-clinic-id";

function fmt(value: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL",
    maximumFractionDigits: 0 }).format(value);
}

export default function DashboardPage() {
  const now = new Date();
  const [year,  setYear]  = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);

  const [summary,  setSummary]  = useState<Level1Summary | null>(null);
  const [trend,    setTrend]    = useState<MonthlyTrend[]>([]);
  const [revenue,  setRevenue]  = useState<Level2Revenue | null>(null);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      dashboardApi.getSummary(CLINIC_ID, year, month),
      dashboardApi.getTrend(CLINIC_ID, 12),
      dashboardApi.getRevenue(CLINIC_ID, year, month),
    ]).then(([s, t, r]) => {
      setSummary(s.data);
      setTrend(t.data);
      setRevenue(r.data);
    }).finally(() => setLoading(false));
  }, [year, month]);

  const MONTHS = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

  return (
    <main className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Dashboard Gerencial</h1>
          <p className="text-sm text-gray-500 mt-0.5">Visão financeira da clínica</p>
        </div>

        {/* Filtro de período */}
        <div className="flex gap-2">
          <select
            className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white shadow-sm"
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
          >
            {MONTHS.map((m, i) => (
              <option key={i} value={i + 1}>{m}</option>
            ))}
          </select>
          <select
            className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white shadow-sm"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
          >
            {[2023, 2024, 2025, 2026].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-gray-400 py-20">Carregando...</div>
      ) : (
        <>
          {/* ── Nível 1: KPIs principais ─────────────────────────────── */}
          <section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <KPICard
              title="Faturamento"
              value={fmt(summary?.revenue ?? 0)}
              percent={summary?.revenue_goal_pct}
              subtitle={`Meta: ${fmt(summary?.revenue_goal ?? 0)}`}
              colorVariant="blue"
            />
            <KPICard
              title="Gastos Totais"
              value={fmt(summary?.expenses ?? 0)}
              colorVariant="red"
            />
            <KPICard
              title="Lucro Real"
              value={fmt(summary?.profit ?? 0)}
              percent={summary?.profit_goal_pct}
              subtitle={`Meta: ${fmt(summary?.profit_goal ?? 0)}`}
              colorVariant={(summary?.profit ?? 0) >= 0 ? "green" : "red"}
            />
            <KPICard
              title="Margem de Lucro"
              value={`${(summary?.profit_margin_pct ?? 0).toFixed(1)}%`}
              subtitle="Lucro / Faturamento"
              colorVariant="yellow"
            />
          </section>

          {/* ── Gráfico de evolução ───────────────────────────────────── */}
          <section className="mb-8">
            <RevenueChart data={trend} />
          </section>

          {/* ── Ranking de produtos ───────────────────────────────────── */}
          <section>
            <TopProducts products={revenue?.top_products ?? []} />
          </section>
        </>
      )}
    </main>
  );
}
