import time
import psutil
import logging
from datetime import datetime, timedelta
from django.db import connection
from django.core.cache import cache

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Monitor system performance and resource usage
    """
    
    def __init__(self):
        self.metrics = {
            'response_times': [],
            'memory_usage': [],
            'database_queries': [],
            'cache_hits': 0,
            'cache_misses': 0
        }
        self.start_time = time.time()
    
    def track_response_time(self, endpoint, response_time):
        """Track API response times"""
        self.metrics['response_times'].append({
            'endpoint': endpoint,
            'response_time': response_time,
            'timestamp': datetime.now()
        })
        
        # Keep only last 1000 records
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def get_performance_metrics(self):
        """Get comprehensive performance metrics"""
        # System metrics
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Database metrics
        db_queries = len(connection.queries) if connection.queries else 0
        
        # Response time metrics
        recent_responses = [
            rt for rt in self.metrics['response_times']
            if rt['timestamp'] > datetime.now() - timedelta(hours=1)
        ]
        
        avg_response_time = (
            sum(rt['response_time'] for rt in recent_responses) / len(recent_responses)
            if recent_responses else 0
        )
        
        # Uptime
        uptime = time.time() - self.start_time
        
        return {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'memory_usage_percent': memory_usage,
                'cpu_usage_percent': cpu_usage,
                'uptime_seconds': uptime
            },
            'application': {
                'average_response_time_ms': avg_response_time * 1000,
                'recent_requests_count': len(recent_responses),
                'database_queries_count': db_queries,
                'cache_hit_rate': self._calculate_cache_hit_rate()
            },
            'endpoints': self._get_endpoint_metrics()
        }
    
    def _calculate_cache_hit_rate(self):
        """Calculate cache hit rate"""
        total = self.metrics['cache_hits'] + self.metrics['cache_misses']
        return self.metrics['cache_hits'] / total if total > 0 else 0
    
    def _get_endpoint_metrics(self):
        """Get metrics by endpoint"""
        endpoint_metrics = {}
        
        for response in self.metrics['response_times'][-100:]:  # Last 100 requests
            endpoint = response['endpoint']
            if endpoint not in endpoint_metrics:
                endpoint_metrics[endpoint] = {
                    'count': 0,
                    'total_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
            
            metrics = endpoint_metrics[endpoint]
            metrics['count'] += 1
            metrics['total_time'] += response['response_time']
            metrics['min_time'] = min(metrics['min_time'], response['response_time'])
            metrics['max_time'] = max(metrics['max_time'], response['response_time'])
        
        # Calculate averages
        for endpoint, metrics in endpoint_metrics.items():
            metrics['avg_time'] = metrics['total_time'] / metrics['count']
        
        return endpoint_metrics
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics['cache_hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics['cache_misses'] += 1

# Global performance monitor
performance_monitor = PerformanceMonitor()