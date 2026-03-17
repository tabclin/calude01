"use client";
import { ReactNode } from "react";
import clsx from "clsx";

interface KPICardProps {
  title: string;
  value: string;
  subtitle?: string;
  percent?: number;       // 0–100
  icon?: ReactNode;
  trend?: "up" | "down" | "neutral";
  colorVariant?: "green" | "red" | "blue" | "yellow";
}

/**
 * Card de KPI reutilizável para o dashboard.
 * Exibe valor principal, barra de progresso opcional e ícone.
 */
export function KPICard({
  title, value, subtitle, percent, icon, trend, colorVariant = "blue",
}: KPICardProps) {
  const colors = {
    green:  { bar: "bg-green-500",  text: "text-green-600",  bg: "bg-green-50"  },
    red:    { bar: "bg-red-500",    text: "text-red-600",    bg: "bg-red-50"    },
    blue:   { bar: "bg-blue-500",   text: "text-blue-600",   bg: "bg-blue-50"   },
    yellow: { bar: "bg-yellow-400", text: "text-yellow-600", bg: "bg-yellow-50" },
  }[colorVariant];

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-500">{title}</span>
        {icon && (
          <span className={clsx("p-2 rounded-xl", colors.bg, colors.text)}>
            {icon}
          </span>
        )}
      </div>

      <div className="flex items-end gap-2">
        <span className="text-2xl font-bold text-gray-800">{value}</span>
        {trend && (
          <span className={clsx("text-sm mb-1", trend === "up" ? "text-green-500" : "text-red-500")}>
            {trend === "up" ? "▲" : "▼"}
          </span>
        )}
      </div>

      {subtitle && <p className="text-xs text-gray-400">{subtitle}</p>}

      {percent !== undefined && (
        <div>
          <div className="flex justify-between text-xs text-gray-400 mb-1">
            <span>Meta</span>
            <span>{percent.toFixed(1)}%</span>
          </div>
          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={clsx("h-full rounded-full transition-all", colors.bar)}
              style={{ width: `${Math.min(percent, 100)}%` }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
