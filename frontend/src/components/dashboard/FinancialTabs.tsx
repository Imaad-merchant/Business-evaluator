"use client";

import { useState } from "react";
import { formatCurrency } from "@/lib/utils";
import type { FinancialStatement } from "@/lib/types";

type Tab = "income" | "balance" | "cashflow";

const INCOME_ROWS: [string, keyof FinancialStatement][] = [
  ["Revenue", "revenue"],
  ["Cost of Revenue", "cost_of_revenue"],
  ["Gross Profit", "gross_profit"],
  ["Operating Expenses", "operating_expenses"],
  ["Operating Income", "operating_income"],
  ["Interest Expense", "interest_expense"],
  ["Income Tax", "income_tax"],
  ["Net Income", "net_income"],
  ["EBITDA", "ebitda"],
  ["EPS (Diluted)", "eps_diluted"],
];

const BALANCE_ROWS: [string, keyof FinancialStatement][] = [
  ["Cash & Equivalents", "cash_and_equivalents"],
  ["Total Current Assets", "total_current_assets"],
  ["Total Assets", "total_assets"],
  ["Total Current Liabilities", "total_current_liabilities"],
  ["Long-Term Debt", "long_term_debt"],
  ["Total Liabilities", "total_liabilities"],
  ["Stockholders' Equity", "stockholders_equity"],
];

const CASHFLOW_ROWS: [string, keyof FinancialStatement][] = [
  ["Operating Cash Flow", "operating_cash_flow"],
  ["Capital Expenditures", "capital_expenditures"],
  ["Free Cash Flow", "free_cash_flow"],
  ["D&A", "depreciation_amortization"],
];

export default function FinancialTabs({
  statements,
}: {
  statements?: FinancialStatement[];
}) {
  const [tab, setTab] = useState<Tab>("income");

  if (!statements?.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">Financial Statements</h3>
        <p className="text-gray-500 mt-2">No financial data available</p>
      </div>
    );
  }

  const rows =
    tab === "income"
      ? INCOME_ROWS
      : tab === "balance"
      ? BALANCE_ROWS
      : CASHFLOW_ROWS;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center gap-4 mb-4">
        <h3 className="text-sm text-gray-400">Financial Statements</h3>
        <div className="flex gap-1">
          {(
            [
              ["income", "Income Statement"],
              ["balance", "Balance Sheet"],
              ["cashflow", "Cash Flow"],
            ] as const
          ).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setTab(key)}
              className={`px-3 py-1 text-xs rounded-lg ${
                tab === key
                  ? "bg-blue-600 text-white"
                  : "text-gray-500 hover:text-gray-300 hover:bg-gray-800"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left py-2 text-gray-500 font-normal">
                Metric
              </th>
              {statements.map((s) => (
                <th
                  key={s.fiscal_year}
                  className="text-right py-2 text-gray-500 font-normal px-3"
                >
                  FY{s.fiscal_year}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map(([label, key]) => (
              <tr
                key={key}
                className="border-b border-gray-800/50 hover:bg-gray-800/30"
              >
                <td className="py-2 text-gray-300">{label}</td>
                {statements.map((s) => {
                  const val = s[key] as number | null;
                  return (
                    <td
                      key={s.fiscal_year}
                      className={`text-right py-2 font-mono text-xs px-3 ${
                        val != null && val < 0 ? "text-red-400" : "text-gray-200"
                      }`}
                    >
                      {key === "eps_diluted" || key === "eps_basic"
                        ? val != null
                          ? `$${(val as number).toFixed(2)}`
                          : "—"
                        : val != null
                        ? formatCurrency(val as number)
                        : "—"}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
