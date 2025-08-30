#!/usr/bin/env python3
"""
Comprehensive Monitoring and Logging System
Tracks performance, usage, and system health
"""

import json
import time
import psutil
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import sqlite3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Metric:
    """Represents a system metric"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class Event:
    """Represents a system event"""
    event_type: str
    message: str
    timestamp: datetime
    level: str  # info, warning, error, critical
    metadata: Dict[str, Any] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

class MetricsCollector:
    """Collects system and application metrics"""
    
    def __init__(self, interval: int = 60):
        self.interval = interval
        self.metrics_buffer = deque(maxlen=10000)
        self.running = False
        self.thread = None
    
    def collect_system_metrics(self) -> List[Metric]:
        """Collect system-level metrics"""
        metrics = []
        now = datetime.now()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(Metric(
            name="system.cpu.usage",
            value=cpu_percent,
            unit="percent",
            timestamp=now
        ))
        
        # Memory metrics
        memory = psutil.virtual_memory()
        metrics.append(Metric(
            name="system.memory.usage",
            value=memory.percent,
            unit="percent",
            timestamp=now
        ))
        metrics.append(Metric(
            name="system.memory.available",
            value=memory.available / (1024**3),  # Convert to GB
            unit="GB",
            timestamp=now
        ))
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        metrics.append(Metric(
            name="system.disk.usage",
            value=disk.percent,
            unit="percent",
            timestamp=now
        ))
        
        # Network metrics (if available)
        try:
            net_io = psutil.net_io_counters()
            metrics.append(Metric(
                name="system.network.bytes_sent",
                value=net_io.bytes_sent,
                unit="bytes",
                timestamp=now
            ))
            metrics.append(Metric(
                name="system.network.bytes_recv",
                value=net_io.bytes_recv,
                unit="bytes",
                timestamp=now
            ))
        except:
            pass
        
        return metrics
    
    def _collection_loop(self):
        """Background collection loop"""
        while self.running:
            try:
                metrics = self.collect_system_metrics()
                self.metrics_buffer.extend(metrics)
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
            
            time.sleep(self.interval)
    
    def start(self):
        """Start metrics collection"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._collection_loop)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Metrics collector started")
    
    def stop(self):
        """Stop metrics collection"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Metrics collector stopped")
    
    def get_recent_metrics(self, count: int = 100) -> List[Dict]:
        """Get recent metrics"""
        return [m.to_dict() for m in list(self.metrics_buffer)[-count:]]

class EventLogger:
    """Logs and tracks system events"""
    
    def __init__(self, log_file: str = "events.log"):
        self.log_file = log_file
        self.events_buffer = deque(maxlen=1000)
        self.event_counts = defaultdict(int)
    
    def log_event(
        self,
        event_type: str,
        message: str,
        level: str = "info",
        metadata: Dict = None,
        user_id: str = None,
        session_id: str = None
    ):
        """Log an event"""
        event = Event(
            event_type=event_type,
            message=message,
            timestamp=datetime.now(),
            level=level,
            metadata=metadata,
            user_id=user_id,
            session_id=session_id
        )
        
        self.events_buffer.append(event)
        self.event_counts[event_type] += 1
        
        # Write to file
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event.to_dict()) + '\n')
        
        # Also log to standard logger
        log_func = getattr(logger, level, logger.info)
        log_func(f"[{event_type}] {message}")
    
    def get_recent_events(
        self,
        count: int = 100,
        event_type: str = None,
        level: str = None
    ) -> List[Dict]:
        """Get recent events with optional filtering"""
        events = list(self.events_buffer)
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if level:
            events = [e for e in events if e.level == level]
        
        return [e.to_dict() for e in events[-count:]]
    
    def get_event_statistics(self) -> Dict:
        """Get event statistics"""
        return dict(self.event_counts)

class PerformanceTracker:
    """Tracks performance metrics for operations"""
    
    def __init__(self):
        self.operation_times = defaultdict(list)
        self.operation_counts = defaultdict(int)
    
    def track_operation(self, operation_name: str):
        """Decorator to track operation performance"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    self.operation_times[operation_name].append(duration)
                    self.operation_counts[operation_name] += 1
                    
                    # Keep only last 1000 measurements
                    if len(self.operation_times[operation_name]) > 1000:
                        self.operation_times[operation_name] = \
                            self.operation_times[operation_name][-1000:]
                    
                    return result
                
                except Exception as e:
                    duration = time.time() - start_time
                    self.operation_times[f"{operation_name}_error"].append(duration)
                    raise
            
            return wrapper
        return decorator
    
    def get_performance_stats(self, operation_name: str = None) -> Dict:
        """Get performance statistics"""
        if operation_name:
            times = self.operation_times.get(operation_name, [])
            if not times:
                return {}
            
            return {
                'operation': operation_name,
                'count': self.operation_counts[operation_name],
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times)
            }
        
        # Get stats for all operations
        stats = {}
        for op_name in self.operation_times:
            stats[op_name] = self.get_performance_stats(op_name)
        
        return stats

