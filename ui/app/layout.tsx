import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'DocuMind | Intelligent Document Processing & RAG',
  description: 'AI-powered document intelligence with hybrid RAG retrieval, DSPy reasoning, and smart PDF processing',
  icons: {
    icon: '/favicon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}
