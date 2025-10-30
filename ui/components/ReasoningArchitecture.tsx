'use client'

import MermaidDiagram from './MermaidDiagram'

export default function ReasoningArchitecture() {
  const requestFlow = `flowchart TD
    Start["1. User sends question<br/>POST /api/v1/ask<br/>{question: 'What did WESTDALE do in June 2022?'}"] --> Route["2. FastAPI Route Handler<br/>(api/routes.py:ask_question)<br/>• Validates request with QuestionRequest schema<br/>• Extracts question string"]

    Route --> GetContext["3. Get Context<br/>(handlers/runtime/2_get_context.py)<br/>• POST to http://localhost:8000/retrieve<br/>• Payload: {query, min_chunks: 3, max: 6}<br/>• Response: {chunks: [{text: ...}, ...]}<br/>• Returns: List[str] with 3-6 context strings"]

    GetContext --> GetModel["4. Get RAG Model<br/>(api/routes.py:get_rag_model)<br/>• Checks if model is cached in _rag_model global var<br/>• If not cached:<br/>  a. Configure OpenAI (dspy.settings.configure)<br/>  b. Load DSPy model (compiled OR ReasonVerifyRAG())<br/>• Cache model for future requests"]

    GetModel --> Reason["5a. REASON (LLM Call #1)<br/><br/>Signature: ReasonSignature<br/>Input: context + question<br/>LLM generates DRAFT answer<br/>Uses ChainOfThought reasoning"]

    Reason --> Verify["5b. VERIFY (LLM Call #2)<br/><br/>Signature: VerifySignature<br/>Input: context + question + draft_answer<br/>LLM verifies and corrects draft<br/>Returns VERIFIED answer"]

    Verify --> Response["6. Format Response<br/>(api/routes.py:ask_question)<br/>• Extract verified_answer from result<br/>• Create AnswerResponse object<br/>• Include: question, answer, context_used"]

    Response --> Final["7. Response to User<br/>{<br/>  question: 'What did WESTDALE do...',<br/>  answer: 'In June 2022, WESTDALE...',<br/>  context_used: [chunk1, chunk2, ...],<br/>  reasoning: null<br/>}"]

    style Start fill:#e0f2fe
    style Route fill:#dbeafe
    style GetContext fill:#f3e8ff
    style GetModel fill:#fef3c7
    style Reason fill:#fed7aa
    style Verify fill:#bbf7d0
    style Response fill:#e0f2fe
    style Final fill:#d1fae5`

  const llmCallSequence = `sequenceDiagram
    participant User
    participant Context as Context<br/>(3-6 chunks)
    participant LLM1 as LLM #1<br/>REASON<br/>(GPT-4o-mini)
    participant LLM2 as LLM #2<br/>VERIFY<br/>(GPT-4o-mini)
    participant Response

    User->>Context: Question: "What did WESTDALE<br/>do in June 2022?"
    Note over Context: Retrieved context:<br/>3-6 relevant chunks

    Context->>LLM1: Input: context + question
    Note over LLM1: ChainOfThought<br/>Read & understand context<br/>Identify relevant info<br/>Generate draft answer
    LLM1-->>LLM2: draft_answer:<br/>"In June 2022, Westdale..."
    Note right of LLM1: Cost: ~0.5¢ per 1000 tokens

    LLM2->>LLM2: Input: context +<br/>question + draft_answer
    Note over LLM2: Re-read context<br/>Compare draft with context<br/>Check accuracy & completeness<br/>Correct errors or omissions<br/>Generate verified answer
    LLM2-->>Response: verified_answer:<br/>"In June 2022, WESTDALE..."
    Note right of LLM2: Cost: ~0.5¢ per 1000 tokens

    Response->>User: Final Answer ✓
    Note over Response: Total Cost: < $0.001`

  return (
    <div className="space-y-8">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="overflow-hidden rounded-2xl border-2 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-blue-600">Service</div>
            <div className="text-2xl font-bold text-blue-900">FastAPI + DSPy</div>
            <div className="mt-2 text-xs text-blue-700">Port 8001 • Optimized prompts</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-purple-600">Context Source</div>
            <div className="text-2xl font-bold text-purple-900">RAG Service</div>
            <div className="mt-2 text-xs text-purple-700">Port 8000 • 3-6 chunks</div>
          </div>
        </div>
        <div className="overflow-hidden rounded-2xl border-2 border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100 shadow-lg">
          <div className="p-6">
            <div className="mb-2 text-sm font-semibold text-amber-600">LLM</div>
            <div className="text-2xl font-bold text-amber-900">GPT-4o-mini</div>
            <div className="mt-2 text-xs text-amber-700">2 calls • &lt;$0.001/query</div>
          </div>
        </div>
      </div>

      {/* Complete Request Flow */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-purple-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Complete Request Flow</h3>
          <p className="mt-1 text-sm text-slate-600">User Question → Answer (7 steps)</p>
        </div>
        <div className="p-8">
          <MermaidDiagram chart={requestFlow} id="request-flow" />
        </div>
      </div>

      {/* LLM Call Sequence */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-orange-50 to-amber-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">LLM Call Sequence</h3>
          <p className="mt-1 text-sm text-slate-600">Two LLM calls per query (Reason + Verify)</p>
        </div>
        <div className="p-8">
          <MermaidDiagram chart={llmCallSequence} id="llm-sequence" />

          <div className="mt-6 rounded-lg border border-green-200 bg-green-50 p-6">
            <h5 className="mb-3 font-semibold text-green-900">Performance Metrics</h5>
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-700">2</div>
                <div className="text-xs text-green-600">LLM Calls</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-700">2-4s</div>
                <div className="text-xs text-blue-600">Latency</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-700">&lt;$0.001</div>
                <div className="text-xs text-purple-600">Cost/Query</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-700">3-6</div>
                <div className="text-xs text-orange-600">Context Chunks</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* DSPy Offline Training */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-purple-50 to-pink-50 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">DSPy Offline Training Layer</h3>
          <p className="mt-1 text-sm text-slate-600">Prompt optimization with few-shot learning and query rewriting</p>
        </div>
        <div className="p-8">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="rounded-2xl border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-purple-900">MIPROv2 Optimizer</h5>
              <div className="space-y-2 text-sm text-purple-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div><strong>Algorithm:</strong> Multi-Prompt Instruction Optimization v2</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div><strong>Training Data:</strong> 100 question-answer examples</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div><strong>LLM Calls:</strong> 300-600 during compilation</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-purple-500 flex-shrink-0"></div>
                  <div><strong>Cost:</strong> ~$0.50-$1.00 per compilation</div>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border-2 border-pink-200 bg-gradient-to-br from-pink-50 to-pink-100 p-6 shadow-md">
              <h5 className="mb-3 text-lg font-bold text-pink-900">Query Correction/Rewrite</h5>
              <div className="space-y-2 text-sm text-pink-800">
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-pink-500 flex-shrink-0"></div>
                  <div><strong>Few-Shot Learning:</strong> Learns from feedback examples</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-pink-500 flex-shrink-0"></div>
                  <div><strong>Auto-Optimization:</strong> Refines prompts automatically</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-pink-500 flex-shrink-0"></div>
                  <div><strong>Recompilation:</strong> Updates with 50+ new feedback samples</div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="mt-1 h-2 w-2 rounded-full bg-pink-500 flex-shrink-0"></div>
                  <div><strong>Storage:</strong> Feedback stored in JSONL format</div>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 rounded-2xl border-2 border-indigo-200 bg-gradient-to-br from-indigo-50 to-indigo-100 p-6">
            <div className="mb-4 text-lg font-bold text-indigo-900">Training Workflow</div>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
              <div className="rounded-xl border border-indigo-200 bg-white p-4">
                <div className="mb-3 flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-white font-bold text-sm">1</div>
                  <h6 className="font-bold text-indigo-900">Prepare Data</h6>
                </div>
                <p className="text-xs text-indigo-800">
                  Create training_samples.json with 100 question-context-answer triples for initial compilation
                </p>
              </div>
              <div className="rounded-xl border border-indigo-200 bg-white p-4">
                <div className="mb-3 flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-white font-bold text-sm">2</div>
                  <h6 className="font-bold text-indigo-900">Compile Model</h6>
                </div>
                <p className="text-xs text-indigo-800">
                  MIPROv2 optimizer generates optimized prompts for Reason and Verify stages, saved to compiled_rag_v1.dspy
                </p>
              </div>
              <div className="rounded-xl border border-indigo-200 bg-white p-4">
                <div className="mb-3 flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-500 text-white font-bold text-sm">3</div>
                  <h6 className="font-bold text-indigo-900">Continuous Learning</h6>
                </div>
                <p className="text-xs text-indigo-800">
                  Collect user feedback, recompile with 50+ new examples to improve accuracy over time
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">100</div>
              <div className="text-xs text-slate-600">Training Examples</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">300-600</div>
              <div className="text-xs text-slate-600">LLM Calls</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">$0.50</div>
              <div className="text-xs text-slate-600">Training Cost</div>
            </div>
            <div className="text-center rounded-xl border border-slate-200 bg-slate-50 p-4">
              <div className="text-2xl font-bold text-slate-900">50+</div>
              <div className="text-xs text-slate-600">Feedback for Recompile</div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Stack */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
        <div className="border-b border-slate-200 bg-gradient-to-r from-slate-50 to-slate-100 px-8 py-6">
          <h3 className="text-xl font-semibold text-slate-900">Technology Stack</h3>
        </div>
        <div className="p-8">
          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            <div className="text-center">
              <div className="mb-2 text-sm font-semibold text-slate-900">Framework</div>
              <div className="text-xs text-slate-600">FastAPI + DSPy</div>
            </div>
            <div className="text-center">
              <div className="mb-2 text-sm font-semibold text-slate-900">LLM Model</div>
              <div className="text-xs text-slate-600">GPT-4o-mini</div>
            </div>
            <div className="text-center">
              <div className="mb-2 text-sm font-semibold text-slate-900">Retrieval</div>
              <div className="text-xs text-slate-600">External API (Port 8000)</div>
            </div>
            <div className="text-center">
              <div className="mb-2 text-sm font-semibold text-slate-900">Storage</div>
              <div className="text-xs text-slate-600">JSONL Feedback</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
