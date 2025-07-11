# Maintenance Guide

This guide covers ongoing maintenance tasks, troubleshooting procedures, and best practices for keeping the Crawl4AI MCP Server running smoothly in production.

## Overview

Regular maintenance is essential for:
- **Performance**: Maintaining optimal response times and throughput
- **Security**: Keeping the system secure with updates and monitoring
- **Reliability**: Preventing issues before they impact users
- **Cost Management**: Optimizing resource usage and costs

## Daily Maintenance Tasks

### 1. System Health Checks

**Automated Health Monitoring**:
```bash
#!/bin/bash
# daily_health_check.sh

# Check service status
systemctl is-active crawl4ai-mcp-server || echo "Service is not running"

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.2f", $3/$2 * 100}')
echo "Memory usage: ${MEMORY_USAGE}%"

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
echo "Disk usage: ${DISK_USAGE}%"

# Check recent errors
ERROR_COUNT=$(grep -c "ERROR" /var/log/crawl4ai-mcp.log | tail -n 1000)
echo "Recent errors: $ERROR_COUNT"

# Alert if thresholds exceeded
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "ALERT: High memory usage: ${MEMORY_USAGE}%"
fi

if (( $DISK_USAGE > 90 )); then
    echo "ALERT: High disk usage: ${DISK_USAGE}%"
fi

if (( $ERROR_COUNT > 10 )); then
    echo "ALERT: High error rate: $ERROR_COUNT errors"
fi
```

### 2. Log Analysis

**Daily Log Review**:
```bash
#!/bin/bash
# daily_log_analysis.sh

LOG_FILE="/var/log/crawl4ai-mcp.log"
TODAY=$(date +%Y-%m-%d)

echo "=== Daily Log Summary for $TODAY ==="

# Count requests by status
echo "Request Summary:"
grep "$TODAY" $LOG_FILE | grep "Extracting content" | wc -l | xargs echo "Total requests:"
grep "$TODAY" $LOG_FILE | grep "Successfully extracted" | wc -l | xargs echo "Successful extractions:"
grep "$TODAY" $LOG_FILE | grep "ERROR" | wc -l | xargs echo "Errors:"

# Most common errors
echo -e "\nTop 5 Error Types:"
grep "$TODAY" $LOG_FILE | grep "ERROR" | awk '{print $NF}' | sort | uniq -c | sort -nr | head -5

# Performance metrics
echo -e "\nPerformance Metrics:"
grep "$TODAY" $LOG_FILE | grep "Successfully extracted" | \
    awk '{print $(NF-1)}' | sed 's/[^0-9]//g' | \
    awk '{sum+=$1; count++} END {if(count>0) print "Average response time:", sum/count "ms"}'

# Most requested domains
echo -e "\nTop 10 Requested Domains:"
grep "$TODAY" $LOG_FILE | grep "Extracting content" | \
    awk '{print $NF}' | sed 's|https\?://||' | cut -d'/' -f1 | \
    sort | uniq -c | sort -nr | head -10
```

### 3. Performance Monitoring

**Performance Metrics Collection**:
```python
# daily_performance_check.py
import asyncio
import time
import statistics
from fastmcp import Client
from server import mcp

async def performance_check():
    """Run daily performance checks."""
    test_urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://example.com"
    ]
    
    results = {
        'response_times': [],
        'success_rate': 0,
        'error_count': 0,
        'total_requests': 0
    }
    
    async with Client(mcp) as client:
        for url in test_urls:
            for _ in range(5):  # Test each URL 5 times
                start_time = time.time()
                try:
                    result = await client.call_tool_mcp("web_content_extract", {
                        "url": url
                    })
                    response_time = time.time() - start_time
                    results['response_times'].append(response_time)
                    results['total_requests'] += 1
                    
                    if not result.isError:
                        results['success_rate'] += 1
                    else:
                        results['error_count'] += 1
                        
                except Exception as e:
                    results['error_count'] += 1
                    results['total_requests'] += 1
                    print(f"Error testing {url}: {e}")
    
    # Calculate metrics
    if results['response_times']:
        avg_response_time = statistics.mean(results['response_times'])
        p95_response_time = statistics.quantiles(results['response_times'], n=20)[18]
        success_rate = (results['success_rate'] / results['total_requests']) * 100
        
        print(f"Daily Performance Report:")
        print(f"Average Response Time: {avg_response_time:.3f}s")
        print(f"95th Percentile Response Time: {p95_response_time:.3f}s")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Total Requests: {results['total_requests']}")
        print(f"Error Count: {results['error_count']}")
        
        # Alert on performance degradation
        if avg_response_time > 0.5:
            print("ALERT: Average response time exceeds 500ms")
        
        if success_rate < 95:
            print("ALERT: Success rate below 95%")

if __name__ == "__main__":
    asyncio.run(performance_check())
```

