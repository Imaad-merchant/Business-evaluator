"use client";

import { getSentimentColor } from "@/lib/utils";
import type { NewsData } from "@/lib/types";

export default function SentimentGauge({ news }: { news?: NewsData }) {
  if (!news?.sentiment) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">News Sentiment</h3>
        <p className="text-gray-500 mt-2">No sentiment data</p>
      </div>
    );
  }

  const { overall_score, overall_label, positive_count, negative_count, neutral_count } =
    news.sentiment;

  // Score ranges from -1 to 1, map to 0-180 degrees for semicircle
  const angle = ((overall_score + 1) / 2) * 180;
  const total = positive_count + negative_count + neutral_count;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm text-gray-400 mb-4">News Sentiment</h3>

      {/* Semicircle Gauge */}
      <div className="flex justify-center mb-4">
        <div className="relative w-40 h-20 overflow-hidden">
          <svg viewBox="0 0 200 100" className="w-full h-full">
            {/* Background arc */}
            <path
              d="M 10 100 A 90 90 0 0 1 190 100"
              fill="none"
              stroke="#1e1e3a"
              strokeWidth="12"
              strokeLinecap="round"
            />
            {/* Gradient arc: red to yellow to green */}
            <defs>
              <linearGradient id="sentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#ef4444" />
                <stop offset="50%" stopColor="#eab308" />
                <stop offset="100%" stopColor="#10b981" />
              </linearGradient>
            </defs>
            <path
              d="M 10 100 A 90 90 0 0 1 190 100"
              fill="none"
              stroke="url(#sentGrad)"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray={`${(angle / 180) * 283} 283`}
            />
            {/* Needle */}
            <line
              x1="100"
              y1="100"
              x2={100 + 70 * Math.cos(((180 - angle) * Math.PI) / 180)}
              y2={100 - 70 * Math.sin(((180 - angle) * Math.PI) / 180)}
              stroke="#e0e0e8"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="4" fill="#e0e0e8" />
          </svg>
        </div>
      </div>

      <div className="text-center mb-4">
        <span
          className={`text-lg font-bold ${getSentimentColor(overall_label)}`}
        >
          {overall_label.toUpperCase()}
        </span>
        <p className="text-xs text-gray-500 font-mono">
          Score: {overall_score.toFixed(3)}
        </p>
      </div>

      {/* Breakdown */}
      <div className="flex justify-between text-xs">
        <div className="text-center">
          <p className="text-emerald-400 font-bold">{positive_count}</p>
          <p className="text-gray-500">Positive</p>
        </div>
        <div className="text-center">
          <p className="text-gray-400 font-bold">{neutral_count}</p>
          <p className="text-gray-500">Neutral</p>
        </div>
        <div className="text-center">
          <p className="text-red-400 font-bold">{negative_count}</p>
          <p className="text-gray-500">Negative</p>
        </div>
      </div>

      {/* Sentiment bar */}
      {total > 0 && (
        <div className="flex h-2 rounded-full overflow-hidden mt-3">
          <div
            className="bg-emerald-400"
            style={{ width: `${(positive_count / total) * 100}%` }}
          />
          <div
            className="bg-gray-500"
            style={{ width: `${(neutral_count / total) * 100}%` }}
          />
          <div
            className="bg-red-400"
            style={{ width: `${(negative_count / total) * 100}%` }}
          />
        </div>
      )}

      {/* Latest headline */}
      {news.articles?.[0] && (
        <div className="mt-3 pt-3 border-t border-gray-800">
          <p className="text-xs text-gray-500">Latest</p>
          <a
            href={news.articles[0].url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-300 hover:text-blue-400 line-clamp-2"
          >
            {news.articles[0].title}
          </a>
        </div>
      )}
    </div>
  );
}
