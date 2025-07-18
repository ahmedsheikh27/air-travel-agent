import type React from "react"
import type { Metadata } from "next"
import { Inter, Orbitron } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const orbitron = Orbitron({ subsets: ["latin"], variable: "--font-orbitron" })

export const metadata: Metadata = {
  title: "AI Airline Assistant",
  description: "Your futuristic AI-powered airline assistant.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${orbitron.variable} font-sans text-white min-h-screen antialiased`}
        style={{ background: "radial-gradient(circle at 0% 50%, #3b82f6 0%, #0f172a 100%)" }}
      >
        {children}
      </body>
    </html>
  )
}