class DatabaseMonitor:
    """Monitors database for analytics"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                message TEXT,
                level TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                user_id TEXT,
                session_id TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT NOT NULL,
                method TEXT,
                status_code INTEGER,
                response_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                ip_address TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric: Metric):
        """Record a metric to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO metrics (name, value, unit, timestamp, tags)
            VALUES (?, ?, ?, ?, ?)
        """, (
            metric.name,
            metric.value,
            metric.unit,
            metric.timestamp,
            json.dumps(metric.tags) if metric.tags else None
        ))
        
        conn.commit()
        conn.close()
    
    def record_event(self, event: Event):
        """Record an event to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO events (event_type, message, level, timestamp, metadata, user_id, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event.event_type,
            event.message,
            event.level,
            event.timestamp,
            json.dumps(event.metadata) if event.metadata else None,
            event.user_id,
            event.session_id
        ))
        
        conn.commit()
        conn.close()
    
    def record_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time: float,
        user_id: str = None,
        ip_address: str = None
    ):
        """Record API call"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO api_calls (endpoint, method, status_code, response_time, user_id, ip_address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (endpoint, method, status_code, response_time, user_id, ip_address))
        
        conn.commit()
        conn.close()
    
    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """Get metrics summary for last N hours"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT name, AVG(value) as avg_value, MIN(value) as min_value, 
                   MAX(value) as max_value, COUNT(*) as count
            FROM metrics
            WHERE timestamp > ?
            GROUP BY name
        """, (since,))
        
        results = cursor.fetchall()
        conn.close()
        
        summary = {}
        for row in results:
            summary[row[0]] = {
                'avg': row[1],
                'min': row[2],
                'max': row[3],
                'count': row[4]
            }
        
        return summary
    
    def get_api_stats(self, hours: int = 24) -> Dict:
        """Get API statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        # Overall stats
        cursor.execute("""
            SELECT COUNT(*) as total_calls,
                   AVG(response_time) as avg_response_time,
                   COUNT(DISTINCT user_id) as unique_users
            FROM api_calls
            WHERE timestamp > ?
        """, (since,))
        
        overall = cursor.fetchone()
        
        # Per endpoint stats
        cursor.execute("""
            SELECT endpoint, method, COUNT(*) as count,
                   AVG(response_time) as avg_time
            FROM api_calls
            WHERE timestamp > ?
            GROUP BY endpoint, method
            ORDER BY count DESC
            LIMIT 10
        """, (since,))
        
        endpoints = cursor.fetchall()
        
        # Status code distribution
        cursor.execute("""
            SELECT status_code, COUNT(*) as count
            FROM api_calls
            WHERE timestamp > ?
            GROUP BY status_code
        """, (since,))
        
        status_codes = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_calls': overall[0],
            'avg_response_time': overall[1],
            'unique_users': overall[2],
            'top_endpoints': [
                {
                    'endpoint': e[0],
                    'method': e[1],
                    'count': e[2],
                    'avg_time': e[3]
                }
                for e in endpoints
            ],
            'status_codes': {str(s[0]): s[1] for s in status_codes}
        }

