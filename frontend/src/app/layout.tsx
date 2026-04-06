import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Business Evaluator | Investment Analysis Platform",
  description:
    "Comprehensive company evaluation for investors, VCs, PE firms, and traders. SEC filings, financial analysis, valuation models, and more.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-[#0a0a1a] text-gray-100">
        <nav className="border-b border-gray-800 bg-[#0a0a1a]/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between">
            <a href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-sm">
                BE
              </div>
              <span className="font-semibold text-lg">Business Evaluator</span>
            </a>
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <a href="/" className="hover:text-white transition-colors">
                Search
              </a>
              <span className="text-gray-700">|</span>
              <span>SEC EDGAR + AI Analysis</span>
            </div>
          </div>
        </nav>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
