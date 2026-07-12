import type { Metadata } from "next";
import { Geist, Inter, JetBrains_Mono } from "next/font/google";
import { Toaster } from "@/components/ui/sonner";
import { AppProviders } from "@/components/layout/app-providers";
import "./globals.css";

const geistHeading = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Scout AI: Football Intelligence for Every Team",
  description:
    "Professional AI-powered football analysis from a single smartphone video. Player tracking, heatmaps, tactical reports, built for every club, not just billion-dollar ones.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark scroll-smooth ${geistHeading.variable} ${inter.variable} ${jetbrainsMono.variable} h-full antialiased`}
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col bg-background text-foreground font-sans">
        <AppProviders>
          {children}
          <Toaster />
        </AppProviders>
      </body>
    </html>
  );
}
