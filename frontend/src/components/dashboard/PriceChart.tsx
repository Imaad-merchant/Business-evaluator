"use client";

import { useState, useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { PricePoint } from "@/lib/types";

export default function PriceChart({
  history,
  ticker,
}: {
  history: PricePoint[] | null;
  ticker: string;
}) {
  const [period, setPeriod] = useState("1y");

  const chartData = useMemo(() => {
    if (!history) return [];
    return history
      .filter((p) => p.close != null)
      .map((p) => ({
        date: new Date(p.timestamp * 1000).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
        }),
        price: p.close,
        volume: p.volume,
      }));
  }, [history]);

  if (!chartData.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400 mb-4">Price Chart</h3>
        <p className="text-gray-500">Price data unavailable</p>
      </div>
    );
  }

  const isPositive =
    chartData.length >= 2 &&
    (chartData[chartData.length - 1].price ?? 0) >= (chartData[0].price ?? 0);

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400">
          {ticker} Price Chart
        </h3>
        <div className="flex gap-1">
          {["1m", "3m", "6m", "1y", "5y"].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-2 py-1 text-xs rounded ${
                period === p
                  ? "bg-blue-600 text-white"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor={isPositive ? "#10b981" : "#ef4444"}
                stopOpacity={0.3}
              />
              <stop
                offset="95%"
                stopColor={isPositive ? "#10b981" : "#ef4444"}
                stopOpacity={0}
              />
            </linearGradient>
          </defs>
          <XAxis
            dataKey="date"
            tick={{ fill: "#6b7280", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval="preserveStartEnd"
          />
          <YAxis
            tick={{ fill: "#6b7280", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            domain={["auto", "auto"]}
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip
            contentStyle={{
              background: "#1a1a2e",
              border: "1px solid #2a2a4a",
              borderRadius: "8px",
              color: "#e0e0e8",
            }}
            formatter={(value) => [`$${Number(value).toFixed(2)}`, "Price"]}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={isPositive ? "#10b981" : "#ef4444"}
            fill="url(#priceGradient)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
