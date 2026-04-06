"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";

const TRENDING = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM"];

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState<
    { ticker: string; cik?: string; name?: string }[]
  >([]);
  const [loading, setLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>(undefined);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      try {
        const API_URL =
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
        const res = await fetch(
          `${API_URL}/search?q=${encodeURIComponent(query)}`
        );
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data.results || []);
          setShowSuggestions(true);
        }
      } catch {
        // Silently fail — suggestions are optional
      }
    }, 300);
  }, [query]);

  const handleSearch = (ticker?: string) => {
    const t = (ticker || query).trim().toUpperCase();
    if (!t) return;
    setLoading(true);
    router.push(`/company/${t}`);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-3.5rem)] px-4">
      {/* Hero */}
      <div className="text-center mb-10 animate-fade-in">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent">
          Business Evaluator
        </h1>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Comprehensive company analysis powered by SEC EDGAR. Built for
          investors, venture capitalists, private equity, and traders.
        </p>
      </div>

      {/* Search Bar */}
      <div className="relative w-full max-w-2xl mb-8">
        <div className="relative">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Search by ticker or company name... (e.g., AAPL, Tesla)"
            className="w-full h-14 pl-12 pr-32 bg-[#111128] border border-gray-700 rounded-xl text-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-600"
          />
          <button
            onClick={() => handleSearch()}
            disabled={loading}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? "Loading..." : "Evaluate"}
          </button>
        </div>

        {/* Suggestions Dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-[#111128] border border-gray-700 rounded-xl overflow-hidden z-50 shadow-xl">
            {suggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => handleSearch(s.ticker)}
                className="w-full px-4 py-3 text-left hover:bg-blue-600/20 flex items-center gap-3 border-b border-gray-800 last:border-0 transition-colors"
              >
                <span className="font-mono font-bold text-blue-400">
                  {s.ticker}
                </span>
                {s.name && (
                  <span className="text-gray-400 text-sm truncate">
                    {s.name}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Trending Tickers */}
      <div className="mb-12">
        <p className="text-gray-500 text-sm mb-3 text-center">
          Trending Tickers
        </p>
        <div className="flex flex-wrap gap-2 justify-center">
          {TRENDING.map((t) => (
            <button
              key={t}
              onClick={() => handleSearch(t)}
              className="px-4 py-2 bg-[#111128] border border-gray-700 rounded-lg font-mono text-sm hover:border-blue-500 hover:text-blue-400 transition-all"
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl w-full">
        {[
          {
            title: "SEC Filings",
            desc: "10-K, 10-Q, 8-K filings with XBRL financial data extraction",
            icon: "M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4",
          },
          {
            title: "DCF Valuation",
            desc: "10-year discounted cash flow model with intrinsic value",
            icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
          },
          {
            title: "Investment Score",
            desc: "0-100 score with bull/bear case analysis and peer comparison",
            icon: "M13 7h8m0 0v8m0-8l-8 8-4-4-6 6",
          },
          {
            title: "Risk Analysis",
            desc: "Debt analysis, burn rate, insider trading, and news sentiment",
            icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z",
          },
        ].map((f, i) => (
          <div
            key={i}
            className="p-4 bg-[#111128] border border-gray-800 rounded-xl"
          >
            <svg className="w-8 h-8 text-blue-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={f.icon} /></svg>
            <h3 className="font-semibold mb-1">{f.title}</h3>
            <p className="text-gray-500 text-sm">{f.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
