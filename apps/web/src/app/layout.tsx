import type { Metadata } from "next";

import "./globals.css";

export const metadata: Metadata = {
  title: "AI Career Concierge",
  description: "Single-user PoC dashboard for curated AI job matching.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
