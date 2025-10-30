'use client'

import MermaidDiagram from './MermaidDiagram'

export default function PDFProcessingArchitecture() {
  const decisionTree = `
graph TD
    Start(["PDF Document"]) --> Scan["Scan First 5 Pages"]

    Scan --> Convert["pdf2image: PDF → Images"]
    Convert --> Model["Vision Model Analysis<br/>table-transformer-detection"]

    Model --> Check{"Table Detection<br/>Score >= 0.90?"}

    Check -->|Yes| HasTable["✓ Tables Detected"]
    Check -->|No| NoTable["✗ No Tables"]

    HasTable --> RouteA["Route to OpenAI Vision API"]
    NoTable --> RouteB["Route to PyMuPDF4LLM"]

    RouteA --> CostA["Cost: ~$0.004/page<br/>Speed: 2-3 sec/page<br/>Quality: Excellent tables"]
    RouteB --> CostB["Cost: FREE<br/>Speed: < 1 sec/PDF<br/>Quality: Clean text"]

    CostA --> OutputA["Markdown with<br/>preserved tables<br/>+ page markers"]
    CostB --> OutputB["Markdown with<br/>clean formatting<br/>+ page markers"]

    OutputA --> Done(["data/output/file.md"])
    OutputB --> Done

    style HasTable fill:#ffcdd2
    style NoTable fill:#c8e6c9
    style RouteA fill:#ffe0b2
    style RouteB fill:#b2dfdb
    style Done fill:#e1bee7
  `

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        <div className="overflow-hidden rounded-2xl border-2 border-pink-200 bg-gradient-to-br from-pink-50 to-pink-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-pink-600">Detection Model</div>
            <div className="text-lg font-bold text-pink-900">table-transformer</div>
            <div className="mt-2 text-xs text-pink-700">90% accuracy • 240MB</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-green-200 bg-gradient-to-br from-green-50 to-green-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-green-600">Simple PDFs</div>
            <div className="text-lg font-bold text-green-900">PyMuPDF4LLM</div>
            <div className="mt-2 text-xs text-green-700">FREE • Ultra-fast</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-orange-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-orange-600">Complex PDFs</div>
            <div className="text-lg font-bold text-orange-900">OpenAI Vision</div>
            <div className="mt-2 text-xs text-orange-700">$0.004/page • GPT-4o-mini</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-purple-600">Processing</div>
            <div className="text-lg font-bold text-purple-900">Parallel</div>
            <div className="mt-2 text-xs text-purple-700">ThreadPool • 4 workers</div>
          </div>
        </div>
      </div>

      {/* Smart Routing Decision Tree */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-pink-50 via-rose-50 to-orange-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Smart Routing Architecture</h3>
          <p className="mt-1 text-sm text-slate-600">Vision-based table detection with intelligent converter selection</p>
        </div>
        <div className="p-8">
          <MermaidDiagram chart={decisionTree} id="decision-tree" />

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border-2 border-green-200 bg-gradient-to-br from-green-50 to-green-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-green-900">PyMuPDF4LLM Route</h5>
              <div className="space-y-2 text-sm text-green-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-green-500 flex-shrink-0"></div>
                  <div><strong>Trigger:</strong> No tables detected in first 5 pages</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-green-500 flex-shrink-0"></div>
                  <div><strong>Cost:</strong> Completely FREE (no API calls)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-green-500 flex-shrink-0"></div>
                  <div><strong>Speed:</strong> &lt;1 second per entire PDF</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-green-500 flex-shrink-0"></div>
                  <div><strong>Use Case:</strong> Text-heavy documents, reports, articles</div>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border-2 border-orange-200 bg-gradient-to-br from-orange-50 to-orange-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-orange-900">OpenAI Vision Route</h5>
              <div className="space-y-2 text-sm text-orange-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-orange-500 flex-shrink-0"></div>
                  <div><strong>Trigger:</strong> Tables detected (score ≥ 0.90)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-orange-500 flex-shrink-0"></div>
                  <div><strong>Cost:</strong> ~$0.004 per page (GPT-4o-mini)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-orange-500 flex-shrink-0"></div>
                  <div><strong>Speed:</strong> 2-3 seconds per page</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-orange-500 flex-shrink-0"></div>
                  <div><strong>Use Case:</strong> Financial statements, data sheets, forms</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Processing Pipeline */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Two-Phase Processing Pipeline</h3>
        </div>
        <div className="p-8">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-6">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500 text-white font-bold">1</div>
                <h5 className="text-lg font-bold text-blue-900">Detection Phase</h5>
              </div>
              <div className="space-y-3 text-sm text-blue-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Convert first 5 pages to images (pdf2image at 200 DPI)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Run table-transformer-detection model (PyTorch)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Filter detections with 90% confidence threshold</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Route each PDF to appropriate converter</div>
                </div>
              </div>
            </div>
            <div className="rounded-xl border border-purple-200 bg-purple-50 p-6">
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-500 text-white font-bold">2</div>
                <h5 className="text-lg font-bold text-purple-900">Conversion Phase</h5>
              </div>
              <div className="space-y-3 text-sm text-purple-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Parallel processing with ThreadPool (4 workers)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Each PDF converted independently and concurrently</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Vision API processes in 5-page chunks for efficiency</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Output saved to data/output/ with detailed logging</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cost Optimization */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-green-50 to-emerald-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Cost Optimization Strategy</h3>
        </div>
        <div className="p-8">
          <div className="rounded-2xl border-2 border-emerald-200 bg-gradient-to-br from-emerald-50 to-green-100 p-6">
            <div className="mb-4 text-lg font-bold text-emerald-900">Smart Detection Saves Money</div>
            <div className="space-y-3 text-sm text-emerald-800">
              <div className="flex items-start gap-3">
                <div className="mt-1 font-bold text-emerald-600">✓</div>
                <div>
                  <strong>Only scan first 5 pages</strong> - Most documents have consistent formatting throughout
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-1 font-bold text-emerald-600">✓</div>
                <div>
                  <strong>FREE for ~70% of documents</strong> - Most business docs are text-only
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-1 font-bold text-emerald-600">✓</div>
                <div>
                  <strong>Vision API only when needed</strong> - Pay only for complex table processing
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="mt-1 font-bold text-emerald-600">✓</div>
                <div>
                  <strong>Parallel processing</strong> - Multiple PDFs converted simultaneously for faster throughput
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">240MB</div>
              <div className="text-xs text-slate-600">Detection Model</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">90%</div>
              <div className="text-xs text-slate-600">Detection Accuracy</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">5</div>
              <div className="text-xs text-slate-600">Pages/Chunk</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">4</div>
              <div className="text-xs text-slate-600">Max Workers</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
