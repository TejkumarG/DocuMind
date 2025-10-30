# AI Architecture Showcase

Professional Next.js frontend showcasing enterprise-grade AI infrastructure with stunning architecture visualizations.

## Features

### 3 Production-Ready AI Systems

1. **DSPy RAG Pipeline**
   - Two-stage Reason + Verify architecture
   - OpenAI GPT-4o-mini integration
   - 2 LLM calls per query
   - < $0.001 cost per query
   - FastAPI backend with DSPy framework

2. **Hybrid RAG Pipeline**
   - Semantic search + Entity matching
   - Milvus vector database
   - 384-dim embeddings (Sentence Transformer)
   - spaCy NER for entity extraction
   - Parallel dual-path retrieval

3. **Intelligent PDF Processing**
   - Vision-based table detection
   - Smart routing (PyMuPDF vs OpenAI Vision)
   - 90% detection accuracy
   - Cost-optimized ($0.004/page for complex PDFs)
   - Parallel processing with ThreadPool

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Deployment**: Docker

## Quick Start

### Development Mode

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Production Mode (Docker)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f ui

# Stop container
docker-compose down
```

### Build for Production

```bash
# Build optimized production bundle
npm run build

# Start production server
npm start
```

## Project Structure

```
ui/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Main landing page
│   └── globals.css         # Global styles
├── components/
│   ├── ReasoningArchitecture.tsx      # DSPy RAG visualization
│   ├── RAGPipelineArchitecture.tsx    # Hybrid search visualization
│   └── PDFProcessingArchitecture.tsx  # PDF processing visualization
├── public/                 # Static assets
├── Dockerfile             # Production container
├── docker-compose.yml     # Docker orchestration
└── package.json           # Dependencies
```

## Architecture Visualizations

### 1. DSPy RAG Pipeline
- **Request Flow**: User → Context Retrieval → Reason (LLM #1) → Verify (LLM #2)
- **Key Metrics**: 2 LLM calls, 2-4s latency, < $0.001/query
- **Tech**: FastAPI, DSPy, OpenAI GPT-4o-mini
- **Features**: Feedback loop, optional compilation, health checks

### 2. Hybrid RAG Pipeline
- **Dual Path**: Semantic Search + Entity Matching (parallel)
- **Models**: Sentence Transformer (all-MiniLM-L6-v2), spaCy NER (en_core_web_md)
- **Database**: Milvus (IVF_FLAT, L2 distance)
- **Output**: 3-6 deduplicated chunks, ranked by similarity

### 3. PDF Processing
- **Phase 1**: Vision-based table detection (first 5 pages)
- **Phase 2**: Smart routing
  - No tables → PyMuPDF4LLM (free, fast)
  - Has tables → OpenAI Vision (accurate, paid)
- **Cost**: Free for simple PDFs, $0.004/page for complex ones
- **Accuracy**: 90% confidence threshold, no false positives

## Design Features

- **Modern UI**: Gradient backgrounds, glassmorphism effects
- **Responsive**: Mobile-first design, works on all devices
- **Animations**: Smooth fade-in effects, hover states
- **Professional**: Clean typography, consistent spacing
- **Accessible**: Semantic HTML, proper contrast ratios
- **Performance**: Optimized build, lazy loading

## Coming Soon

- **Interactive Chat Interface**: Query your documents in real-time
- **Live Demos**: Try each system with sample data
- **Performance Metrics**: Real-time monitoring dashboard
- **API Playground**: Test endpoints directly from UI

## Environment Variables

Create a `.env.local` file (optional):

```bash
# Add any environment-specific variables here
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

Enterprise AI Infrastructure © 2024

---

## Screenshots

The application features:
- Clean, professional landing page
- Three stunning architecture visualizations
- Color-coded system components
- Interactive hover effects
- Responsive grid layouts
- Performance metrics display

Perfect for demos, presentations, and showcasing your AI infrastructure to stakeholders.

## Support

For questions or issues, please refer to the individual project documentation:
- `/reasoning/ARCHITECTURE.md` - DSPy RAG Pipeline
- `/rag-pipeline/ARCHITECTURE_FLOW.md` - Hybrid RAG System
- `/pdf-to-md/README.md` - PDF Processing System
