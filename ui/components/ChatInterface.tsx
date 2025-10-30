'use client'

import { Send, Sparkles, Clock, DollarSign, Loader2, Trash2 } from 'lucide-react'
import { useState, useEffect } from 'react'

interface Message {
  id?: string
  role: string
  content: string
  timestamp?: string
  createdAt?: string
}

export default function ChatInterface() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)

  // Load chat history from database on component mount
  useEffect(() => {
    loadChatHistory()
  }, [])

  const loadChatHistory = async () => {
    try {
      const response = await fetch('/api/chat/messages')
      if (response.ok) {
        const history = await response.json()
        if (history.length === 0) {
          // If no history, add welcome message (only once)
          const welcomeMessage = {
            role: 'assistant',
            content: 'Hello! I\'m your AI Architecture Assistant. Ask me anything about the RAG pipeline, PDF processing, or DSPy framework.',
          }
          // Save to DB first
          const saveResponse = await fetch('/api/chat/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(welcomeMessage),
          })

          if (saveResponse.ok) {
            const savedMessage = await saveResponse.json()
            // Use the saved message with DB timestamp
            setMessages([{
              ...savedMessage,
              timestamp: new Date(savedMessage.createdAt).toLocaleTimeString(),
            }])
          }
        } else {
          // Format timestamps for existing messages
          setMessages(history.map((msg: Message) => ({
            ...msg,
            timestamp: new Date(msg.createdAt || '').toLocaleTimeString(),
          })))
        }
      }
    } catch (error) {
      console.error('Error loading chat history:', error)
    } finally {
      setIsLoadingHistory(false)
    }
  }

  const saveMessageToDb = async (msg: { role: string; content: string }) => {
    try {
      await fetch('/api/chat/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(msg),
      })
    } catch (error) {
      console.error('Error saving message:', error)
    }
  }

  const clearChatHistory = async () => {
    if (!confirm('Are you sure you want to clear all chat history?')) return

    try {
      const response = await fetch('/api/chat/messages', {
        method: 'DELETE',
      })
      if (response.ok) {
        setMessages([])
        // Add welcome message after clearing
        const welcomeMessage = {
          role: 'assistant',
          content: 'Chat history cleared. How can I help you?',
        }
        await saveMessageToDb(welcomeMessage)
        setMessages([{ ...welcomeMessage, timestamp: new Date().toLocaleTimeString() }])
      }
    } catch (error) {
      console.error('Error clearing chat history:', error)
    }
  }

  const handleSend = async () => {
    if (!message.trim() || isLoading) return

    const userMessage = message
    setMessage('')

    // Create and save user message
    const userMsg = {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleTimeString(),
    }

    const newMessages = [...messages, userMsg]
    setMessages(newMessages)
    setIsLoading(true)

    // Save user message to DB
    await saveMessageToDb({ role: 'user', content: userMessage })

    try {
      // Call the real API
      const response = await fetch('http://localhost:8001/api/v1/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userMessage }),
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`)
      }

      const data = await response.json()

      // Create AI response
      const aiResponse = data.answer || 'No answer received from API'
      const aiMsg = {
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date().toLocaleTimeString(),
      }

      // Add AI response to state
      setMessages([...newMessages, aiMsg])

      // Save AI response to DB
      await saveMessageToDb({ role: 'assistant', content: aiResponse })
    } catch (error) {
      // Create error message
      const errorMsg = {
        role: 'assistant',
        content: `⚠️ Error connecting to Reasoning API: ${error instanceof Error ? error.message : 'Unknown error'}. Please ensure the service is running on port 8001.`,
        timestamp: new Date().toLocaleTimeString(),
      }

      // Add error to state
      setMessages([...newMessages, errorMsg])

      // Save error message to DB
      await saveMessageToDb({ role: 'assistant', content: errorMsg.content })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white/80 backdrop-blur-sm">
        <div className="mx-auto max-w-5xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">AI Chat Interface</h2>
              <p className="text-sm text-slate-600">
                Powered by DSPy RAG Pipeline • GPT-4o-mini
              </p>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <button
                onClick={clearChatHistory}
                className="flex items-center gap-2 rounded-lg bg-red-50 px-3 py-2 text-red-700 transition-colors hover:bg-red-100"
                title="Clear chat history"
              >
                <Trash2 className="h-4 w-4" />
                <span>Clear History</span>
              </button>
              <div className="flex items-center gap-2 rounded-lg bg-green-50 px-3 py-2">
                <div className="h-2 w-2 animate-pulse rounded-full bg-green-500"></div>
                <span className="text-green-700">Connected</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-6 py-3">
          <div className="flex items-center justify-center gap-8 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-blue-500" />
              <span className="text-slate-600">Latency:</span>
              <span className="font-semibold text-slate-900">2-4s</span>
            </div>
            <div className="h-4 w-px bg-slate-200"></div>
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-green-500" />
              <span className="text-slate-600">Cost/Query:</span>
              <span className="font-semibold text-slate-900">&lt; $0.001</span>
            </div>
            <div className="h-4 w-px bg-slate-200"></div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-purple-500" />
              <span className="text-slate-600">LLM Calls:</span>
              <span className="font-semibold text-slate-900">2 (Reason + Verify)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-5xl px-6 py-6">
          {isLoadingHistory ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex items-center gap-3 text-slate-600">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Loading chat history...</span>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-3xl rounded-2xl px-6 py-4 shadow-md ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                        : 'border border-slate-200 bg-white text-slate-800'
                    }`}
                  >
                    <div className="mb-2 flex items-center gap-2 text-xs opacity-70">
                      {msg.role === 'assistant' && (
                        <Sparkles className="h-3 w-3" />
                      )}
                      <span>{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
                      <span>•</span>
                      <span>{msg.timestamp}</span>
                    </div>
                    <div className="text-sm leading-relaxed">{msg.content}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-slate-200 bg-white">
        <div className="mx-auto max-w-5xl px-6 py-4">
          <div className="flex items-start gap-3">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about architecture, performance, or implementation details..."
              className="flex-1 resize-none rounded-xl border-2 border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-500 focus:bg-white focus:outline-none"
              rows={3}
            />
            <button
              onClick={handleSend}
              disabled={!message.trim() || isLoading}
              className="flex h-[84px] w-12 items-center justify-center rounded-xl bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg transition-all hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Send className="h-5 w-5" />
              )}
            </button>
          </div>

          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
            <span>Press Enter to send, Shift+Enter for new line</span>
            <span>{message.length} characters</span>
          </div>
        </div>
      </div>
    </div>
  )
}
