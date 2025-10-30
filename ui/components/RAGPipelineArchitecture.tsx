'use client'

import MermaidDiagram from './MermaidDiagram'

export default function RAGPipelineArchitecture() {
  const retrievalFlow = `
flowchart TD
    Query(["🔍 User Query"]) --> Parallel{"Parallel Processing"}

    %% Semantic Search Branch
    Parallel --> Semantic["Path 1: Semantic Search"]
    Semantic --> EmbedQ1["🤖 Sentence Transformer<br/>all-MiniLM-L6-v2"]
    EmbedQ1 --> Vector1["Generate Query<br/>Embedding 384-dim"]
    Vector1 --> MilvusS["Milvus Vector Search<br/>L2 Distance"]
    MilvusS --> TopS["Top 3 Chunks<br/>by Similarity"]

    %% Entity Search Branch
    Parallel --> Entity["Path 2: Entity Search"]
    Entity --> NERQ["🤖 spaCy NER<br/>en_core_web_md"]
    NERQ --> ExtractQ["Extract Query Entities<br/>Convert to Lowercase"]
    ExtractQ --> HasEnt{"Has<br/>Entities?"}
    HasEnt -->|No| EmptyE(["Return Empty"])
    HasEnt -->|Yes| EmbedQ2["🤖 Sentence Transformer<br/>all-MiniLM-L6-v2"]
    EmbedQ2 --> Vector2["Generate Query<br/>Embedding 384-dim"]
    Vector2 --> MilvusE["Milvus Vector Search<br/>Get Top 15 Candidates"]
    MilvusE --> Filter["Python Filter:<br/>Match query entities with<br/>chunk entities<br/>Case-insensitive substring"]
    Filter --> RankE["Rank by Semantic<br/>Similarity L2 Distance"]
    RankE --> TopE["Top 3 Chunks<br/>with Entity Match"]

    %% Combine Results
    TopS --> Combine["Combine Results"]
    TopE --> Combine
    EmptyE --> Combine

    Combine --> Dedup["Deduplicate by Chunk ID"]
    Dedup --> Limit["Apply Limits:<br/>Min: 3 chunks<br/>Max: 6 chunks"]
    Limit --> Final(["✅ Return Results"])

    style EmbedQ1 fill:#99ccff
    style EmbedQ2 fill:#99ccff
    style NERQ fill:#ff9999
    style Filter fill:#ffcc99
    style Final fill:#99ff99
  `

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        <div className="overflow-hidden rounded-2xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-blue-600">Embedding Model</div>
            <div className="text-lg font-bold text-blue-900">all-MiniLM-L6-v2</div>
            <div className="mt-2 text-xs text-blue-700">90MB • 384-dim</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-red-200 bg-gradient-to-br from-red-50 to-red-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-red-600">NER Model</div>
            <div className="text-lg font-bold text-red-900">en_core_web_md</div>
            <div className="mt-2 text-xs text-red-700">43MB • spaCy 3.7.x</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-green-200 bg-gradient-to-br from-green-50 to-green-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-green-600">Vector DB</div>
            <div className="text-lg font-bold text-green-900">Milvus 2.3.3</div>
            <div className="mt-2 text-xs text-green-700">IVF_FLAT + L2 distance</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-purple-600">Results</div>
            <div className="text-lg font-bold text-purple-900">3-6 chunks</div>
            <div className="mt-2 text-xs text-purple-700">Deduplicated & ranked</div>
          </div>
        </div>
      </div>

      {/* Hybrid Retrieval Flow */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-purple-50 via-blue-50 to-cyan-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Hybrid Retrieval Architecture</h3>
          <p className="mt-1 text-sm text-slate-600">Parallel semantic search + entity matching for optimal results</p>
        </div>
        <div className="p-8">
          <MermaidDiagram chart={retrievalFlow} id="retrieval-flow" />

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-blue-900">Path 1: Semantic Search</h5>
              <div className="space-y-2 text-sm text-blue-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Encodes query with Sentence Transformer</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Searches Milvus by L2 distance (vector similarity)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Returns top 3 most similar chunks</div>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-purple-900">Path 2: Entity Search</h5>
              <div className="space-y-2 text-sm text-purple-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Extracts entities (names, dates, orgs) with spaCy NER</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Filters top 15 candidates by entity match (substring)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Returns top 3 ranked by semantic similarity</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Model Details */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">AI Models & Infrastructure</h3>
        </div>
        <div className="p-8">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-blue-900">Embedding Model</h5>
              <div className="space-y-2 text-sm text-blue-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div><strong>Model:</strong> sentence-transformers/all-MiniLM-L6-v2</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div><strong>Size:</strong> 90MB (compact yet powerful)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div><strong>Dimensions:</strong> 384-dimensional vectors</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div><strong>Speed:</strong> ~1000 sentences/sec on CPU</div>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border-2 border-red-200 bg-gradient-to-br from-red-50 to-red-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-red-900">NER Model</h5>
              <div className="space-y-2 text-sm text-red-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-red-500 flex-shrink-0"></div>
                  <div><strong>Model:</strong> spaCy en_core_web_md v3.7.x</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-red-500 flex-shrink-0"></div>
                  <div><strong>Size:</strong> 43MB (includes word vectors)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-red-500 flex-shrink-0"></div>
                  <div><strong>Entities:</strong> PERSON, ORG, GPE, LOC, DATE</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-red-500 flex-shrink-0"></div>
                  <div><strong>Normalization:</strong> All entities lowercased</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Vector Database Details */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-green-50 to-emerald-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Vector Database Configuration</h3>
        </div>
        <div className="p-8">
          <div className="rounded-2xl border-2 border-green-200 bg-gradient-to-br from-green-50 to-green-100 p-6">
            <div className="mb-4 text-lg font-bold text-green-900">Milvus 2.3.3 Setup</div>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className="space-y-3 text-sm text-green-800">
                <div className="flex items-start gap-3">
                  <div className="mt-1 font-bold text-green-600">✓</div>
                  <div>
                    <strong>Index Type:</strong> IVF_FLAT (Inverted File with Flat compression)
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 font-bold text-green-600">✓</div>
                  <div>
                    <strong>Distance Metric:</strong> L2 (Euclidean distance)
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 font-bold text-green-600">✓</div>
                  <div>
                    <strong>Collection Schema:</strong> document_id, file_hash, page_number, text, embedding[384], 5 entity fields
                  </div>
                </div>
              </div>
              <div className="space-y-3 text-sm text-green-800">
                <div className="flex items-start gap-3">
                  <div className="mt-1 font-bold text-green-600">✓</div>
                  <div>
                    <strong>Metadata Storage:</strong> etcd for cluster metadata
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 font-bold text-green-600">✓</div>
                  <div>
                    <strong>Object Storage:</strong> MinIO for vector data persistence
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="mt-1 font-bold text-green-600">✓</div>
                  <div>
                    <strong>Deduplication:</strong> SHA256 file hash prevents duplicates
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">384</div>
              <div className="text-xs text-slate-600">Vector Dimensions</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">L2</div>
              <div className="text-xs text-slate-600">Distance Metric</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">3-6</div>
              <div className="text-xs text-slate-600">Results Returned</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">5</div>
              <div className="text-xs text-slate-600">Entity Types</div>
            </div>
          </div>
        </div>
      </div>

      {/* Why Hybrid Search */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-amber-50 to-orange-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Why Hybrid Search?</h3>
        </div>
        <div className="p-8">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <div className="rounded-xl border border-blue-200 bg-blue-50 p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-blue-500"></div>
                <h5 className="font-bold text-blue-900">Semantic Search</h5>
              </div>
              <p className="text-sm text-blue-800">
                Catches similar meaning even without exact keyword matches. Great for concept-based queries.
              </p>
            </div>
            <div className="rounded-xl border border-purple-200 bg-purple-50 p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-purple-500"></div>
                <h5 className="font-bold text-purple-900">Entity Matching</h5>
              </div>
              <p className="text-sm text-purple-800">
                Ensures specific names, dates, and organizations are found accurately. Critical for precise queries.
              </p>
            </div>
            <div className="rounded-xl border border-green-200 bg-green-50 p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-green-500"></div>
                <h5 className="font-bold text-green-900">Combined Power</h5>
              </div>
              <p className="text-sm text-green-800">
                Deduplicated and ranked by L2 distance. Best of both approaches for comprehensive retrieval.
              </p>
            </div>
          </div>

          <div className="mt-6 rounded-xl border-2 border-amber-200 bg-amber-50 p-6">
            <h5 className="mb-3 font-bold text-amber-900">Technical Details</h5>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 text-sm text-amber-800">
              <div>
                <strong>Model Consistency:</strong> Both ingestion and retrieval use the same models (all-MiniLM-L6-v2 and en_core_web_md) to ensure vector space alignment.
              </div>
              <div>
                <strong>Milvus Workaround:</strong> Since Milvus doesn't support substring matching, we fetch candidates via vector search and filter in Python.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
