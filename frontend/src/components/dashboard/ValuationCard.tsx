"use client";

import type { DCFResult, StockData } from "@/lib/types";

export default function ValuationCard({
  dcf,
  stock,
}: {
  dcf?: DCFResult;
  stock?: StockData;
}) {
  if (!dcf || dcf.error) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400 mb-2">DCF Valuation</h3>
        <p className="text-gray-500">{dcf?.error || "Valuation unavailable"}</p>
      </div>
    );
  }

  const upside = dcf.upside_percent ?? 0;
  const isUndervalued = upside > 0;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm text-gray-400 mb-4">DCF Valuation</h3>

      <div className="flex items-center gap-6 mb-4">
        <div>
          <p className="text-xs text-gray-500">Intrinsic Value</p>
          <p className="text-2xl font-mono font-bold text-blue-400">
            ${dcf.intrinsic_value_per_share?.toFixed(2)}
          </p>
        </div>
        <div className="text-2xl text-gray-600">vs</div>
        <div>
          <p className="text-xs text-gray-500">Current Price</p>
          <p className="text-2xl font-mono font-bold">
            ${stock?.current_price?.toFixed(2) ?? "N/A"}
          </p>
        </div>
      </div>

      {/* Upside/Downside Bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Downside</span>
          <span
            className={`font-mono font-bold ${
              isUndervalued ? "text-emerald-400" : "text-red-400"
            }`}
          >
            {upside >= 0 ? "+" : ""}
            {upside.toFixed(1)}%
          </span>
          <span>Upside</span>
        </div>
        <div className="h-3 bg-gray-800 rounded-full overflow-hidden relative">
          <div
            className={`absolute top-0 h-full rounded-full ${
              isUndervalued ? "bg-emerald-400" : "bg-red-400"
            }`}
            style={{
              left: isUndervalued ? "50%" : `${50 + upside / 2}%`,
              width: `${Math.min(Math.abs(upside) / 2, 50)}%`,
            }}
          />
          <div className="absolute top-0 left-1/2 w-px h-full bg-gray-600" />
        </div>
      </div>

      <div
        className={`text-center text-sm font-bold ${
          isUndervalued ? "text-emerald-400" : "text-red-400"
        }`}
      >
        {dcf.verdict}
      </div>

      {/* Assumptions */}
      {dcf.assumptions && (
        <div className="mt-4 pt-3 border-t border-gray-800 grid grid-cols-2 gap-2 text-xs">
          <div>
            <span className="text-gray-500">Growth Rate: </span>
            <span className="font-mono">
              {dcf.assumptions.initial_growth_rate}%
            </span>
          </div>
          <div>
            <span className="text-gray-500">WACC: </span>
            <span className="font-mono">
              {dcf.assumptions.discount_rate_wacc}%
            </span>
          </div>
          <div>
            <span className="text-gray-500">Terminal Growth: </span>
            <span className="font-mono">
              {dcf.assumptions.terminal_growth_rate}%
            </span>
          </div>
          <div>
            <span className="text-gray-500">Latest FCF: </span>
            <span className="font-mono">
              ${((dcf.assumptions.latest_fcf || 0) / 1e9).toFixed(1)}B
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