## Weekly Maintenance Tasks

### 1. Dependency Updates

**Check for Security Updates**:
```bash
#!/bin/bash
# weekly_security_updates.sh

echo "=== Weekly Security Update Check ==="

# Check for Python security updates
pip list --outdated | grep -E "(security|vulner|cve)"

# Update dependencies with security patches
uv update --only-security

# Check for Playwright updates
playwright --version
echo "Check https://playwright.dev/python/docs/release-notes for latest version"

# Audit dependencies for vulnerabilities
pip-audit

# Update system packages (Ubuntu/Debian)
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt list --upgradable | grep -E "(security|important)"
fi
```

### 2. Database Cleanup

**Log Rotation and Cleanup**:
```bash
#!/bin/bash
# weekly_cleanup.sh

echo "=== Weekly Cleanup Tasks ==="

# Rotate logs
logrotate -f /etc/logrotate.d/crawl4ai-mcp

# Clean up old cache files
find /tmp -name "crawl4ai_*" -mtime +7 -delete
find /var/cache/crawl4ai -name "*.tmp" -mtime +7 -delete

# Clean up old backup files
find /backup/crawl4ai-mcp -name "*.tar.gz" -mtime +30 -delete

# Clear browser cache (if using Playwright)
find ~/.cache/ms-playwright -name "*.tmp" -mtime +7 -delete

# Check disk space after cleanup
df -h
```

### 3. Performance Analysis

**Weekly Performance Report**:
```python
# weekly_performance_analysis.py
import json
import statistics
from datetime import datetime, timedelta
from collections import defaultdict

class WeeklyPerformanceAnalyzer:
    def __init__(self, log_file="/var/log/crawl4ai-mcp.log"):
        self.log_file = log_file
        self.metrics = defaultdict(list)
        
    def parse_logs(self):
        """Parse logs for the last week."""
        one_week_ago = datetime.now() - timedelta(days=7)
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    # Parse timestamp and check if within last week
                    timestamp_str = line.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    
                    if timestamp >= one_week_ago:
                        self.parse_line(line, timestamp)
                except Exception as e:
                    continue
    
    def parse_line(self, line, timestamp):
        """Parse individual log line."""
        if "Successfully extracted" in line:
            # Extract response time
            try:
                chars = line.split("Successfully extracted ")[1].split(" characters")[0]
                if chars.isdigit():
                    day = timestamp.strftime('%Y-%m-%d')
                    self.metrics['daily_requests'][day] += 1
            except:
                pass
                
        elif "ERROR" in line:
            day = timestamp.strftime('%Y-%m-%d')
            self.metrics['daily_errors'][day] += 1
    
    def generate_report(self):
        """Generate weekly performance report."""
        report = {
            'period': f"{datetime.now() - timedelta(days=7):%Y-%m-%d} to {datetime.now():%Y-%m-%d}",
            'summary': {}
        }
        
        # Calculate totals
        total_requests = sum(self.metrics['daily_requests'].values())
        total_errors = sum(self.metrics['daily_errors'].values())
        
        if total_requests > 0:
            error_rate = (total_errors / total_requests) * 100
            avg_daily_requests = total_requests / 7
            
            report['summary'] = {
                'total_requests': total_requests,
                'total_errors': total_errors,
                'error_rate': f"{error_rate:.2f}%",
                'avg_daily_requests': f"{avg_daily_requests:.0f}",
                'uptime': self.calculate_uptime()
            }
        
        return report
    
    def calculate_uptime(self):
        """Calculate system uptime percentage."""
        # Simplified uptime calculation
        # In practice, this would check service restarts and downtime
        return "99.9%"  # Placeholder
    
    def print_report(self):
        """Print formatted report."""
        self.parse_logs()
        report = self.generate_report()
        
        print("=== Weekly Performance Report ===")
        print(f"Period: {report['period']}")
        print(f"Total Requests: {report['summary'].get('total_requests', 0)}")
        print(f"Total Errors: {report['summary'].get('total_errors', 0)}")
        print(f"Error Rate: {report['summary'].get('error_rate', 'N/A')}")
        print(f"Average Daily Requests: {report['summary'].get('avg_daily_requests', 'N/A')}")
        print(f"Uptime: {report['summary'].get('uptime', 'N/A')}")
        
        # Daily breakdown
        print("\n=== Daily Breakdown ===")
        for day in sorted(self.metrics['daily_requests'].keys()):
            requests = self.metrics['daily_requests'][day]
            errors = self.metrics['daily_errors'].get(day, 0)
            error_rate = (errors / requests * 100) if requests > 0 else 0
            print(f"{day}: {requests} requests, {errors} errors ({error_rate:.1f}%)")

if __name__ == "__main__":
    analyzer = WeeklyPerformanceAnalyzer()
    analyzer.print_report()
```

