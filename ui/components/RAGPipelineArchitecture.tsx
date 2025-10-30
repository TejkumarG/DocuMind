'use client'

import MermaidDiagram from './MermaidDiagram'

export default function RAGPipelineArchitecture() {
  const ingestionFlow = `
flowchart TD
    Start(["📄 Document File"]) --> Load["Document Loader<br/>Split by pages"]
    Load --> Pages["Pages Array<br/>Each page = 1 chunk"]

    Pages --> Hash["Calculate SHA256<br/>File Hash"]
    Hash --> Check{"Already<br/>Exists?"}
    Check -->|Yes| Skip(["❌ Skip Document"])
    Check -->|No| Process["Process Each Page"]

    Process --> NER["🤖 spaCy NER<br/>Extract entities"]
    NER --> Entities["Extract:<br/>PERSON, ORG, LOC<br/>DATE, CARDINAL"]
    Entities --> Lower["Convert to lowercase<br/>Store as JSON"]

    Process --> Embed["🤖 Sentence Transformer<br/>Generate embeddings"]
    Embed --> Vectors["384-dim vectors"]

    Lower --> Combine["Combine Metadata"]
    Vectors --> Combine
    Combine --> Insert["Insert into Milvus<br/>document_chunks"]
    Insert --> Success(["✅ Complete"])

    style NER fill:#ff9999
    style Embed fill:#99ccff
    style Insert fill:#99ff99
  `

  const retrievalFlow = `
flowchart TD
    Query(["🔍 User Query"]) --> Parallel{"Run Both Scenarios<br/>in Parallel"}

    %% Scenario 1: Direct Semantic
    Parallel --> S1["Scenario 1:<br/>Direct Semantic"]
    S1 --> S1_Embed["Step 1: 🤖 Embed query<br/>384-dim vector"]
    S1_Embed --> S1_Search["Step 2: Milvus search<br/>on ALL documents"]
    S1_Search --> S1_Top3["Get top 3 chunks"]
    S1_Top3 --> S1_Docs["Extract document_ids<br/>from those 3"]
    S1_Docs --> S1_Step3["Step 3: Milvus search<br/>ONLY in those documents"]
    S1_Step3 --> S1_Result["Get top 5 chunks"]

    %% Scenario 2: Entity-based
    Parallel --> S2["Scenario 2:<br/>Entity-based"]
    S2 --> S2_NER["🤖 spaCy NER<br/>Extract entities"]
    S2_NER --> S2_Has{"Has<br/>Entities?"}
    S2_Has -->|No| S2_Empty(["0 chunks"])
    S2_Has -->|Yes| S2_Query["Query ALL chunks<br/>NO semantic search"]
    S2_Query --> S2_Filter["Filter by entity match<br/>Count matches per chunk"]
    S2_Filter --> S2_Sort["Sort by match count"]
    S2_Sort --> S2_Top2["Select top 2<br/>entity chunks"]
    S2_Top2 --> S2_AllDocs["Extract document IDs<br/>from ALL matches"]
    S2_AllDocs --> S2_Semantic["Semantic search<br/>within matched documents"]
    S2_Semantic --> S2_Top2More["Select top 2<br/>semantic chunks"]
    S2_Top2 --> S2_Combine["Combine"]
    S2_Top2More --> S2_Combine
    S2_Combine --> S2_Result["4 chunks total"]

    %% Final Combination
    S1_Result --> Final["Combine Results"]
    S2_Result --> Final
    S2_Empty --> Final

    Final --> Dedup["Deduplicate by ID"]
    Dedup --> Sort["Sort by distance"]
    Sort --> Return(["✅ Return 6-9 chunks"])

    style S1_Embed fill:#99ccff
    style S2_NER fill:#ff9999
    style S2_Filter fill:#ffcc99
    style Return fill:#99ff99
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
            <div className="text-lg font-bold text-purple-900">6-9 chunks</div>
            <div className="mt-2 text-xs text-purple-700">Deduplicated & ranked</div>
          </div>
        </div>
      </div>

      {/* Ingestion Flow */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-green-50 via-emerald-50 to-teal-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Document Ingestion Pipeline</h3>
          <p className="mt-1 text-sm text-slate-600">Processing documents into vector embeddings with entity extraction</p>
        </div>
        <div className="p-8">
          <MermaidDiagram chart={ingestionFlow} id="ingestion-flow" />
        </div>
      </div>

      {/* Hybrid Retrieval Flow */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-purple-50 via-blue-50 to-cyan-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Hybrid Retrieval Architecture</h3>
          <p className="mt-1 text-sm text-slate-600">Two parallel scenarios: semantic search + entity-based filtering</p>
        </div>
        <div className="p-8">
          <MermaidDiagram chart={retrievalFlow} id="retrieval-flow" />

          <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-blue-900">Scenario 1: Direct Semantic</h5>
              <div className="space-y-2 text-sm text-blue-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Semantic search on ALL docs → top 3 chunks</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Extract document_ids from those 3 chunks</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div>Semantic search within those docs → top 5</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-blue-500 flex-shrink-0"></div>
                  <div><strong>Returns: 5 chunks</strong></div>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-purple-900">Scenario 2: Entity-Based</h5>
              <div className="space-y-2 text-sm text-purple-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Extract entities with spaCy NER</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Query ALL 900+ chunks (no semantic!)</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Filter by entity match → sort by count</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div>Top 2 entity + 2 semantic from matched docs</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div><strong>Returns: 4 chunks</strong></div>
                </div>
              </div>
            </div>
          </div>

          {/* NEW: Key Difference Highlight */}
          <div className="mt-6 rounded-xl border-2 border-orange-200 bg-orange-50 p-6">
            <h5 className="mb-3 font-bold text-orange-900">🔑 Key Difference</h5>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 text-sm">
              <div className="text-orange-800">
                <strong>Scenario 1 (Semantic):</strong> Uses vector similarity throughout. Fast but may miss exact entity matches if semantically distant.
              </div>
              <div className="text-orange-800">
                <strong>Scenario 2 (Entity):</strong> Filters ALL chunks by entity first, then uses semantic only for expansion. Guarantees entity presence.
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
                  <div><strong>Entities:</strong> PERSON, ORG, GPE, LOC, DATE, CARDINAL</div>
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
              <div className="text-2xl font-bold text-slate-900">6-9</div>
              <div className="text-xs text-slate-600">Results Returned</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">900+</div>
              <div className="text-xs text-slate-600">Total Chunks</div>
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
                <h5 className="font-bold text-blue-900">Semantic Power</h5>
              </div>
              <p className="text-sm text-blue-800">
                Catches similar meaning even without exact keyword matches. Great for concept-based queries and finding related content.
              </p>
            </div>
            <div className="rounded-xl border border-purple-200 bg-purple-50 p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-purple-500"></div>
                <h5 className="font-bold text-purple-900">Entity Precision</h5>
              </div>
              <p className="text-sm text-purple-800">
                Queries ALL chunks by entity match first. Ensures specific names, dates, numbers, and organizations are found accurately.
              </p>
            </div>
            <div className="rounded-xl border border-green-200 bg-green-50 p-6">
              <div className="mb-3 flex items-center gap-2">
                <div className="h-3 w-3 rounded-full bg-green-500"></div>
                <h5 className="font-bold text-green-900">Combined Results</h5>
              </div>
              <p className="text-sm text-green-800">
                Deduplicates overlaps and ranks by L2 distance. Best of both approaches for comprehensive and accurate retrieval.
              </p>
            </div>
          </div>

          <div className="mt-6 rounded-xl border-2 border-amber-200 bg-amber-50 p-6">
            <h5 className="mb-3 font-bold text-amber-900">Technical Implementation</h5>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 text-sm text-amber-800">
              <div>
                <strong>Model Consistency:</strong> Both ingestion and retrieval use identical models (all-MiniLM-L6-v2 and en_core_web_md) ensuring vector space alignment.
              </div>
              <div>
                <strong>Entity-First Approach:</strong> Scenario 2 queries ALL chunks without semantic filtering, ensuring entity matches aren't missed due to semantic distance.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
