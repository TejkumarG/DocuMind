#!/bin/bash

# AI Architecture - Helper Scripts
# Convenience commands for Docker operations

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Help message
show_help() {
    cat << EOF
${BLUE}AI Architecture - Docker Helper Scripts${NC}

Usage: ./scripts.sh [COMMAND]

${GREEN}Service Management:${NC}
  start               Start all core services (RAG, Reasoning, UI, Milvus)
  start-all           Start all services including monitoring and PDF tools
  start-monitoring    Start core services + Attu monitoring GUI
  start-pdf           Start core services + PDF converter
  stop                Stop all services
  restart             Restart all services
  status              Show status of all services

${GREEN}PDF Converter:${NC}
  pdf-convert         Run PDF to Markdown converter
  pdf-shell           Open shell in PDF converter container
  pdf-logs            Show PDF converter logs

${GREEN}Logs & Monitoring:${NC}
  logs [service]      Show logs for specific service (or all if none specified)
  health              Check health of all services

${GREEN}Maintenance:${NC}
  build               Rebuild all services
  clean               Stop services and remove volumes
  reset               Complete reset (removes containers, volumes, networks)

${GREEN}Examples:${NC}
  ./scripts.sh start
  ./scripts.sh pdf-convert
  ./scripts.sh logs rag-service
  ./scripts.sh health

EOF
}

# Start core services
start_core() {
    print_info "Starting core services (RAG, Reasoning, UI, Milvus)..."
    docker-compose up -d
    print_success "Core services started!"
    print_info "Access points:"
    echo "  - UI: http://localhost:3000"
    echo "  - RAG API: http://localhost:8000"
    echo "  - Reasoning API: http://localhost:8001"
    echo "  - Milvus: localhost:19530"
}

# Start all services
start_all() {
    print_info "Starting all services..."
    docker-compose --profile monitoring --profile pdf-tools up -d
    print_success "All services started!"
    print_info "Access points:"
    echo "  - UI: http://localhost:3000"
    echo "  - RAG API: http://localhost:8000"
    echo "  - Reasoning API: http://localhost:8001"
    echo "  - Milvus: localhost:19530"
    echo "  - Attu GUI: http://localhost:3001"
}

# Start with monitoring
start_monitoring() {
    print_info "Starting services with monitoring..."
    docker-compose --profile monitoring up -d
    print_success "Services started with monitoring!"
    print_info "Attu GUI available at: http://localhost:3001"
}

# Start with PDF tools
start_pdf() {
    print_info "Starting services with PDF tools..."
    docker-compose --profile pdf-tools up -d
    print_success "Services started with PDF tools!"
}

# Stop services
stop_services() {
    print_info "Stopping all services..."
    docker-compose --profile monitoring --profile pdf-tools down
    print_success "All services stopped!"
}

# Restart services
restart_services() {
    print_info "Restarting services..."
    docker-compose --profile monitoring --profile pdf-tools restart
    print_success "Services restarted!"
}

# Show status
show_status() {
    print_info "Service Status:"
    docker-compose ps
}

# PDF Converter - Run conversion
pdf_convert() {
    print_info "Starting PDF converter..."

    # Check if pdf-converter is running
    if ! docker ps | grep -q "pdf-to-md"; then
        print_warning "PDF converter not running, starting it..."
        docker-compose --profile pdf-tools up -d pdf-converter
        sleep 3
    fi

    print_info "Running PDF conversion..."
    print_warning "Make sure your PDFs are in ./pdf-to-md/data/ directory"
    docker exec -it pdf-to-md python main.py
    print_success "PDF conversion completed!"
}

# PDF Converter - Shell access
pdf_shell() {
    print_info "Opening shell in PDF converter..."

    if ! docker ps | grep -q "pdf-to-md"; then
        print_error "PDF converter not running. Start it first with: ./scripts.sh start-pdf"
        exit 1
    fi

    docker exec -it pdf-to-md bash
}

# PDF Converter - Logs
pdf_logs() {
    print_info "Showing PDF converter logs..."
    docker-compose logs -f pdf-converter
}

# Show logs
show_logs() {
    if [ -z "$1" ]; then
        print_info "Showing logs for all services..."
        docker-compose logs -f
    else
        print_info "Showing logs for $1..."
        docker-compose logs -f "$1"
    fi
}

# Health check
health_check() {
    print_info "Checking service health..."
    echo ""

    # Check RAG Service
    if curl -s http://localhost:8000/ > /dev/null; then
        print_success "RAG Service (8000): Healthy"
    else
        print_error "RAG Service (8000): Unhealthy"
    fi

    # Check Reasoning Service
    if curl -s http://localhost:8001/ > /dev/null; then
        print_success "Reasoning Service (8001): Healthy"
    else
        print_error "Reasoning Service (8001): Unhealthy"
    fi

    # Check UI
    if curl -s http://localhost:3000/ > /dev/null; then
        print_success "UI (3000): Healthy"
    else
        print_error "UI (3000): Unhealthy"
    fi

    # Check Milvus
    if curl -s http://localhost:9091/healthz > /dev/null; then
        print_success "Milvus (19530): Healthy"
    else
        print_error "Milvus (19530): Unhealthy"
    fi

    echo ""
}

# Build services
build_services() {
    print_info "Building all services..."
    docker-compose build
    print_success "Build completed!"
}

# Clean up
clean_up() {
    print_warning "This will stop services and remove volumes. Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Cleaning up..."
        docker-compose --profile monitoring --profile pdf-tools down -v
        print_success "Cleanup completed!"
    else
        print_info "Cleanup cancelled."
    fi
}

# Complete reset
reset_all() {
    print_error "⚠️  WARNING: This will remove all containers, volumes, and networks!"
    print_warning "Continue? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_info "Performing complete reset..."
        docker-compose --profile monitoring --profile pdf-tools down -v --remove-orphans
        docker network prune -f
        print_success "Reset completed!"
    else
        print_info "Reset cancelled."
    fi
}

# Main command handler
case "$1" in
    start)
        start_core
        ;;
    start-all)
        start_all
        ;;
    start-monitoring)
        start_monitoring
        ;;
    start-pdf)
        start_pdf
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    pdf-convert)
        pdf_convert
        ;;
    pdf-shell)
        pdf_shell
        ;;
    pdf-logs)
        pdf_logs
        ;;
    logs)
        show_logs "$2"
        ;;
    health)
        health_check
        ;;
    build)
        build_services
        ;;
    clean)
        clean_up
        ;;
    reset)
        reset_all
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