## Monthly Maintenance Tasks

### 1. Comprehensive System Audit

**Monthly System Audit**:
```bash
#!/bin/bash
# monthly_audit.sh

echo "=== Monthly System Audit ==="

# Check system resources
echo "System Resources:"
free -h
df -h
uptime

# Check service configuration
echo -e "\nService Configuration:"
systemctl status crawl4ai-mcp-server
systemctl show crawl4ai-mcp-server --property=CPUUsage,MemoryUsage,TasksCurrent

# Check security updates
echo -e "\nSecurity Updates:"
apt list --upgradable 2>/dev/null | grep -i security | wc -l | xargs echo "Available security updates:"

# Check certificate expiration (if using HTTPS)
echo -e "\nCertificate Status:"
if [ -f /etc/ssl/certs/crawl4ai-mcp.crt ]; then
    openssl x509 -in /etc/ssl/certs/crawl4ai-mcp.crt -noout -dates
fi

# Check backup integrity
echo -e "\nBackup Status:"
find /backup/crawl4ai-mcp -name "*.tar.gz" -mtime -30 | wc -l | xargs echo "Backups from last 30 days:"

# Check for any unusual patterns
echo -e "\nSecurity Scan:"
grep -i "failed\|error\|hack\|attack" /var/log/crawl4ai-mcp.log | tail -10
```

### 2. Capacity Planning

**Monthly Capacity Review**:
```python
# monthly_capacity_review.py
import psutil
import json
from datetime import datetime, timedelta
from collections import defaultdict

class CapacityPlanner:
    def __init__(self):
        self.metrics = defaultdict(list)
        
    def collect_system_metrics(self):
        """Collect current system metrics."""
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0],
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_trends(self):
        """Analyze resource usage trends."""
        # In practice, this would analyze historical data
        current_metrics = self.collect_system_metrics()
        
        # Simulate trend analysis
        trends = {
            'cpu_trend': 'stable',  # increasing, decreasing, stable
            'memory_trend': 'stable',
            'disk_trend': 'increasing',
            'load_trend': 'stable'
        }
        
        return {
            'current_metrics': current_metrics,
            'trends': trends,
            'recommendations': self.generate_recommendations(current_metrics, trends)
        }
    
    def generate_recommendations(self, metrics, trends):
        """Generate capacity recommendations."""
        recommendations = []
        
        if metrics['cpu_usage'] > 80:
            recommendations.append("Consider upgrading CPU or adding more instances")
        
        if metrics['memory_usage'] > 85:
            recommendations.append("Consider increasing memory allocation")
        
        if metrics['disk_usage'] > 80:
            recommendations.append("Consider increasing disk space or implementing cleanup")
        
        if trends['disk_trend'] == 'increasing':
            recommendations.append("Monitor disk usage growth and plan for expansion")
        
        if not recommendations:
            recommendations.append("System resources are within normal limits")
        
        return recommendations
    
    def print_capacity_report(self):
        """Print capacity planning report."""
        analysis = self.analyze_trends()
        
        print("=== Monthly Capacity Planning Report ===")
        print(f"Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n=== Current Resource Usage ===")
        print(f"CPU Usage: {analysis['current_metrics']['cpu_usage']:.1f}%")
        print(f"Memory Usage: {analysis['current_metrics']['memory_usage']:.1f}%")
        print(f"Disk Usage: {analysis['current_metrics']['disk_usage']:.1f}%")
        print(f"Load Average: {analysis['current_metrics']['load_average']:.2f}")
        
        print("\n=== Trends ===")
        for resource, trend in analysis['trends'].items():
            print(f"{resource.replace('_', ' ').title()}: {trend}")
        
        print("\n=== Recommendations ===")
        for i, recommendation in enumerate(analysis['recommendations'], 1):
            print(f"{i}. {recommendation}")

if __name__ == "__main__":
    planner = CapacityPlanner()
    planner.print_capacity_report()
```

