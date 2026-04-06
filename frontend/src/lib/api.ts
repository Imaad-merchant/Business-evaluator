const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function fetchAPI(endpoint: string) {
  const res = await fetch(`${API_URL}${endpoint}`, {
    next: { revalidate: 300 }, // Cache for 5 minutes
  });

  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json();
}

export async function getCompanyEvaluation(ticker: string) {
  return fetchAPI(`/company/${ticker}`);
}

export async function searchCompanies(query: string) {
  return fetchAPI(`/search?q=${encodeURIComponent(query)}`);
}

export async function getFilings(ticker: string) {
  return fetchAPI(`/filings/${ticker}`);
}

export async function getFinancials(ticker: string) {
  return fetchAPI(`/financials/${ticker}`);
}

export async function getValuation(ticker: string) {
  return fetchAPI(`/valuation/${ticker}`);
}

export async function getNews(ticker: string) {
  return fetchAPI(`/news/${ticker}`);
}

export async function getInsiders(ticker: string) {
  return fetchAPI(`/insiders/${ticker}`);
}

export async function getIndustryBenchmark(sicCode: string) {
  return fetchAPI(`/industry/${sicCode}`);
}

export function getExportPdfUrl(ticker: string) {
  return `${API_URL}/export/${ticker}/pdf`;
}
