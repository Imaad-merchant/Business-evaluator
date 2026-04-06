"use client";

import { getSentimentColor } from "@/lib/utils";
import type { NewsData } from "@/lib/types";

export default function NewsSection({ news }: { news?: NewsData }) {
  if (!news?.articles?.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">News</h3>
        <p className="text-gray-500 mt-2">No news articles found</p>
      </div>
    );
  }

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <h3 className="text-sm text-gray-400 mb-4">Recent News</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {news.articles.slice(0, 9).map((a, i) => (
          <a
            key={i}
            href={a.url}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-3 bg-[#0a0a1a] border border-gray-800 rounded-lg hover:border-blue-500/50 transition-colors"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <h4 className="text-sm text-gray-200 line-clamp-2 flex-1">
                {a.title}
              </h4>
              {a.sentiment && (
                <span
                  className={`text-xs shrink-0 ${getSentimentColor(
                    a.sentiment.label
                  )}`}
                >
                  {a.sentiment.label === "positive"
                    ? "+"
                    : a.sentiment.label === "negative"
                    ? "-"
                    : "~"}
                </span>
              )}
            </div>
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>{a.source}</span>
              {a.published_at && (
                <span>
                  {new Date(a.published_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                  })}
                </span>
              )}
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
