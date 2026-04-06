"use client";

import { formatCurrency } from "@/lib/utils";
import type { BurnRate } from "@/lib/types";

export default function BurnRateCard({
  burnRate,
}: {
  burnRate?: BurnRate;
}) {
  if (!burnRate) {
    return null;
  }

  if (!burnRate.is_burning_cash) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400 mb-2">Burn Rate</h3>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-emerald-400" />
          <span className="text-emerald-400 font-bold">PROFITABLE</span>
        </div>
        <p className="text-gray-500 text-sm mt-2">{burnRate.note}</p>
      </div>
    );
  }

  const healthColor =
    burnRate.health === "CRITICAL"
      ? "text-red-400"
      : burnRate.health === "WARNING"
      ? "text-orange-400"
      : burnRate.health === "ADEQUATE"
      ? "text-yellow-400"
      : "text-emerald-400";

  const runwayPercent = burnRate.runway_months
    ? Math.min((burnRate.runway_months / 36) * 100, 100)
    : 0;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400">Burn Rate & Runway</h3>
        <span className={`text-xs font-bold ${healthColor}`}>
          {burnRate.health}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500">Monthly Burn</p>
          <p className="font-mono font-bold text-red-400">
            {formatCurrency(burnRate.monthly_burn_rate)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Cash on Hand</p>
          <p className="font-mono font-bold">
            {formatCurrency(burnRate.total_cash)}
          </p>
        </div>
      </div>

      {/* Runway Bar */}
      {burnRate.runway_months != null && (
        <div className="mb-3">
          <div className="flex justify-between text-xs text-gray-500 mb-1">
            <span>Runway</span>
            <span className={`font-mono font-bold ${healthColor}`}>
              {burnRate.runway_months.toFixed(0)} months
            </span>
          </div>
          <div className="h-3 bg-gray-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${
                burnRate.health === "CRITICAL"
                  ? "bg-red-400"
                  : burnRate.health === "WARNING"
                  ? "bg-orange-400"
                  : "bg-emerald-400"
              }`}
              style={{ width: `${runwayPercent}%` }}
            />
          </div>
        </div>
      )}

      <p className="text-xs text-gray-500 mt-2">{burnRate.note}</p>
    </div>
  );
}
