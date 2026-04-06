"use client";

import { getScoreColor, getScoreBgColor } from "@/lib/utils";
import type { InvestmentScore } from "@/lib/types";

export default function ScoreCard({ score }: { score: InvestmentScore }) {
  if (!score?.overall_score) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <p className="text-gray-500">Score unavailable</p>
      </div>
    );
  }

  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score.overall_score / 100) * circumference;

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm text-gray-400 mb-4">Investment Score</h3>

      {/* Circular Score */}
      <div className="flex justify-center mb-4">
        <div className="relative w-32 h-32">
          <svg className="w-32 h-32 -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#1e1e3a"
              strokeWidth="8"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              className={getScoreColor(score.overall_score)}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span
              className={`text-3xl font-bold font-mono ${getScoreColor(
                score.overall_score
              )}`}
            >
              {score.overall_score}
            </span>
            <span
              className={`text-lg font-bold ${getScoreColor(
                score.overall_score
              )}`}
            >
              {score.grade}
            </span>
          </div>
        </div>
      </div>

      {/* Component Breakdown */}
      <div className="space-y-2">
        {score.components &&
          Object.entries(score.components).map(([key, val]) => (
            <div key={key} className="flex items-center justify-between text-xs">
              <span className="text-gray-400 capitalize">
                {key.replace("_", " ")}
              </span>
              <div className="flex items-center gap-2">
                <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      val.score >= 70
                        ? "bg-emerald-400"
                        : val.score >= 40
                        ? "bg-yellow-400"
                        : "bg-red-400"
                    }`}
                    style={{ width: `${val.score}%` }}
                  />
                </div>
                <span className="font-mono w-6 text-right">{val.score}</span>
              </div>
            </div>
          ))}
      </div>

      {/* Bull/Bear */}
      {(score.bull_case?.length > 0 || score.bear_case?.length > 0) && (
        <div className="mt-4 pt-4 border-t border-gray-800 space-y-3">
          {score.bull_case?.length > 0 && (
            <div>
              <p className="text-xs text-emerald-400 font-semibold mb-1">
                Bull Case
              </p>
              {score.bull_case.map((p, i) => (
                <p key={i} className="text-xs text-gray-400 pl-2">
                  + {p}
                </p>
              ))}
            </div>
          )}
          {score.bear_case?.length > 0 && (
            <div>
              <p className="text-xs text-red-400 font-semibold mb-1">
                Bear Case
              </p>
              {score.bear_case.map((p, i) => (
                <p key={i} className="text-xs text-gray-400 pl-2">
                  - {p}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