### 3. Security Review

**Monthly Security Assessment**:
```bash
#!/bin/bash
# monthly_security_review.sh

echo "=== Monthly Security Review ==="

# Check for failed login attempts
echo "Failed Login Attempts:"
grep "Failed" /var/log/auth.log | tail -10

# Check for unusual network activity
echo -e "\nNetwork Connections:"
netstat -tuln | grep LISTEN

# Check file permissions
echo -e "\nCritical File Permissions:"
ls -la /opt/crawl4ai-mcp-server/server.py
ls -la /opt/crawl4ai-mcp-server/.env

# Check for unauthorized changes
echo -e "\nRecent File Changes:"
find /opt/crawl4ai-mcp-server -type f -mtime -30 -ls | head -20

# Check SSL certificate validity
echo -e "\nSSL Certificate Status:"
if [ -f /etc/ssl/certs/crawl4ai-mcp.crt ]; then
    openssl x509 -in /etc/ssl/certs/crawl4ai-mcp.crt -noout -text | grep -A 2 "Validity"
fi

# Check for security vulnerabilities
echo -e "\nVulnerability Scan:"
if command -v lynis &> /dev/null; then
    lynis audit system --quick
else
    echo "Lynis not installed. Consider installing for security auditing."
fi
```

## Troubleshooting Procedures

### 1. Common Issues and Solutions

**High Memory Usage**:
```bash
#!/bin/bash
# troubleshoot_memory.sh

echo "=== Memory Troubleshooting ==="

# Check memory usage by process
echo "Top memory consumers:"
ps aux --sort=-%mem | head -10

# Check for memory leaks
echo -e "\nMemory usage over time:"
PID=$(pgrep -f "python server.py")
if [ ! -z "$PID" ]; then
    ps -p $PID -o pid,ppid,cmd,%mem,%cpu
    cat /proc/$PID/status | grep -E "(VmRSS|VmSize|VmPeak)"
fi

# Check swap usage
echo -e "\nSwap usage:"
free -h
swapon -s

# Recommendations
echo -e "\nTroubleshooting Steps:"
echo "1. Check for memory leaks in application"
echo "2. Increase memory allocation if needed"
echo "3. Implement connection pooling"
echo "4. Review crawler configuration"
```

**High CPU Usage**:
```bash
#!/bin/bash
# troubleshoot_cpu.sh

echo "=== CPU Troubleshooting ==="

# Check CPU usage by process
echo "Top CPU consumers:"
ps aux --sort=-%cpu | head -10

# Check load average
echo -e "\nLoad average:"
uptime

# Check for CPU-intensive processes
echo -e "\nCPU usage over time:"
top -bn1 | grep "python server.py"

# Check for runaway processes
echo -e "\nRunaway process check:"
ps aux | awk '$3 > 50 {print $0}'

# Recommendations
echo -e "\nTroubleshooting Steps:"
echo "1. Check for infinite loops in code"
echo "2. Optimize crawler configuration"
echo "3. Implement rate limiting"
echo "4. Consider horizontal scaling"
```

**Network Issues**:
```bash
#!/bin/bash
# troubleshoot_network.sh

echo "=== Network Troubleshooting ==="

# Check network connectivity
echo "Network connectivity:"
ping -c 4 8.8.8.8

# Check DNS resolution
echo -e "\nDNS resolution:"
nslookup google.com

# Check port availability
echo -e "\nPort status:"
netstat -tuln | grep :8000

# Check firewall rules
echo -e "\nFirewall rules:"
if command -v ufw &> /dev/null; then
    ufw status
fi

# Check for connection issues
echo -e "\nConnection statistics:"
ss -s

# Test MCP server connectivity
echo -e "\nMCP server test:"
curl -s http://localhost:8000/health 2>/dev/null || echo "Health endpoint not available"
```

