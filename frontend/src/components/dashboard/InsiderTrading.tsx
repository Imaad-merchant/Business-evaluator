"use client";

import { formatCurrency } from "@/lib/utils";
import type { InsiderData } from "@/lib/types";

export default function InsiderTrading({
  insider,
}: {
  insider?: InsiderData;
}) {
  if (!insider?.trades?.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">Insider Trading</h3>
        <p className="text-gray-500 mt-2">No insider trading data available</p>
      </div>
    );
  }

  const clusterDetected = insider.cluster_buys?.detected;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400">Insider Trading Activity</h3>
        {clusterDetected && (
          <span className="px-2 py-1 bg-emerald-400/20 border border-emerald-400/50 rounded text-xs font-bold text-emerald-400 animate-pulse">
            CLUSTER BUY DETECTED
          </span>
        )}
      </div>

      {/* Cluster Buy Alert */}
      {clusterDetected && insider.cluster_buys.clusters?.length > 0 && (
        <div className="mb-4 p-3 bg-emerald-400/10 border border-emerald-400/30 rounded-lg">
          <p className="text-sm text-emerald-400 font-bold mb-1">
            Strong Buy Signal
          </p>
          {insider.cluster_buys.clusters.map((c, i) => (
            <p key={i} className="text-xs text-gray-400">
              {c.insider_count} insiders purchased{" "}
              {formatCurrency(c.total_value)} worth of shares
            </p>
          ))}
        </div>
      )}

      {/* Trades Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left py-2 text-gray-500 font-normal">
                Insider
              </th>
              <th className="text-left py-2 text-gray-500 font-normal">
                Title
              </th>
              <th className="text-left py-2 text-gray-500 font-normal">
                Type
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Shares
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Price
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Value
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Date
              </th>
            </tr>
          </thead>
          <tbody>
            {insider.trades.slice(0, 15).map((t, i) => (
              <tr
                key={i}
                className="border-b border-gray-800/50 hover:bg-gray-800/30"
              >
                <td className="py-2 text-gray-300 max-w-[150px] truncate">
                  {t.insider_name}
                </td>
                <td className="py-2 text-gray-500 text-xs max-w-[120px] truncate">
                  {t.insider_title}
                </td>
                <td className="py-2">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-bold ${
                      t.transaction_type === "Purchase"
                        ? "bg-emerald-400/20 text-emerald-400"
                        : t.transaction_type === "Sale"
                        ? "bg-red-400/20 text-red-400"
                        : "bg-gray-600/20 text-gray-400"
                    }`}
                  >
                    {t.transaction_type}
                  </span>
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {t.shares?.toLocaleString()}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  ${t.price_per_share?.toFixed(2)}
                </td>
                <td className="text-right py-2 font-mono text-xs">
                  {formatCurrency(t.total_value)}
                </td>
                <td className="text-right py-2 text-gray-500 text-xs">
                  {t.transaction_date}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {insider.total_trades > 15 && (
        <p className="text-xs text-gray-500 mt-2 text-center">
          Showing 15 of {insider.total_trades} trades
        </p>
      )}
    </div>
  );
}
