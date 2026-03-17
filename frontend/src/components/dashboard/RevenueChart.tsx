"use client";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { MonthlyTrend } from "@/lib/api";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

interface Props {
  data: MonthlyTrend[];
}

const MONTHS = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

function fmt(value: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL",
    maximumFractionDigits: 0 }).format(value);
}

/**
 * Gráfico de área empilhada com evolução mensal de receita, gastos e lucro.
 */
export function RevenueChart({ data }: Props) {
  const chartData = data.map((d) => ({
    name: MONTHS[d.month - 1],
    Receita: Number(d.revenue),
    Gastos:  Number(d.expenses),
    Lucro:   Number(d.profit),
  }));

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-600 mb-4">
        Evolução Financeira — últimos meses
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ top: 4, right: 16, bottom: 0, left: 0 }}>
          <defs>
            <linearGradient id="gRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}   />
            </linearGradient>
            <linearGradient id="gProfit" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%"  stopColor="#10b981" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#10b981" stopOpacity={0}   />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis tickFormatter={(v) => `R$${(v/1000).toFixed(0)}k`} tick={{ fontSize: 11 }} />
          <Tooltip formatter={(value: number) => fmt(value)} />
          <Legend />
          <Area type="monotone" dataKey="Receita" stroke="#3b82f6" fill="url(#gRevenue)" strokeWidth={2} />
          <Area type="monotone" dataKey="Gastos"  stroke="#ef4444" fill="none"            strokeWidth={2} strokeDasharray="4 2" />
          <Area type="monotone" dataKey="Lucro"   stroke="#10b981" fill="url(#gProfit)"  strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
