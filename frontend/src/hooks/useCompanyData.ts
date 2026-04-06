"use client";

import { useState, useEffect } from "react";
import type { CompanyEvaluation } from "@/lib/types";

export function useCompanyData(ticker: string) {
  const [data, setData] = useState<CompanyEvaluation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const API_URL =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

    async function fetchData() {
      setLoading(true);
      setError(null);

      try {
        const res = await fetch(`${API_URL}/company/${ticker}`);
        if (!res.ok) {
          throw new Error(`Failed to fetch: ${res.status}`);
        }
        const json = await res.json();
        if (json.error) {
          setError(json.error);
        } else {
          setData(json);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch data");
      } finally {
        setLoading(false);
      }
    }

    if (ticker) fetchData();
  }, [ticker]);

  return { data, loading, error };
}
