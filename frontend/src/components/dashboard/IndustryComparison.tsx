"use client";

import type { IndustryComparison as IndustryComparisonType } from "@/lib/types";

export default function IndustryComparison({
  comparison,
}: {
  comparison?: IndustryComparisonType;
}) {
  if (!comparison?.metrics?.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">Industry Comparison</h3>
        <p className="text-gray-500 mt-2">No industry data available</p>
      </div>
    );
  }

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400">
          vs {comparison.industry} Industry
        </h3>
        {comparison.summary && (
          <span
            className={`text-xs font-bold ${
              comparison.summary.overall === "ABOVE AVERAGE"
                ? "text-emerald-400"
                : comparison.summary.overall === "BELOW AVERAGE"
                ? "text-red-400"
                : "text-gray-400"
            }`}
          >
            {comparison.summary.overall}
          </span>
        )}
      </div>

      <div className="space-y-3">
        {comparison.metrics.map((m) => {
          const maxVal = Math.max(
            Math.abs(m.company_value),
            Math.abs(m.industry_median)
          );
          const companyWidth =
            maxVal > 0 ? (Math.abs(m.company_value) / maxVal) * 100 : 0;
          const industryWidth =
            maxVal > 0 ? (Math.abs(m.industry_median) / maxVal) * 100 : 0;

          return (
            <div key={m.name}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-gray-400">{m.name}</span>
                <div className="flex gap-4">
                  <span
                    className={`font-mono ${
                      m.status === "above" ? "text-emerald-400" : "text-gray-300"
                    }`}
                  >
                    {m.company_value}
                    {m.unit}
                  </span>
                  <span className="text-gray-600 font-mono">
                    {m.industry_median}
                    {m.unit}
                  </span>
                </div>
              </div>
              <div className="flex gap-1 h-2">
                <div className="flex-1 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      m.status === "above" ? "bg-emerald-400/60" : "bg-blue-400/60"
                    }`}
                    style={{ width: `${companyWidth}%` }}
                  />
                </div>
                <div className="flex-1 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gray-600/60"
                    style={{ width: `${industryWidth}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-4 mt-4 text-xs text-gray-500">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-blue-400/60" />
          Company
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-gray-600/60" />
          Industry Median
        </div>
      </div>
    </div>
  );
}