### 2. Recovery Procedures

**Service Recovery**:
```bash
#!/bin/bash
# service_recovery.sh

echo "=== Service Recovery Procedure ==="

# Check service status
echo "Current service status:"
systemctl status crawl4ai-mcp-server

# Stop service
echo -e "\nStopping service..."
systemctl stop crawl4ai-mcp-server

# Check for hanging processes
echo -e "\nChecking for hanging processes..."
pkill -f "python server.py"

# Clean up temporary files
echo -e "\nCleaning up temporary files..."
rm -f /tmp/crawl4ai_*
rm -f /var/run/crawl4ai-mcp.pid

# Restart service
echo -e "\nRestarting service..."
systemctl start crawl4ai-mcp-server

# Verify service is running
echo -e "\nVerifying service status..."
sleep 5
systemctl status crawl4ai-mcp-server

# Test functionality
echo -e "\nTesting functionality..."
python3 -c "
import asyncio
from fastmcp import Client
from server import mcp

async def test():
    try:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            print(f'Service recovered successfully. Tools available: {len(tools)}')
    except Exception as e:
        print(f'Service recovery failed: {e}')

asyncio.run(test())
"
```

**Database Recovery** (if using external database):
```bash
#!/bin/bash
# database_recovery.sh

echo "=== Database Recovery Procedure ==="

# Check database connection
echo "Checking database connection..."
# Add database-specific commands here

# Restore from backup if needed
echo -e "\nRestoring from backup..."
LATEST_BACKUP=$(find /backup/crawl4ai-mcp -name "*.tar.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2)
if [ ! -z "$LATEST_BACKUP" ]; then
    echo "Latest backup: $LATEST_BACKUP"
    # Add restore procedure here
fi

# Verify data integrity
echo -e "\nVerifying data integrity..."
# Add verification commands here
```

## Performance Optimization

### 1. Configuration Tuning

**Optimize Server Configuration**:
```python
# optimize_config.py
import os
from typing import Dict, Any

class ConfigOptimizer:
    def __init__(self):
        self.recommendations = []
    
    def analyze_current_config(self) -> Dict[str, Any]:
        """Analyze current configuration."""
        config = {
            'user_agent': os.getenv('CRAWL4AI_USER_AGENT', 'Default'),
            'timeout': int(os.getenv('CRAWL4AI_TIMEOUT', '30')),
            'max_concurrent': int(os.getenv('MAX_CONCURRENT_REQUESTS', '50')),
            'log_level': os.getenv('LOG_LEVEL', 'INFO')
        }
        
        return config
    
    def generate_optimizations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimization recommendations."""
        optimized = config.copy()
        
        # Optimize timeout based on typical response times
        if config['timeout'] > 60:
            optimized['timeout'] = 45
            self.recommendations.append("Reduced timeout to 45s for better performance")
        
        # Optimize concurrency based on system resources
        import psutil
        cpu_count = psutil.cpu_count()
        if config['max_concurrent'] > cpu_count * 20:
            optimized['max_concurrent'] = cpu_count * 15
            self.recommendations.append(f"Reduced max concurrent requests to {cpu_count * 15}")
        
        # Optimize logging for production
        if config['log_level'] == 'DEBUG':
            optimized['log_level'] = 'INFO'
            self.recommendations.append("Changed log level to INFO for production")
        
        return optimized
    
    def print_optimization_report(self):
        """Print optimization recommendations."""
        current_config = self.analyze_current_config()
        optimized_config = self.generate_optimizations(current_config)
        
        print("=== Configuration Optimization Report ===")
        print("\nCurrent Configuration:")
        for key, value in current_config.items():
            print(f"  {key}: {value}")
        
        print("\nOptimized Configuration:")
        for key, value in optimized_config.items():
            print(f"  {key}: {value}")
        
        print("\nRecommendations:")
        for i, recommendation in enumerate(self.recommendations, 1):
            print(f"  {i}. {recommendation}")
        
        if not self.recommendations:
            print("  Configuration is already optimized.")

if __name__ == "__main__":
    optimizer = ConfigOptimizer()
    optimizer.print_optimization_report()
```

### 2. Resource Optimization

