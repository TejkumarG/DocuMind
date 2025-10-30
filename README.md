# AI Architecture - Unified Docker Setup

This project contains multiple independent services orchestrated with Docker Compose.

## Architecture Overview

### Services

1. **RAG Service** (FastAPI) - Port 8000
   - Vector database operations
   - Document ingestion and retrieval
   - Connects to Milvus

2. **Reasoning Service** (FastAPI) - Port 8001
   - AI reasoning and decision making
   - Connects to RAG Service for context retrieval

3. **UI Service** (React/Node) - Port 3000
   - User interface
   - Connects to both APIs

4. **Milvus Vector Database** (3 containers)
   - `milvus-standalone` - Main database (Port 19530, 9091)
   - `milvus-etcd` - Metadata storage
   - `milvus-minio` - Object storage

5. **PDF-to-MD Converter** (Utility)
   - Runs via exec command
   - No exposed ports
   - Use profile: `pdf-tools`

### Optional Services

6. **Attu** - Milvus Management GUI (Port 3001)
   - Use profile: `monitoring`

## Quick Start

### Start All Core Services
```bash
docker-compose up -d
```

### Start with Monitoring (includes Attu GUI)
```bash
docker-compose --profile monitoring up -d
```

### Start with PDF Tools
```bash
docker-compose --profile pdf-tools up -d
```

### Start Everything
```bash
docker-compose --profile monitoring --profile pdf-tools up -d
```

## Using PDF-to-MD Service

The PDF converter runs as a utility service. To use it:

```bash
# Start the service
docker-compose --profile pdf-tools up -d pdf-converter

# Execute conversion command
docker exec -it pdf-to-md python src/main.py --input /app/data/input.pdf --output /app/data/output.md

# Or use interactive mode
docker exec -it pdf-to-md bash
```

## Service Dependencies

```
milvus-etcd → milvus-minio → milvus-standalone → rag-service → reasoning-api → ui
                                                ↓
                                              attu
```

## Environment Files

Ensure these environment files exist:
- `./reasoning/.env` - Reasoning service config
- `./pdf-to-md/.env` - PDF converter config
- `./ui/.env.local` - UI config (optional)

## Network

All services run on a shared network: `ai-architecture-network`

Services can communicate using container names:
- `http://rag-service:8000`
- `http://reasoning-api:8001`
- `http://milvus-standalone:19530`

## Volumes

Persistent data is stored in named volumes:
- `milvus_etcd` - Milvus metadata
- `milvus_minio` - Milvus object storage
- `milvus_data` - Milvus vector data

## Useful Commands

```bash
# View logs
docker-compose logs -f [service-name]

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Rebuild a service
docker-compose build [service-name]

# Check service status
docker-compose ps

# Scale services (if needed)
docker-compose up -d --scale rag-service=2
```

## Health Checks

- RAG Service: http://localhost:8000/
- Reasoning Service: http://localhost:8001/
- Milvus: http://localhost:9091/healthz
- UI: http://localhost:3000

## Troubleshooting

### Services not connecting
- Check network: `docker network ls`
- Inspect network: `docker network inspect ai-architecture-network`

### Milvus not starting
- Check dependencies: `docker-compose ps`
- Ensure etcd and minio are healthy first

### Port conflicts
- Check if ports are already in use: `lsof -i :<port>`
- Modify port mappings in docker-compose.yml

## Development

### Hot-Reload Development Mode

For faster UI development without full rebuilds:

```bash
# Start services in development mode (with hot-reload)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Or just rebuild UI in dev mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build ui
```

**Benefits:**
- Instant UI updates without rebuilding (source code mounted as volume)
- Next.js hot-reload enabled
- No need to rebuild for small CSS/component changes
- Reasoning API already has auto-reload enabled

### Production Mode (Current)

For production builds:
```bash
# Full rebuild (takes 1-2 minutes)
docker-compose build ui
docker-compose up -d ui
```

**Note:**
- Reasoning API: Already configured with `--reload` for development
- RAG Service: Restart required for code changes
- Other services: Mount source directories as volumes for hot-reload

## Production Notes

- Set `NODE_ENV=production` for UI
- Remove volume mounts for source code
- Use proper secrets management
- Configure resource limits
- Set up proper logging
