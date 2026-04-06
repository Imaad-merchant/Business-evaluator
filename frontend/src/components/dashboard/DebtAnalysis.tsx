"use client";

import { formatCurrency } from "@/lib/utils";
import type { DebtAnalysis as DebtAnalysisType } from "@/lib/types";

export default function DebtAnalysis({
  debt,
}: {
  debt?: DebtAnalysisType;
}) {
  if (!debt || !debt.ratios) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">Debt Analysis</h3>
        <p className="text-gray-500 mt-2">No debt data available</p>
      </div>
    );
  }

  const riskColor =
    debt.risk_level === "LOW"
      ? "text-emerald-400"
      : debt.risk_level === "MODERATE"
      ? "text-yellow-400"
      : debt.risk_level === "HIGH"
      ? "text-orange-400"
      : "text-red-400";

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400">Debt Analysis</h3>
        <span className={`text-xs font-bold ${riskColor}`}>
          {debt.risk_level} RISK
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500">Total Debt</p>
          <p className="font-mono font-bold">
            {formatCurrency(debt.total_debt)}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500">Net Debt</p>
          <p
            className={`font-mono font-bold ${
              debt.net_debt < 0 ? "text-emerald-400" : ""
            }`}
          >
            {formatCurrency(debt.net_debt)}
          </p>
        </div>
      </div>

      {/* Ratios */}
      <div className="space-y-2">
        {[
          ["D/E Ratio", debt.ratios.debt_to_equity, 2, "x"],
          ["Debt/Assets", debt.ratios.debt_to_assets, 0.5, "x"],
          ["Interest Coverage", debt.ratios.interest_coverage, 5, "x"],
          ["Net Debt/EBITDA", debt.ratios.net_debt_to_ebitda, 3, "x"],
        ].map(([label, value, threshold, unit]) => {
          if (value == null) return null;
          const numVal = value as number;
          const numThreshold = threshold as number;
          const isHealthy =
            label === "Interest Coverage"
              ? numVal > numThreshold
              : numVal < numThreshold;

          return (
            <div key={label as string} className="flex items-center justify-between text-sm">
              <span className="text-gray-400">{label as string}</span>
              <span
                className={`font-mono ${
                  isHealthy ? "text-emerald-400" : "text-orange-400"
                }`}
              >
                {numVal.toFixed(2)}
                {unit}
              </span>
            </div>
          );
        })}
      </div>

      {/* Risk Factors */}
      {debt.risk_factors?.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-800">
          {debt.risk_factors.map((f, i) => (
            <p key={i} className="text-xs text-gray-500 mt-1">
              {f}
            </p>
          ))}
        </div>
      )}
    </div>
  );
}