**Memory Optimization**:
```python
# memory_optimization.py
import gc
import psutil
import asyncio
from typing import Dict, List

class MemoryOptimizer:
    def __init__(self):
        self.baseline_memory = self.get_memory_usage()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def optimize_memory(self):
        """Perform memory optimization."""
        # Force garbage collection
        gc.collect()
        
        # Clear internal caches
        # This would clear application-specific caches
        
        # Report memory savings
        current_memory = self.get_memory_usage()
        savings = self.baseline_memory - current_memory
        
        print(f"Memory optimization complete:")
        print(f"  Before: {self.baseline_memory:.1f} MB")
        print(f"  After: {current_memory:.1f} MB")
        print(f"  Savings: {savings:.1f} MB")
        
        return savings
    
    def monitor_memory_leaks(self, duration: int = 300):
        """Monitor for memory leaks over time."""
        print(f"Monitoring memory usage for {duration} seconds...")
        
        memory_samples = []
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < duration:
            memory_samples.append(self.get_memory_usage())
            asyncio.sleep(10)
        
        # Analyze trend
        if len(memory_samples) > 1:
            trend = memory_samples[-1] - memory_samples[0]
            print(f"Memory trend over {duration}s: {trend:+.1f} MB")
            
            if trend > 50:  # More than 50MB increase
                print("WARNING: Potential memory leak detected")
            else:
                print("Memory usage is stable")

if __name__ == "__main__":
    optimizer = MemoryOptimizer()
    optimizer.optimize_memory()
```

## Monitoring and Alerting

### 1. Monitoring Setup

**Comprehensive Monitoring Script**:
```python
# monitoring_setup.py
import asyncio
import json
import time
import psutil
from datetime import datetime
from typing import Dict, List, Any

class MonitoringSystem:
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.thresholds = {
            'cpu_usage': 80,
            'memory_usage': 85,
            'disk_usage': 90,
            'response_time': 1.0,
            'error_rate': 5.0
        }
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg()[0],
            'process_count': len(psutil.pids()),
            'network_connections': len(psutil.net_connections())
        }
    
    async def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-specific metrics."""
        try:
            from fastmcp import Client
            from server import mcp
            
            start_time = time.time()
            async with Client(mcp) as client:
                tools = await client.list_tools()
                response_time = time.time() - start_time
            
            return {
                'response_time': response_time,
                'tools_available': len(tools),
                'service_status': 'healthy'
            }
        except Exception as e:
            return {
                'response_time': None,
                'tools_available': 0,
                'service_status': 'unhealthy',
                'error': str(e)
            }
    
    def check_thresholds(self, metrics: Dict[str, Any]):
        """Check if metrics exceed thresholds."""
        alerts = []
        
        for metric, threshold in self.thresholds.items():
            if metric in metrics and metrics[metric] is not None:
                if metrics[metric] > threshold:
                    alerts.append({
                        'metric': metric,
                        'value': metrics[metric],
                        'threshold': threshold,
                        'severity': 'warning' if metrics[metric] < threshold * 1.2 else 'critical'
                    })
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]):
        """Send alert (placeholder for actual alerting system)."""
        print(f"ALERT: {alert['metric']} = {alert['value']:.1f} (threshold: {alert['threshold']})")
        # In practice, this would send to Slack, email, PagerDuty, etc.
    
    async def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        # Collect metrics
        system_metrics = self.collect_system_metrics()
        app_metrics = await self.collect_application_metrics()
        
        combined_metrics = {**system_metrics, **app_metrics}
        
        # Check thresholds and send alerts
        alerts = self.check_thresholds(combined_metrics)
        for alert in alerts:
            self.send_alert(alert)
        
        # Store metrics for historical analysis
        self.metrics[datetime.now().isoformat()] = combined_metrics
        
        return combined_metrics
    
    async def continuous_monitoring(self, interval: int = 60):
        """Run continuous monitoring."""
        print(f"Starting continuous monitoring (interval: {interval}s)")
        
        while True:
            try:
                metrics = await self.run_monitoring_cycle()
                print(f"Monitoring cycle completed at {datetime.now()}")
                await asyncio.sleep(interval)
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(interval)

if __name__ == "__main__":
    monitor = MonitoringSystem()
    asyncio.run(monitor.continuous_monitoring())
```

### 2. Alert Configuration

