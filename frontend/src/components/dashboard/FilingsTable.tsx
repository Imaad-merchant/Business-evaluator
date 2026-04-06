"use client";

import type { Filing } from "@/lib/types";

const FORM_COLORS: Record<string, string> = {
  "10-K": "bg-blue-500/20 text-blue-400",
  "10-Q": "bg-purple-500/20 text-purple-400",
  "8-K": "bg-yellow-500/20 text-yellow-400",
  "4": "bg-emerald-500/20 text-emerald-400",
};

export default function FilingsTable({
  filings,
  ticker,
}: {
  filings?: Filing[];
  ticker: string;
}) {
  if (!filings?.length) {
    return (
      <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
        <h3 className="text-sm text-gray-400">SEC Filings</h3>
        <p className="text-gray-500 mt-2">No filings found</p>
      </div>
    );
  }

  return (
    <div className="bg-[#111128] border border-gray-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm text-gray-400">SEC Filings</h3>
        <a
          href={`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company=${ticker}&CIK=&type=&dateb=&owner=include&count=40&search_text=&action=getcompany`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-blue-400 hover:text-blue-300"
        >
          View all on SEC.gov
        </a>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-800">
              <th className="text-left py-2 text-gray-500 font-normal">
                Form
              </th>
              <th className="text-left py-2 text-gray-500 font-normal">
                Description
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Filed
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Report Date
              </th>
              <th className="text-right py-2 text-gray-500 font-normal">
                Link
              </th>
            </tr>
          </thead>
          <tbody>
            {filings.slice(0, 20).map((f, i) => (
              <tr
                key={i}
                className="border-b border-gray-800/50 hover:bg-gray-800/30"
              >
                <td className="py-2">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-bold ${
                      FORM_COLORS[f.form_type] || "bg-gray-600/20 text-gray-400"
                    }`}
                  >
                    {f.form_type}
                  </span>
                </td>
                <td className="py-2 text-gray-300 text-xs max-w-[300px] truncate">
                  {f.description || f.form_type}
                </td>
                <td className="text-right py-2 text-gray-500 text-xs">
                  {f.filed_date}
                </td>
                <td className="text-right py-2 text-gray-500 text-xs">
                  {f.reporting_date || "—"}
                </td>
                <td className="text-right py-2">
                  {f.document_url && (
                    <a
                      href={f.document_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      View
                    </a>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
