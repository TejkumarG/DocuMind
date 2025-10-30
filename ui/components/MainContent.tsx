'use client'

import { useState } from 'react'
import Sidebar from './Sidebar'
import ChatInterface from './ChatInterface'
import ServiceHealth from './ServiceHealth'
import ServiceExplainer from './ServiceExplainer'
import ReasoningArchitecture from './ReasoningArchitecture'
import RAGPipelineArchitecture from './RAGPipelineArchitecture'
import PDFProcessingArchitecture from './PDFProcessingArchitecture'

type Tab = 'dashboard' | 'chat' | 'services' | 'reasoning' | 'rag' | 'pdf'

export default function MainContent() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      <main className="flex-1 overflow-y-auto">
        {activeTab === 'dashboard' && (
          <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-8">
            <div className="mx-auto max-w-6xl">
              <div className="mb-8">
                <h1 className="text-4xl font-bold text-slate-900 mb-3">
                  System Dashboard
                </h1>
                <p className="text-lg text-slate-600">
                  Real-time status of all microservices
                </p>
              </div>
              <ServiceHealth />
            </div>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50 p-8">
            <div className="mx-auto max-w-6xl">
              <ServiceExplainer />
            </div>
          </div>
        )}

        {activeTab === 'chat' && <ChatInterface />}

        {activeTab === 'reasoning' && (
          <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 p-8">
            <div className="mx-auto max-w-7xl">
              <div className="mb-8">
                <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-blue-500/10 px-4 py-2 text-sm font-medium text-blue-700">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-blue-400 opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-blue-500"></span>
                  </span>
                  AI Reasoning Framework
                </div>
                <h1 className="mb-3 text-4xl font-bold text-slate-900">
                  DSPy Reasoning Service
                </h1>
                <p className="text-lg text-slate-600">
                  Two-Stage Reason + Verify Pipeline with GPT-4o-mini (DSPy Framework)
                </p>
                <div className="mt-4 inline-flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 px-4 py-2">
                  <span className="text-sm text-amber-800">
                    <strong>Note:</strong> DSPy is NOT RAG. It's a prompt optimization framework that uses RAG's context.
                  </span>
                </div>
              </div>
              <ReasoningArchitecture />
            </div>
          </div>
        )}

        {activeTab === 'rag' && (
          <div className="min-h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-slate-50 p-8">
            <div className="mx-auto max-w-7xl">
              <div className="mb-8">
                <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-purple-500/10 px-4 py-2 text-sm font-medium text-purple-700">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-purple-400 opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-purple-500"></span>
                  </span>
                  Hybrid Retrieval System
                </div>
                <h1 className="mb-3 text-4xl font-bold text-slate-900">
                  Hybrid RAG Pipeline
                </h1>
                <p className="text-lg text-slate-600">
                  Semantic Search + Entity Matching with Milvus Vector Database
                </p>
              </div>
              <RAGPipelineArchitecture />
            </div>
          </div>
        )}

        {activeTab === 'pdf' && (
          <div className="min-h-screen bg-gradient-to-br from-slate-50 via-pink-50 to-slate-50 p-8">
            <div className="mx-auto max-w-7xl">
              <div className="mb-8">
                <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-pink-500/10 px-4 py-2 text-sm font-medium text-pink-700">
                  <span className="relative flex h-2 w-2">
                    <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-pink-400 opacity-75"></span>
                    <span className="relative inline-flex h-2 w-2 rounded-full bg-pink-500"></span>
                  </span>
                  Intelligent Processing
                </div>
                <h1 className="mb-3 text-4xl font-bold text-slate-900">
                  PDF Processing System
                </h1>
                <p className="text-lg text-slate-600">
                  Vision-Based Table Detection with Smart Routing
                </p>
              </div>
              <PDFProcessingArchitecture />
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
