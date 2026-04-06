"use client";

import { useParams } from "next/navigation";
import { useCompanyData } from "@/hooks/useCompanyData";
import CompanyHeader from "@/components/dashboard/CompanyHeader";
import ScoreCard from "@/components/dashboard/ScoreCard";
import KeyMetrics from "@/components/dashboard/KeyMetrics";
import PriceChart from "@/components/dashboard/PriceChart";
import FinancialTabs from "@/components/dashboard/FinancialTabs";
import ValuationCard from "@/components/dashboard/ValuationCard";
import CompsTable from "@/components/dashboard/CompsTable";
import DebtAnalysis from "@/components/dashboard/DebtAnalysis";
import BurnRateCard from "@/components/dashboard/BurnRateCard";
import InsiderTrading from "@/components/dashboard/InsiderTrading";
import SentimentGauge from "@/components/dashboard/SentimentGauge";
import IndustryComparison from "@/components/dashboard/IndustryComparison";
import NewsSection from "@/components/dashboard/NewsSection";
import FilingsTable from "@/components/dashboard/FilingsTable";

export default function CompanyPage() {
  const params = useParams();
  const ticker = (params.ticker as string)?.toUpperCase();
  const { data, loading, error } = useCompanyData(ticker);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="animate-pulse space-y-6">
          <div className="h-20 bg-[#111128] rounded-xl" />
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-24 bg-[#111128] rounded-xl" />
            ))}
          </div>
          <div className="h-64 bg-[#111128] rounded-xl" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="h-48 bg-[#111128] rounded-xl" />
            <div className="h-48 bg-[#111128] rounded-xl" />
          </div>
        </div>
        <p className="text-center text-gray-500 mt-8">
          Fetching data from SEC EDGAR, analyzing financials...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-8 max-w-md mx-auto">
          <h2 className="text-xl font-bold text-red-400 mb-2">Error</h2>
          <p className="text-gray-400">{error}</p>
          <a
            href="/"
            className="inline-block mt-4 px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Search
          </a>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const showBurnRate =
    data.burn_rate?.is_burning_cash ||
    (data.financials?.statements?.[0]?.net_income ?? 0) < 0;

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <CompanyHeader company={data.company} stock={data.stock} score={data.score} ticker={ticker} />

      {/* Score + Key Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <ScoreCard score={data.score} />
        <div className="lg:col-span-3">
          <KeyMetrics
            stock={data.stock}
            statements={data.financials?.statements}
            ratios={data.financials?.ratios}
          />
        </div>
      </div>

      {/* Price Chart + Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <PriceChart history={data.price_history} ticker={ticker} />
        </div>
        <SentimentGauge news={data.news} />
      </div>

      {/* Financial Statements */}
      <FinancialTabs statements={data.financials?.statements} />

      {/* Valuation Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <ValuationCard dcf={data.valuation?.dcf} stock={data.stock} />
        <CompsTable comps={data.valuation?.comps} />
      </div>

      {/* Debt + Burn Rate */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <DebtAnalysis debt={data.debt_analysis} />
        {showBurnRate && <BurnRateCard burnRate={data.burn_rate} />}
        {!showBurnRate && <IndustryComparison comparison={data.industry_comparison} />}
      </div>

      {/* Insider Trading */}
      <InsiderTrading insider={data.insider_trading} />

      {/* Industry Comparison (if not shown above) */}
      {showBurnRate && <IndustryComparison comparison={data.industry_comparison} />}

      {/* News */}
      <NewsSection news={data.news} />

      {/* SEC Filings */}
      <FilingsTable filings={data.filings} ticker={ticker} />
    </div>
  );
}
