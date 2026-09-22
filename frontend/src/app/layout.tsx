import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agni-Netra | Spaceborne Thermal Event Intelligence",
  description: "The satellite sees heat. Agni-Netra understands the event. Operational AI decision support for thermal anomalies across India.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" />
      </head>
      <body className="h-screen bg-[#F4F6F9] text-slate-800 flex flex-col antialiased">
        {children}
      </body>
    </html>
  );
}
