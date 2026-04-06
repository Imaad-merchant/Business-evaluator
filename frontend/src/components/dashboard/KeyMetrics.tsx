"use client";

import { formatCurrency, formatPercent } from "@/lib/utils";
import type { StockData, FinancialStatement, FinancialRatios } from "@/lib/types";

function MetricCard({
  label,
  value,
  subValue,
}: {
  label: string;
  value: string;
  subValue?: string;
}) {
  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-4">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-lg font-mono font-bold">{value}</p>
      {subValue && <p className="text-xs text-gray-500 mt-1">{subValue}</p>}
    </div>
  );
}

export default function KeyMetrics({
  stock,
  statements,
  ratios,
}: {
  stock: StockData;
  statements?: FinancialStatement[];
  ratios?: FinancialRatios;
}) {
  const latest = statements?.[0];
  const prof = ratios?.profitability;
  const growth = ratios?.growth;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <MetricCard
        label="Market Cap"
        value={formatCurrency(stock?.market_cap)}
      />
      <MetricCard
        label="Revenue"
        value={formatCurrency(latest?.revenue)}
        subValue={
          growth?.revenue_growth != null
            ? `${formatPercent(growth.revenue_growth)} YoY`
            : undefined
        }
      />
      <MetricCard
        label="Net Income"
        value={formatCurrency(latest?.net_income)}
      />
      <MetricCard
        label="P/E Ratio"
        value={stock?.pe_ratio != null ? stock.pe_ratio.toFixed(1) : "N/A"}
        subValue={
          stock?.forward_pe != null
            ? `Fwd: ${stock.forward_pe.toFixed(1)}`
            : undefined
        }
      />
      <MetricCard
        label="EV/EBITDA"
        value={stock?.ev_to_ebitda != null ? stock.ev_to_ebitda.toFixed(1) : "N/A"}
      />
      <MetricCard
        label="Net Margin"
        value={prof?.net_margin != null ? `${prof.net_margin}%` : "N/A"}
      />
      <MetricCard
        label="Revenue Growth"
        value={growth?.revenue_growth != null ? formatPercent(growth.revenue_growth) : "N/A"}
      />
      <MetricCard
        label="Free Cash Flow"
        value={formatCurrency(latest?.free_cash_flow)}
      />
    </div>
  );
}
