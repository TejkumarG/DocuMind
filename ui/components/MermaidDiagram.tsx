'use client'

import { useEffect, useRef } from 'react'
import mermaid from 'mermaid'

interface MermaidDiagramProps {
  chart: string
  id?: string
}

export default function MermaidDiagram({ chart, id = 'mermaid-diagram' }: MermaidDiagramProps) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'base',
      themeVariables: {
        primaryColor: '#3b82f6',
        primaryTextColor: '#1e293b',
        primaryBorderColor: '#2563eb',
        lineColor: '#64748b',
        secondaryColor: '#a78bfa',
        tertiaryColor: '#f472b6',
        background: '#ffffff',
        mainBkg: '#f8fafc',
        secondBkg: '#e0e7ff',
        tertiaryBkg: '#fce7f3',
        fontSize: '15px',
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      },
      flowchart: {
        curve: 'basis',
        padding: 20,
        nodeSpacing: 50,
        rankSpacing: 80,
      },
    })

    const renderDiagram = async () => {
      if (ref.current) {
        try {
          const uniqueId = `${id}-${Date.now()}`
          const { svg } = await mermaid.render(uniqueId, chart)
          ref.current.innerHTML = svg
        } catch (error) {
          console.error('Mermaid rendering error:', error)
          ref.current.innerHTML = `<pre>${chart}</pre>`
        }
      }
    }

    renderDiagram()
  }, [chart, id])

  return (
    <div
      ref={ref}
      className="flex items-center justify-center rounded-xl bg-white p-8"
      style={{ minHeight: '400px' }}
    />
  )
}
