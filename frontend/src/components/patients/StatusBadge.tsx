"use client";
import clsx from "clsx";

type Status = "OK" | "ATENÇÃO" | "PERIGO" | "NOVO";

const config: Record<Status, { label: string; className: string }> = {
  OK:      { label: "OK",      className: "bg-green-100 text-green-700 border-green-200" },
  ATENÇÃO: { label: "ATENÇÃO", className: "bg-yellow-100 text-yellow-700 border-yellow-200" },
  PERIGO:  { label: "PERIGO",  className: "bg-red-100 text-red-700 border-red-200" },
  NOVO:    { label: "NOVO",    className: "bg-gray-100 text-gray-500 border-gray-200" },
};

export function StatusBadge({ status }: { status: Status }) {
  const { label, className } = config[status] ?? config.NOVO;
  return (
    <span className={clsx("inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border", className)}>
      {label}
    </span>
  );
}
