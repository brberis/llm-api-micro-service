#!/bin/bash

# Heidi LLM Service Management Script

set -e

PROJECT_NAME="heidi-llm"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_requirements() {
    log_info "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "Docker and Docker Compose are available"
}

# Build the service
build_service() {
    log_info "Building Heidi LLM service..."
    docker-compose build
    log_success "Service built successfully"
}

# Start the service
start_service() {
    log_info "Starting Heidi LLM service..."
    docker-compose up -d
    
    log_info "Waiting for service to be ready..."
    sleep 10
    
    # Wait for health check
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            log_success "Service is healthy and ready!"
            break
        fi
        
        log_info "Attempt $attempt/$max_attempts - Service not ready yet, waiting..."
        sleep 10
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        log_error "Service failed to start within expected time"
        docker-compose logs
        exit 1
    fi
}

# Stop the service
stop_service() {
    log_info "Stopping Heidi LLM service..."
    docker-compose down
    log_success "Service stopped"
}

# Restart the service
restart_service() {
    stop_service
    start_service
}

# View logs
view_logs() {
    docker-compose logs -f
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    # Check if service is running
    if ! curl -f http://localhost:8000/health &> /dev/null; then
        log_error "Service is not running. Please start the service first."
        exit 1
    fi
    
    python3 test_client.py
}

# Show status
show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    echo ""
    log_info "Health Check:"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Service not responding"
}

# Show usage
show_usage() {
    echo "Heidi LLM Service Manager"
    echo ""
    echo "Usage: $0 {start|stop|restart|build|logs|test|status|help}"
    echo ""
    echo "Commands:"
    echo "  start     - Start the LLM service"
    echo "  stop      - Stop the LLM service"
    echo "  restart   - Restart the LLM service"
    echo "  build     - Build the Docker image"
    echo "  logs      - View service logs"
    echo "  test      - Run test client"
    echo "  status    - Show service status"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start          # Start the service"
    echo "  $0 test           # Run tests"
    echo "  $0 logs           # View logs"
}

# Main script logic
case "${1:-help}" in
    "start")
        check_requirements
        start_service
        ;;
    "stop")
        stop_service
        ;;
    "restart")
        check_requirements
        restart_service
        ;;
    "build")
        check_requirements
        build_service
        ;;
    "logs")
        view_logs
        ;;
    "test")
        run_tests
        ;;
    "status")
        show_status
        ;;
    "help"|*)
        show_usage
        ;;
esac