**Alert Management System**:
```python
# alert_management.py
import json
import smtplib
from email.mime.text import MIMEText
from typing import Dict, List
from datetime import datetime, timedelta

class AlertManager:
    def __init__(self, config_file: str = "alert_config.json"):
        self.config = self.load_config(config_file)
        self.alert_history = []
    
    def load_config(self, config_file: str) -> Dict:
        """Load alerting configuration."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'recipients': []
                },
                'slack': {
                    'enabled': False,
                    'webhook_url': ''
                },
                'thresholds': {
                    'cpu_usage': 80,
                    'memory_usage': 85,
                    'disk_usage': 90,
                    'response_time': 1.0,
                    'error_rate': 5.0
                }
            }
    
    def should_suppress_alert(self, metric: str, severity: str) -> bool:
        """Check if alert should be suppressed due to recent similar alerts."""
        # Suppress if same alert was sent in the last 15 minutes
        cutoff_time = datetime.now() - timedelta(minutes=15)
        
        for alert in self.alert_history:
            if (alert['metric'] == metric and 
                alert['severity'] == severity and 
                alert['timestamp'] > cutoff_time):
                return True
        
        return False
    
    def send_email_alert(self, alert: Dict):
        """Send email alert."""
        if not self.config['email']['enabled']:
            return
        
        subject = f"Crawl4AI MCP Server Alert: {alert['metric']} {alert['severity']}"
        body = f"""
        Alert Details:
        - Metric: {alert['metric']}
        - Current Value: {alert['value']:.1f}
        - Threshold: {alert['threshold']}
        - Severity: {alert['severity']}
        - Timestamp: {alert['timestamp']}
        
        Please investigate and take appropriate action.
        """
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.config['email']['username']
        msg['To'] = ', '.join(self.config['email']['recipients'])
        
        try:
            server = smtplib.SMTP(self.config['email']['smtp_server'], 
                                self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], 
                        self.config['email']['password'])
            server.send_message(msg)
            server.quit()
            print(f"Email alert sent for {alert['metric']}")
        except Exception as e:
            print(f"Failed to send email alert: {e}")
    
    def send_slack_alert(self, alert: Dict):
        """Send Slack alert."""
        if not self.config['slack']['enabled']:
            return
        
        try:
            import requests
            
            message = {
                'text': f"🚨 Crawl4AI MCP Server Alert",
                'attachments': [{
                    'color': 'danger' if alert['severity'] == 'critical' else 'warning',
                    'fields': [
                        {'title': 'Metric', 'value': alert['metric'], 'short': True},
                        {'title': 'Value', 'value': f"{alert['value']:.1f}", 'short': True},
                        {'title': 'Threshold', 'value': str(alert['threshold']), 'short': True},
                        {'title': 'Severity', 'value': alert['severity'], 'short': True}
                    ]
                }]
            }
            
            response = requests.post(self.config['slack']['webhook_url'], 
                                   json=message)
            response.raise_for_status()
            print(f"Slack alert sent for {alert['metric']}")
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def process_alert(self, alert: Dict):
        """Process and send alert."""
        alert['timestamp'] = datetime.now()
        
        # Check if alert should be suppressed
        if self.should_suppress_alert(alert['metric'], alert['severity']):
            print(f"Alert suppressed: {alert['metric']} (recent similar alert)")
            return
        
        # Send alerts
        self.send_email_alert(alert)
        self.send_slack_alert(alert)
        
        # Store in history
        self.alert_history.append(alert)
        
        # Cleanup old alerts from history
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.alert_history = [a for a in self.alert_history if a['timestamp'] > cutoff_time]

if __name__ == "__main__":
    # Example usage
    alert_manager = AlertManager()
    
    # Example alert
    test_alert = {
        'metric': 'cpu_usage',
        'value': 85.5,
        'threshold': 80,
        'severity': 'warning'
    }
    
    alert_manager.process_alert(test_alert)
```

## Backup and Recovery

### 1. Backup Strategy

