"use client";
import { ProductRanking } from "@/lib/api";

interface Props {
  products: ProductRanking[];
}

function fmt(value: number) {
  return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value);
}

/**
 * Tabela de ranking dos produtos/serviços mais faturados no mês.
 */
export function TopProducts({ products }: Props) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-600 mb-4">
        Ranking de Produtos / Serviços
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-gray-400 border-b border-gray-100">
              <th className="pb-2 font-medium">#</th>
              <th className="pb-2 font-medium">Produto / Serviço</th>
              <th className="pb-2 font-medium text-right">Qtd</th>
              <th className="pb-2 font-medium text-right">Receita</th>
              <th className="pb-2 font-medium text-right">% Meta</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p, i) => (
              <tr key={p.product_id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-2 text-gray-400">{i + 1}</td>
                <td className="py-2 font-medium text-gray-700">{p.product_name}</td>
                <td className="py-2 text-right text-gray-500">{Number(p.quantity_sold).toFixed(0)}</td>
                <td className="py-2 text-right font-semibold text-gray-800">{fmt(p.revenue)}</td>
                <td className="py-2 text-right">
                  {p.revenue_goal_pct != null ? (
                    <span className={
                      p.revenue_goal_pct >= 100
                        ? "text-green-600 font-semibold"
                        : p.revenue_goal_pct >= 70
                        ? "text-yellow-600"
                        : "text-red-500"
                    }>
                      {p.revenue_goal_pct.toFixed(1)}%
                    </span>
                  ) : (
                    <span className="text-gray-300">—</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
