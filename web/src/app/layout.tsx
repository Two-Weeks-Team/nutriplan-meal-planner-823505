import type { Metadata } from "next";
import { DM_Sans, Fraunces } from "next/font/google";
import "@/app/globals.css";

const bodyFont = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "700"]
});

const displayFont = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["600", "700"]
});

export const metadata: Metadata = {
  title: "Nutriplan Meal Planner",
  description: "AI meal planning folio with instant macros, live swaps, and grocery roll-up"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${bodyFont.variable} ${displayFont.variable} bg-background text-foreground font-[--font-body]`}>
        {children}
      </body>
    </html>
  );
}
