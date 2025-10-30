'use client'

import { useEffect, useState } from 'react'
import { Activity, Check, X, Loader2 } from 'lucide-react'

interface ServiceStatus {
  name: string
  url: string
  status: 'healthy' | 'unhealthy' | 'checking'
  description: string
  port: number
}

export default function ServiceHealth() {
  const ragApiUrl = process.env.NEXT_PUBLIC_RAG_API_URL || 'http://localhost:8000'
  const reasoningApiUrl = process.env.NEXT_PUBLIC_REASONING_API_URL || 'http://localhost:8001'

  const [services, setServices] = useState<ServiceStatus[]>([
    {
      name: 'RAG Service',
      url: ragApiUrl,
      status: 'checking',
      description: 'Document ingestion & retrieval with Milvus vector database',
      port: 8000
    },
    {
      name: 'Reasoning API',
      url: reasoningApiUrl,
      status: 'checking',
      description: 'DSPy-powered AI reasoning with GPT-4o-mini (2-stage pipeline)',
      port: 8001
    },
    {
      name: 'Milvus Database',
      url: `${ragApiUrl}/milvus-health`,
      status: 'checking',
      description: 'Vector database for ultra-fast semantic search',
      port: 19530
    }
  ])

  useEffect(() => {
    checkServices()
    const interval = setInterval(checkServices, 10000) // Check every 10s
    return () => clearInterval(interval)
  }, [])

  const checkServices = async () => {
    const updatedServices = await Promise.all(
      services.map(async (service) => {
        try {
          const response = await fetch(service.url, {
            method: 'GET',
            mode: 'cors'
          })
          return {
            ...service,
            status: response.ok ? 'healthy' as const : 'unhealthy' as const
          }
        } catch (error) {
          return {
            ...service,
            status: 'unhealthy' as const
          }
        }
      })
    )
    setServices(updatedServices)
  }

  const healthyCount = services.filter(s => s.status === 'healthy').length
  const totalServices = services.length

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-slate-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <Activity className="h-6 w-6 text-blue-500" />
            System Services
          </h2>
          <p className="text-sm text-slate-600 mt-1">
            Real-time health status of all microservices
          </p>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-slate-900">
            {healthyCount}/{totalServices}
          </div>
          <div className="text-xs text-slate-600">Services Online</div>
        </div>
      </div>

      <div className="grid gap-4">
        {services.map((service, idx) => (
          <div
            key={idx}
            className={`p-4 rounded-xl border-2 transition-all ${
              service.status === 'healthy'
                ? 'bg-green-50 border-green-200'
                : service.status === 'unhealthy'
                ? 'bg-red-50 border-red-200'
                : 'bg-slate-50 border-slate-200'
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="font-semibold text-slate-900">{service.name}</h3>
                  {service.status === 'healthy' && (
                    <div className="flex items-center gap-1 text-green-700 text-sm">
                      <Check className="h-4 w-4" />
                      <span>Online</span>
                    </div>
                  )}
                  {service.status === 'unhealthy' && (
                    <div className="flex items-center gap-1 text-red-700 text-sm">
                      <X className="h-4 w-4" />
                      <span>Offline</span>
                    </div>
                  )}
                  {service.status === 'checking' && (
                    <div className="flex items-center gap-1 text-slate-600 text-sm">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Checking...</span>
                    </div>
                  )}
                </div>
                <p className="text-sm text-slate-600 mb-2">{service.description}</p>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  <span>Port: {service.port}</span>
                  <span>•</span>
                  <span className="font-mono">{service.url}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-200">
        <p className="text-sm text-blue-900 mb-2">
          <strong>💡 Note:</strong> All services must be online (green) before using the chat interface.
          Start services with: <code className="bg-white px-2 py-1 rounded">docker-compose up -d</code>
        </p>
      </div>

      <div className="mt-4 p-4 bg-purple-50 rounded-xl border border-purple-200">
        <p className="text-sm text-purple-900">
          <strong>🔧 Utility Tools:</strong> PDF-to-MD Converter is NOT a running service.
          It's an on-demand tool. Run it with: <code className="bg-white px-2 py-1 rounded">docker exec -it pdf-to-md python main.py</code>
        </p>
      </div>
    </div>
  )
}
