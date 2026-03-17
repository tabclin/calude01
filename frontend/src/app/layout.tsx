import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClinicAnalytics",
  description: "Sistema de análise gerencial para clínicas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className="antialiased">{children}</body>
    </html>
  );
}
