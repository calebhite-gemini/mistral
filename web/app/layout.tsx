import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MarketEdge Terminal",
  description: "Sports prediction market trading terminal",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
