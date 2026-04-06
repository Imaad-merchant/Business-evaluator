"use client";

import { formatCurrency, getScoreColor } from "@/lib/utils";
import type { CompanyInfo, StockData, InvestmentScore } from "@/lib/types";

export default function CompanyHeader({
  company,
  stock,
  score,
  ticker,
}: {
  company: CompanyInfo;
  stock: StockData;
  score: InvestmentScore;
  ticker: string;
}) {
  const priceChange =
    stock?.current_price && stock?.previous_close
      ? stock.current_price - stock.previous_close
      : null;
  const priceChangePercent =
    priceChange && stock?.previous_close
      ? (priceChange / stock.previous_close) * 100
      : null;

  const handleExportPDF = () => {
    const API_URL =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
    window.open(`${API_URL}/export/${ticker}/pdf`, "_blank");
  };

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div>
        <div className="flex items-center gap-3 mb-1">
          <h1 className="text-2xl font-bold">{company?.name || ticker}</h1>
          {score?.grade && (
            <span
              className={`px-2 py-0.5 rounded font-mono font-bold text-sm border ${getScoreColor(
                score.overall_score
              )} border-current/30`}
            >
              {score.grade}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-400">
          <span className="font-mono font-bold text-blue-400">{ticker}</span>
          {company?.exchange && <span>{company.exchange}</span>}
          {company?.sic_description && (
            <>
              <span className="text-gray-700">|</span>
              <span>{company.sic_description}</span>
            </>
          )}
        </div>
      </div>

      <div className="flex items-center gap-6">
        {stock?.current_price != null && (
          <div className="text-right">
            <div className="text-2xl font-mono font-bold">
              ${stock.current_price.toFixed(2)}
            </div>
            {priceChange != null && priceChangePercent != null && (
              <div
                className={`text-sm font-mono ${
                  priceChange >= 0 ? "text-emerald-400" : "text-red-400"
                }`}
              >
                {priceChange >= 0 ? "+" : ""}
                {priceChange.toFixed(2)} ({priceChangePercent >= 0 ? "+" : ""}
                {priceChangePercent.toFixed(2)}%)
              </div>
            )}
          </div>
        )}

        <button
          onClick={handleExportPDF}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          Export PDF
        </button>
      </div>
    </div>
  );
}
