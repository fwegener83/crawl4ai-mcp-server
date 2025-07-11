# Deployment Guide

This guide covers deployment options and best practices for running the Crawl4AI MCP Server in production environments.

## Overview

The Crawl4AI MCP Server is designed for production deployment with the following characteristics:

- **Async Architecture**: Built on FastMCP for high-performance async operations
- **Resource Efficient**: Minimal memory footprint and CPU usage
- **Scalable**: Handles concurrent requests efficiently
- **Robust**: Comprehensive error handling and recovery
- **Secure**: Built-in security features and validation

## Deployment Options

### 1. Direct Python Deployment

#### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+
- **Python**: 3.10 or higher
- **Memory**: 512MB minimum, 2GB recommended
- **CPU**: 1 core minimum, 2+ cores recommended
- **Disk**: 1GB for dependencies and cache

#### Installation Steps

```bash
# Clone repository
git clone <repository-url>
cd crawl4ai-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install uv
uv install

# Install Playwright browsers
playwright install

# Run server
python server.py
```

#### Process Management

Use a process manager for production:

**systemd (Linux)**:
```ini
# /etc/systemd/system/crawl4ai-mcp.service
[Unit]
Description=Crawl4AI MCP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/crawl4ai-mcp-server
Environment=PATH=/opt/crawl4ai-mcp-server/venv/bin
ExecStart=/opt/crawl4ai-mcp-server/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**supervisord**:
```ini
# /etc/supervisor/conf.d/crawl4ai-mcp.conf
[program:crawl4ai-mcp]
command=/opt/crawl4ai-mcp-server/venv/bin/python server.py
directory=/opt/crawl4ai-mcp-server
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/crawl4ai-mcp.log
```

### 2. Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv install --frozen

# Install Playwright browsers
RUN playwright install --with-deps

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (if needed for HTTP transport)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import asyncio; from server import mcp; from fastmcp import Client; asyncio.run(Client(mcp).list_tools())"

# Run server
CMD ["python", "server.py"]
```

#### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  crawl4ai-mcp:
    build: .
    restart: unless-stopped
    environment:
      - CRAWL4AI_USER_AGENT=ProductionBot/1.0
      - CRAWL4AI_TIMEOUT=30
    volumes:
      - ./logs:/app/logs
      - ./cache:/app/cache
    ports:
      - "8000:8000"  # If using HTTP transport
    healthcheck:
      test: ["CMD", "python", "-c", "import asyncio; from server import mcp; from fastmcp import Client; asyncio.run(Client(mcp).list_tools())"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
```

#### Build and Run

```bash
# Build image
docker build -t crawl4ai-mcp-server .

# Run container
docker run -d \
    --name crawl4ai-mcp \
    --restart unless-stopped \
    -e CRAWL4AI_USER_AGENT="ProductionBot/1.0" \
    -e CRAWL4AI_TIMEOUT=30 \
    -v $(pwd)/logs:/app/logs \
    -v $(pwd)/cache:/app/cache \
    crawl4ai-mcp-server

# With docker-compose
docker-compose up -d
```

### 3. Kubernetes Deployment

#### Deployment Configuration

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: crawl4ai-mcp-server
  labels:
    app: crawl4ai-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: crawl4ai-mcp-server
  template:
    metadata:
      labels:
        app: crawl4ai-mcp-server
    spec:
      containers:
      - name: crawl4ai-mcp
        image: crawl4ai-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: CRAWL4AI_USER_AGENT
          value: "ProductionBot/1.0"
        - name: CRAWL4AI_TIMEOUT
          value: "30"
        resources:
          limits:
            memory: "1Gi"
            cpu: "1000m"
          requests:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import asyncio; from server import mcp; from fastmcp import Client; asyncio.run(Client(mcp).list_tools())"
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import asyncio; from server import mcp; from fastmcp import Client; asyncio.run(Client(mcp).list_tools())"
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: cache
          mountPath: /app/cache
      volumes:
      - name: logs
        emptyDir: {}
      - name: cache
        emptyDir: {}
```

#### Service Configuration

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: crawl4ai-mcp-service
spec:
  selector:
    app: crawl4ai-mcp-server
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

#### ConfigMap for Configuration

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: crawl4ai-mcp-config
data:
  CRAWL4AI_USER_AGENT: "ProductionBot/1.0"
  CRAWL4AI_TIMEOUT: "30"
```

#### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/crawl4ai-mcp-server
```

## Configuration

### Environment Variables

```bash
# Core configuration
CRAWL4AI_USER_AGENT="ProductionBot/1.0"
CRAWL4AI_TIMEOUT="30"

# Optional: Custom configuration
CRAWL4AI_HEADERS='{"Accept": "text/html,application/xhtml+xml"}'
CRAWL4AI_PROXY="http://proxy.example.com:8080"

# Logging configuration
LOG_LEVEL="INFO"
LOG_FORMAT="json"
LOG_FILE="/var/log/crawl4ai-mcp.log"

# Performance tuning
MAX_CONCURRENT_REQUESTS="50"
REQUEST_TIMEOUT="30"
CONNECTION_POOL_SIZE="100"
```

### Configuration File

Create a `.env` file for persistent configuration:

```env
# Production configuration
CRAWL4AI_USER_AGENT=ProductionBot/1.0
CRAWL4AI_TIMEOUT=30
LOG_LEVEL=INFO
LOG_FORMAT=json
MAX_CONCURRENT_REQUESTS=50
```

### Advanced Configuration

For advanced use cases, modify the server configuration:

```python
# server_config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Crawl4AI settings
    USER_AGENT = os.getenv("CRAWL4AI_USER_AGENT", "Crawl4AI-MCP-Server/1.0")
    TIMEOUT = int(os.getenv("CRAWL4AI_TIMEOUT", "30"))
    
    # Performance settings
    MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_REQUESTS", "50"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "text")
    LOG_FILE = os.getenv("LOG_FILE", None)
```

## Security Considerations

### Network Security

1. **Firewall Configuration**:
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 8000/tcp  # MCP server (if using HTTP)
ufw enable
```

2. **SSL/TLS Configuration**:
```bash
# Use reverse proxy with SSL
# Example with nginx:
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_private_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Application Security

1. **Input Validation**: All URLs are validated before processing
2. **Rate Limiting**: Built-in protection against abuse
3. **Error Sanitization**: No sensitive information in error messages
4. **Resource Limits**: Prevents resource exhaustion attacks

### Security Hardening

```bash
# Create dedicated user
useradd -r -s /bin/false crawl4ai

# Set proper permissions
chown -R crawl4ai:crawl4ai /opt/crawl4ai-mcp-server
chmod 750 /opt/crawl4ai-mcp-server

# Secure configuration files
chmod 600 /opt/crawl4ai-mcp-server/.env
```

## Monitoring and Observability

### Logging

Configure structured logging:

```python
# logging_config.py
import logging
import logging.handlers
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        return json.dumps(log_entry)

# Configure logging
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        '/var/log/crawl4ai-mcp.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
```

### Metrics Collection

Implement metrics collection:

```python
# metrics.py
import time
import psutil
from collections import defaultdict

class Metrics:
    def __init__(self):
        self.request_count = defaultdict(int)
        self.request_duration = defaultdict(list)
        self.error_count = defaultdict(int)
    
    def record_request(self, duration, status):
        self.request_count[status] += 1
        self.request_duration[status].append(duration)
    
    def record_error(self, error_type):
        self.error_count[error_type] += 1
    
    def get_metrics(self):
        process = psutil.Process()
        return {
            'requests': dict(self.request_count),
            'errors': dict(self.error_count),
            'memory_mb': process.memory_info().rss / 1024 / 1024,
            'cpu_percent': process.cpu_percent(),
            'timestamp': time.time()
        }
```

### Health Checks

Implement comprehensive health checks:

```python
# health.py
import asyncio
import time
from fastmcp import Client
from server import mcp

class HealthChecker:
    def __init__(self):
        self.last_check = None
        self.check_interval = 30  # seconds
    
    async def check_health(self):
        try:
            # Test basic connectivity
            async with Client(mcp) as client:
                tools = await client.list_tools()
                
                if len(tools) != 1:
                    return {'status': 'unhealthy', 'reason': 'tool registration failed'}
                
                # Test tool execution
                start_time = time.time()
                result = await client.call_tool_mcp("web_content_extract", {
                    "url": "https://httpbin.org/html"
                })
                duration = time.time() - start_time
                
                if result.isError:
                    return {'status': 'unhealthy', 'reason': 'tool execution failed'}
                
                return {
                    'status': 'healthy',
                    'response_time': duration,
                    'timestamp': time.time()
                }
                
        except Exception as e:
            return {'status': 'unhealthy', 'reason': str(e)}
    
    async def continuous_health_check(self):
        while True:
            health = await self.check_health()
            print(f"Health check: {health}")
            await asyncio.sleep(self.check_interval)
```

### Monitoring Integration

#### Prometheus Integration

```python
# prometheus_metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
REQUEST_COUNT = Counter('crawl4ai_requests_total', 'Total requests', ['status'])
REQUEST_DURATION = Histogram('crawl4ai_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('crawl4ai_active_connections', 'Active connections')
MEMORY_USAGE = Gauge('crawl4ai_memory_usage_bytes', 'Memory usage')

def setup_prometheus_metrics():
    start_http_server(9090)  # Metrics endpoint on port 9090
    
def record_request(duration, status):
    REQUEST_COUNT.labels(status=status).inc()
    REQUEST_DURATION.observe(duration)
```

#### Grafana Dashboard

Create a Grafana dashboard to visualize metrics:

```json
{
  "dashboard": {
    "title": "Crawl4AI MCP Server",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(crawl4ai_requests_total[5m])",
            "legendFormat": "RPS"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "crawl4ai_request_duration_seconds",
            "legendFormat": "Duration"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "crawl4ai_memory_usage_bytes",
            "legendFormat": "Memory"
          }
        ]
      }
    ]
  }
}
```

## Performance Tuning

### System-Level Optimizations

```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize TCP settings
echo "net.core.somaxconn = 1024" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 1024" >> /etc/sysctl.conf
sysctl -p
```

### Application-Level Optimizations

```python
# performance_config.py
import asyncio
from crawl4ai import AsyncWebCrawler

class PerformanceConfig:
    # Connection pool settings
    MAX_CONNECTIONS = 100
    MAX_CONNECTIONS_PER_HOST = 20
    
    # Timeout settings
    CONNECT_TIMEOUT = 10
    REQUEST_TIMEOUT = 30
    
    # Crawler settings
    CONCURRENT_CRAWLS = 10
    
    @staticmethod
    async def create_optimized_crawler():
        return AsyncWebCrawler(
            max_connections=PerformanceConfig.MAX_CONNECTIONS,
            max_connections_per_host=PerformanceConfig.MAX_CONNECTIONS_PER_HOST,
            timeout=PerformanceConfig.REQUEST_TIMEOUT
        )
```

### Resource Limits

Set appropriate resource limits:

```bash
# systemd service limits
[Service]
LimitNOFILE=65536
LimitNPROC=32768
MemoryMax=2G
CPUQuota=200%
```

## Backup and Recovery

### Configuration Backup

```bash
#!/bin/bash
# backup_config.sh
BACKUP_DIR="/backup/crawl4ai-mcp"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
cp /opt/crawl4ai-mcp-server/.env $BACKUP_DIR/env_$DATE
cp /opt/crawl4ai-mcp-server/pyproject.toml $BACKUP_DIR/pyproject_$DATE.toml

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz /var/log/crawl4ai-mcp.log*

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Disaster Recovery

```bash
#!/bin/bash
# disaster_recovery.sh
BACKUP_DIR="/backup/crawl4ai-mcp"
RESTORE_DATE=$1

if [ -z "$RESTORE_DATE" ]; then
    echo "Usage: $0 <YYYYMMDD_HHMMSS>"
    exit 1
fi

# Stop service
systemctl stop crawl4ai-mcp

# Restore configuration
cp $BACKUP_DIR/env_$RESTORE_DATE /opt/crawl4ai-mcp-server/.env
cp $BACKUP_DIR/pyproject_$RESTORE_DATE.toml /opt/crawl4ai-mcp-server/pyproject.toml

# Restore logs if needed
tar -xzf $BACKUP_DIR/logs_$RESTORE_DATE.tar.gz -C /

# Start service
systemctl start crawl4ai-mcp
```

## Troubleshooting

### Common Deployment Issues

1. **Port Conflicts**:
```bash
# Check port usage
netstat -tlnp | grep :8000
lsof -i :8000

# Kill conflicting processes
kill -9 <PID>
```

2. **Permission Issues**:
```bash
# Fix permissions
chown -R crawl4ai:crawl4ai /opt/crawl4ai-mcp-server
chmod +x /opt/crawl4ai-mcp-server/server.py
```

3. **Dependencies Issues**:
```bash
# Reinstall dependencies
uv install --reinstall
playwright install --force
```

### Performance Issues

1. **High Memory Usage**:
```bash
# Monitor memory
top -p $(pgrep -f "python server.py")
htop -p $(pgrep -f "python server.py")
```

2. **High CPU Usage**:
```bash
# Check CPU usage
perf top -p $(pgrep -f "python server.py")
```

3. **Connection Issues**:
```bash
# Check connections
netstat -an | grep :8000
ss -tuln | grep :8000
```

### Log Analysis

```bash
# View recent logs
tail -f /var/log/crawl4ai-mcp.log

# Search for errors
grep -i error /var/log/crawl4ai-mcp.log

# Analyze request patterns
grep "Extracting content" /var/log/crawl4ai-mcp.log | awk '{print $1}' | sort | uniq -c
```

## Best Practices

### Security Best Practices

1. **Regular Updates**: Keep dependencies up to date
2. **Security Scanning**: Regularly scan for vulnerabilities
3. **Access Control**: Limit network access to the server
4. **Monitoring**: Monitor for unusual activity patterns
5. **Backup**: Regular configuration and data backups

### Performance Best Practices

1. **Resource Monitoring**: Monitor CPU, memory, and network usage
2. **Load Testing**: Regular load testing to identify bottlenecks
3. **Caching**: Implement caching for frequently accessed URLs
4. **Connection Pooling**: Use connection pooling for better performance
5. **Graceful Degradation**: Implement graceful degradation under load

### Operational Best Practices

1. **Automation**: Automate deployment and scaling
2. **Documentation**: Maintain deployment documentation
3. **Testing**: Test deployments in staging environments
4. **Rollback Plans**: Have rollback procedures ready
5. **Monitoring**: Comprehensive monitoring and alerting

## Scaling

### Horizontal Scaling

Deploy multiple instances behind a load balancer:

```yaml
# docker-compose.yml for scaling
version: '3.8'
services:
  crawl4ai-mcp:
    build: .
    deploy:
      replicas: 3
    environment:
      - CRAWL4AI_USER_AGENT=ProductionBot/1.0
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - crawl4ai-mcp
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Vertical Scaling

Increase resources for single instance:

```yaml
# docker-compose.yml for vertical scaling
services:
  crawl4ai-mcp:
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '4.0'
        reservations:
          memory: 2G
          cpus: '2.0'
```

### Auto-scaling

Implement auto-scaling based on metrics:

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: crawl4ai-mcp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: crawl4ai-mcp-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

This deployment guide provides comprehensive instructions for deploying the Crawl4AI MCP Server in various environments, from development to production-scale deployments.