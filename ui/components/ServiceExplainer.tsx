'use client'

import { FileText, Database, Brain, Zap } from 'lucide-react'

export default function ServiceExplainer() {
  const services = [
    {
      name: 'PDF-to-MD Converter',
      icon: FileText,
      color: 'pink',
      whatItDoes: 'Utility tool (not a service) that converts PDFs to Markdown on-demand',
      howItWorks: [
        'Step 1: Vision model (Microsoft table-transformer) detects tables in PDF',
        'Step 2a: NO tables detected → Process with PyMuPDF (FREE, local)',
        'Step 2b: Tables detected → Convert pages to PNG images',
        'Step 2c: Send images to GPT-4o-mini Vision API ($0.01-$0.05/page)',
        'Step 3: Output clean Markdown with preserved formatting',
        'Run via: docker exec -it pdf-to-md python main.py'
      ],
      cost: 'FREE for simple PDFs | $0.01-$0.05/page ONLY if tables detected',
      speed: '1-2 seconds per page',
      useCases: [
        'Research papers with complex tables',
        'Financial statements and reports',
        'Technical documentation',
        'Scientific papers with data tables'
      ]
    },
    {
      name: 'RAG Service',
      icon: Database,
      color: 'purple',
      whatItDoes: 'Stores and retrieves documents using semantic search',
      howItWorks: [
        'Breaks documents into chunks',
        'Creates embeddings using sentence-transformers',
        'Stores vectors in Milvus database',
        'Hybrid search: semantic + entity matching',
        'Returns most relevant context for questions'
      ],
      cost: '$0 (uses open-source models)',
      speed: '<200ms per search',
      useCases: [
        'Q&A over large document collections',
        'Semantic search across PDFs',
        'Context retrieval for chatbots',
        'Knowledge base search'
      ]
    },
    {
      name: 'Reasoning API',
      icon: Brain,
      color: 'blue',
      whatItDoes: 'Answers questions using retrieved context',
      howItWorks: [
        'Gets question from user',
        'Retrieves relevant context from RAG',
        'Stage 1: Generate answer (GPT-4o-mini)',
        'Stage 2: Verify answer quality (GPT-4o-mini)',
        'Returns high-quality, verified answer'
      ],
      cost: '<$0.001 per query',
      speed: '2-4 seconds per answer',
      useCases: [
        'Chatbots over documents',
        'Technical Q&A systems',
        'Customer support automation',
        'Research assistants'
      ]
    },
    {
      name: 'Milvus Database',
      icon: Zap,
      color: 'green',
      whatItDoes: 'Ultra-fast vector similarity search',
      howItWorks: [
        'Stores document embeddings as vectors',
        'Uses HNSW algorithm for fast search',
        'Scales to billions of vectors',
        'Provides sub-100ms search latency'
      ],
      cost: '$0 (self-hosted)',
      speed: '<100ms for searches',
      useCases: [
        'Large-scale semantic search',
        'Recommendation systems',
        'Similarity matching',
        'Vector analytics'
      ]
    }
  ]

  const colorClasses = {
    pink: {
      bg: 'bg-pink-50',
      border: 'border-pink-200',
      icon: 'bg-gradient-to-br from-pink-500 to-rose-500',
      badge: 'bg-pink-100 text-pink-700'
    },
    purple: {
      bg: 'bg-purple-50',
      border: 'border-purple-200',
      icon: 'bg-gradient-to-br from-purple-500 to-indigo-500',
      badge: 'bg-purple-100 text-purple-700'
    },
    blue: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      icon: 'bg-gradient-to-br from-blue-500 to-cyan-500',
      badge: 'bg-blue-100 text-blue-700'
    },
    green: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      icon: 'bg-gradient-to-br from-green-500 to-emerald-500',
      badge: 'bg-green-100 text-green-700'
    }
  }

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-slate-900 mb-3">
          Microservices Architecture
        </h1>
        <p className="text-lg text-slate-600 max-w-3xl mx-auto">
          Each service does one thing really well. Here's exactly what each one does, how it works, and what it costs.
        </p>
      </div>

      {services.map((service, idx) => {
        const colors = colorClasses[service.color as keyof typeof colorClasses]
        const Icon = service.icon

        return (
          <div
            key={idx}
            className={`rounded-2xl border-2 ${colors.border} ${colors.bg} p-8 shadow-lg`}
          >
            <div className="flex items-start gap-6">
              <div className={`flex-shrink-0 p-4 rounded-xl ${colors.icon} text-white shadow-lg`}>
                <Icon className="h-8 w-8" />
              </div>

              <div className="flex-1">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">{service.name}</h2>

                {/* What it does */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-2">What it does:</h3>
                  <p className="text-slate-700">{service.whatItDoes}</p>
                </div>

                {/* How it works */}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-slate-800 mb-3">How it works:</h3>
                  <ol className="space-y-2">
                    {service.howItWorks.map((step, i) => (
                      <li key={i} className="flex items-start gap-3">
                        <span className={`flex-shrink-0 w-6 h-6 rounded-full ${colors.badge} flex items-center justify-center text-sm font-bold`}>
                          {i + 1}
                        </span>
                        <span className="text-slate-700 pt-0.5">{step}</span>
                      </li>
                    ))}
                  </ol>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className={`p-4 rounded-xl ${colors.badge} bg-opacity-50`}>
                    <div className="text-xs font-semibold uppercase tracking-wide mb-1">Cost</div>
                    <div className="text-lg font-bold">{service.cost}</div>
                  </div>
                  <div className={`p-4 rounded-xl ${colors.badge} bg-opacity-50`}>
                    <div className="text-xs font-semibold uppercase tracking-wide mb-1">Speed</div>
                    <div className="text-lg font-bold">{service.speed}</div>
                  </div>
                </div>

                {/* Use cases */}
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-3">Use cases:</h3>
                  <div className="flex flex-wrap gap-2">
                    {service.useCases.map((useCase, i) => (
                      <span
                        key={i}
                        className={`px-3 py-1.5 rounded-lg text-sm ${colors.badge}`}
                      >
                        {useCase}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