class MonitoringSystem:
    """Main monitoring system orchestrator"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.event_logger = EventLogger()
        self.performance_tracker = PerformanceTracker()
        self.db_monitor = DatabaseMonitor()
        self.alerts = []
    
    def start(self):
        """Start monitoring system"""
        self.metrics_collector.start()
        logger.info("Monitoring system started")
    
    def stop(self):
        """Stop monitoring system"""
        self.metrics_collector.stop()
        logger.info("Monitoring system stopped")
    
    def check_alerts(self) -> List[Dict]:
        """Check for alert conditions"""
        alerts = []
        
        # Check CPU usage
        recent_metrics = self.metrics_collector.get_recent_metrics(10)
        cpu_metrics = [m for m in recent_metrics if m.get('name') == 'system.cpu.usage']
        
        if cpu_metrics:
            avg_cpu = sum(m['value'] for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 80:
                alerts.append({
                    'type': 'high_cpu',
                    'message': f'High CPU usage: {avg_cpu:.1f}%',
                    'severity': 'warning'
                })
        
        # Check memory usage
        memory_metrics = [m for m in recent_metrics if m.get('name') == 'system.memory.usage']
        
        if memory_metrics:
            avg_memory = sum(m['value'] for m in memory_metrics) / len(memory_metrics)
            if avg_memory > 90:
                alerts.append({
                    'type': 'high_memory',
                    'message': f'High memory usage: {avg_memory:.1f}%',
                    'severity': 'critical'
                })
        
        # Check error rate
        events = self.event_logger.get_recent_events(100, level='error')
        if len(events) > 10:
            alerts.append({
                'type': 'high_error_rate',
                'message': f'High error rate: {len(events)} errors in recent events',
                'severity': 'warning'
            })
        
        self.alerts = alerts
        return alerts
    
    def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        return {
            'system_metrics': self.metrics_collector.get_recent_metrics(50),
            'recent_events': self.event_logger.get_recent_events(50),
            'event_stats': self.event_logger.get_event_statistics(),
            'performance_stats': self.performance_tracker.get_performance_stats(),
            'api_stats': self.db_monitor.get_api_stats(24),
            'metrics_summary': self.db_monitor.get_metrics_summary(24),
            'alerts': self.check_alerts(),
            'timestamp': datetime.now().isoformat()
        }

# Global monitoring instance
monitoring = MonitoringSystem()

def track_performance(operation_name: str):
    """Decorator to track operation performance"""
    return monitoring.performance_tracker.track_operation(operation_name)

def log_event(event_type: str, message: str, **kwargs):
    """Log an event"""
    monitoring.event_logger.log_event(event_type, message, **kwargs)

def record_api_call(endpoint: str, method: str, status_code: int, response_time: float, **kwargs):
    """Record API call"""
    monitoring.db_monitor.record_api_call(endpoint, method, status_code, response_time, **kwargs)

if __name__ == "__main__":
    # Example usage
    monitoring.start()
    
    try:
        # Log some events
        log_event("startup", "System started successfully")
        log_event("analysis", "Running data analysis", metadata={'dataset': 'sales_data.csv'})
        
        # Simulate some API calls
        record_api_call("/api/v1/analyze", "POST", 200, 1.23, user_id="user123")
        record_api_call("/api/v1/models", "GET", 200, 0.45, user_id="user456")
        
        # Wait and collect metrics
        time.sleep(5)
        
        # Get dashboard data
        dashboard = monitoring.get_dashboard_data()
        print(json.dumps(dashboard, indent=2))
        
    finally:
        monitoring.stop()