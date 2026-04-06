"use client";

import { formatCurrency } from "@/lib/utils";
import type { CompsResult } from "@/lib/types";

export default function CompsTable({ comps }: { comps?: CompsResult }) {
  if (!comps || comps.error || !comps.peers?.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400 mb-2">Comparable Companies</h3>
        <p className="text-gray-500">
          {comps?.error || "No comparable companies found"}
        </p>
      </div>
    );
  }

  const premium = comps.premium_discount_percent;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm text-gray-400 mb-4">Comparable Companies</h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left py-2 text-gray-500 font-normal">
                Ticker
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Mkt Cap
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                P/E
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                EV/Rev
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                EV/EBITDA
              </th>
            </tr>
          </thead>
          <tbody>
            {comps.peers.map((p) => (
              <tr
                key={p.ticker}
                className="border-b border-gray-800/50 hover:bg-gray-800/30"
              >
                <td className="py-2 font-mono text-blue-400 font-bold">
                  {p.ticker}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {formatCurrency(p.market_cap)}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {p.pe_ratio?.toFixed(1) ?? "—"}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {p.ev_to_revenue?.toFixed(1) ?? "—"}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {p.ev_to_ebitda?.toFixed(1) ?? "—"}
                </td>
              </tr>
            ))}
            {/* Median Row */}
            {comps.median_multiples && (
              <tr className="border-t-2 border-gray-700 font-bold">
                <td className="py-2 text-gray-300">Median</td>
                <td className="text-right py-2">—</td>
                <td className="text-right py-2 font-mono text-xs">
                  {comps.median_multiples.pe_ratio?.toFixed(1) ?? "—"}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {comps.median_multiples.ev_to_revenue?.toFixed(1) ?? "—"}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {comps.median_multiples.ev_to_ebitda?.toFixed(1) ?? "—"}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Implied Value */}
      {comps.average_implied_value && (
        <div className="mt-3 pt-3 border-t border-gray-800 flex items-center justify-between">
          <span className="text-xs text-gray-500">
            Implied Value (Avg of Multiples)
          </span>
          <span className="font-mono font-bold text-blue-400">
            ${comps.average_implied_value.toFixed(2)}
          </span>
        </div>
      )}
      {premium != null && (
        <div
          className={`text-center text-xs font-bold mt-2 ${
            premium > 10
              ? "text-red-400"
              : premium < -10
              ? "text-emerald-400"
              : "text-gray-400"
          }`}
        >
          {comps.verdict}
        </div>
      )}
    </div>
  );
}