**Automated Backup System**:
```bash
#!/bin/bash
# automated_backup.sh

BACKUP_DIR="/backup/crawl4ai-mcp"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "=== Automated Backup - $DATE ==="

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration files
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    /opt/crawl4ai-mcp-server/.env \
    /opt/crawl4ai-mcp-server/pyproject.toml \
    /etc/systemd/system/crawl4ai-mcp-server.service

# Backup logs
echo "Backing up logs..."
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz \
    /var/log/crawl4ai-mcp.log* \
    /var/log/crawl4ai-mcp-error.log*

# Backup application code
echo "Backing up application..."
tar -czf $BACKUP_DIR/app_$DATE.tar.gz \
    /opt/crawl4ai-mcp-server \
    --exclude=/opt/crawl4ai-mcp-server/.venv \
    --exclude=/opt/crawl4ai-mcp-server/__pycache__ \
    --exclude=/opt/crawl4ai-mcp-server/.git

# Create backup manifest
echo "Creating backup manifest..."
cat > $BACKUP_DIR/manifest_$DATE.txt << EOF
Backup Date: $DATE
Backup Contents:
- config_$DATE.tar.gz: Configuration files
- logs_$DATE.tar.gz: Log files
- app_$DATE.tar.gz: Application code
System Info:
- Hostname: $(hostname)
- OS: $(uname -a)
- Python Version: $(python3 --version)
EOF

# Cleanup old backups
echo "Cleaning up old backups..."
find $BACKUP_DIR -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.txt" -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
echo "Verifying backup integrity..."
for backup in $BACKUP_DIR/*_$DATE.tar.gz; do
    if tar -tzf $backup > /dev/null 2>&1; then
        echo "✓ $(basename $backup) - OK"
    else
        echo "✗ $(basename $backup) - CORRUPTED"
    fi
done

echo "Backup completed successfully"
```

### 2. Recovery Procedures

**Recovery Script**:
```bash
#!/bin/bash
# recovery_procedure.sh

BACKUP_DIR="/backup/crawl4ai-mcp"
RESTORE_DATE=$1

if [ -z "$RESTORE_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls -1 $BACKUP_DIR/manifest_*.txt | sed 's/.*manifest_//' | sed 's/.txt//'
    exit 1
fi

echo "=== Recovery Procedure - $RESTORE_DATE ==="

# Verify backup files exist
if [ ! -f "$BACKUP_DIR/config_$RESTORE_DATE.tar.gz" ]; then
    echo "Error: Backup files for $RESTORE_DATE not found"
    exit 1
fi

# Stop service
echo "Stopping service..."
systemctl stop crawl4ai-mcp-server

# Backup current state
echo "Backing up current state..."
CURRENT_DATE=$(date +%Y%m%d_%H%M%S)
tar -czf $BACKUP_DIR/pre_recovery_$CURRENT_DATE.tar.gz /opt/crawl4ai-mcp-server

# Restore configuration
echo "Restoring configuration..."
tar -xzf $BACKUP_DIR/config_$RESTORE_DATE.tar.gz -C /

# Restore application
echo "Restoring application..."
rm -rf /opt/crawl4ai-mcp-server
tar -xzf $BACKUP_DIR/app_$RESTORE_DATE.tar.gz -C /

# Restore logs (optional)
echo "Restoring logs..."
tar -xzf $BACKUP_DIR/logs_$RESTORE_DATE.tar.gz -C /

# Reinstall dependencies
echo "Reinstalling dependencies..."
cd /opt/crawl4ai-mcp-server
python3 -m venv .venv
source .venv/bin/activate
pip install uv
uv install
playwright install

# Fix permissions
echo "Fixing permissions..."
chown -R crawl4ai:crawl4ai /opt/crawl4ai-mcp-server
chmod +x /opt/crawl4ai-mcp-server/server.py

# Start service
echo "Starting service..."
systemctl start crawl4ai-mcp-server

# Verify recovery
echo "Verifying recovery..."
sleep 10
systemctl status crawl4ai-mcp-server

# Test functionality
echo "Testing functionality..."
python3 -c "
import asyncio
from fastmcp import Client
from server import mcp

async def test():
    try:
        async with Client(mcp) as client:
            tools = await client.list_tools()
            print(f'Recovery successful. Tools available: {len(tools)}')
    except Exception as e:
        print(f'Recovery verification failed: {e}')

asyncio.run(test())
"

echo "Recovery procedure completed"
```

This comprehensive maintenance guide provides all the tools and procedures needed to keep the Crawl4AI MCP Server running smoothly in production environments. Regular execution of these maintenance tasks will ensure optimal performance, security, and reliability.