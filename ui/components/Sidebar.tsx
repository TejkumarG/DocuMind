'use client'

import { MessageSquare, Brain, Database, FileText, Activity, Layers } from 'lucide-react'

type Tab = 'dashboard' | 'chat' | 'services' | 'reasoning' | 'rag' | 'pdf'

interface SidebarProps {
  activeTab: Tab
  setActiveTab: (tab: Tab) => void
}

export default function Sidebar({ activeTab, setActiveTab }: SidebarProps) {
  const tabs = [
    {
      id: 'dashboard' as Tab,
      icon: Activity,
      label: 'Dashboard',
      gradient: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-500',
      textColor: 'text-green-700',
    },
    {
      id: 'services' as Tab,
      icon: Layers,
      label: 'Services',
      gradient: 'from-purple-500 to-indigo-500',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-500',
      textColor: 'text-purple-700',
    },
    {
      id: 'chat' as Tab,
      icon: MessageSquare,
      label: 'Chat',
      gradient: 'from-blue-500 to-cyan-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-500',
      textColor: 'text-blue-700',
    },
    {
      id: 'reasoning' as Tab,
      icon: Brain,
      label: 'Reasoning',
      gradient: 'from-blue-500 to-indigo-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-500',
      textColor: 'text-blue-700',
    },
    {
      id: 'rag' as Tab,
      icon: Database,
      label: 'RAG',
      gradient: 'from-purple-500 to-pink-500',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-500',
      textColor: 'text-purple-700',
    },
    {
      id: 'pdf' as Tab,
      icon: FileText,
      label: 'PDF Processing',
      gradient: 'from-pink-500 to-rose-500',
      bgColor: 'bg-pink-50',
      borderColor: 'border-pink-500',
      textColor: 'text-pink-700',
    },
  ]

  return (
    <aside className="flex h-screen w-72 flex-col border-r border-slate-200 bg-white">
      {/* Header */}
      <div className="border-b border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50 p-6">
        <h1 className="mb-1 text-xl font-bold text-slate-900">AI Architecture</h1>
        <p className="text-xs text-slate-600">Enterprise Showcase</p>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-2">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`group relative w-full rounded-xl p-4 text-left transition-all ${
                  isActive
                    ? `${tab.bgColor} border-2 ${tab.borderColor} shadow-lg`
                    : 'border-2 border-transparent bg-slate-50 hover:border-slate-200 hover:bg-slate-100'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br ${tab.gradient} text-white shadow-md transition-transform group-hover:scale-110`}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <div
                      className={`font-semibold ${
                        isActive ? tab.textColor : 'text-slate-700'
                      }`}
                    >
                      {tab.label}
                    </div>
                    {isActive && (
                      <div className="mt-0.5 text-xs text-slate-500">Active</div>
                    )}
                  </div>
                </div>

                {isActive && (
                  <div
                    className={`absolute left-0 top-1/2 h-12 w-1 -translate-y-1/2 rounded-r-full bg-gradient-to-b ${tab.gradient}`}
                  ></div>
                )}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-200 p-4">
        <div className="rounded-lg bg-gradient-to-r from-slate-100 to-blue-100 p-3 text-center">
          <div className="mb-1 text-xs font-semibold text-slate-700">
            Production Ready
          </div>
          <div className="flex items-center justify-center gap-2 text-xs text-slate-600">
            <div className="h-2 w-2 animate-pulse rounded-full bg-green-500"></div>
            <span>All Systems Online</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
