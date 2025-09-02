"""
Production Monitoring and Logging Configuration
Enterprise AI Data Analysis Platform
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
import json
import psutil
import streamlit as st

# Create logs directory
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
def setup_logging():
    """Set up comprehensive logging for production environment"""
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler for all logs
    file_handler = logging.FileHandler(
        LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # File handler for errors only
    error_handler = logging.FileHandler(
        LOGS_DIR / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Performance monitoring
class PerformanceMonitor:
    """Monitor system and application performance"""
    
    @staticmethod
    def get_system_metrics():
        """Get current system metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
            "process_count": len(psutil.pids())
        }
    
    @staticmethod
    def log_metrics(logger):
        """Log system metrics"""
        metrics = PerformanceMonitor.get_system_metrics()
        logger.info(f"System Metrics: {json.dumps(metrics)}")
        return metrics
    
    @staticmethod
    def check_health():
        """Check system health and return status"""
        metrics = PerformanceMonitor.get_system_metrics()
        
        health_status = {
            "healthy": True,
            "warnings": [],
            "metrics": metrics
        }
        
        # Check CPU usage
        if metrics["cpu_percent"] > 80:
            health_status["warnings"].append(f"High CPU usage: {metrics['cpu_percent']}%")
            health_status["healthy"] = False
        
        # Check memory usage
        if metrics["memory_percent"] > 85:
            health_status["warnings"].append(f"High memory usage: {metrics['memory_percent']}%")
            health_status["healthy"] = False
        
        # Check disk usage
        if metrics["disk_usage"] > 90:
            health_status["warnings"].append(f"High disk usage: {metrics['disk_usage']}%")
            health_status["healthy"] = False
        
        return health_status

# User activity tracking
class ActivityTracker:
    """Track user activities for analytics"""
    
    @staticmethod
    def log_activity(logger, user_email, action, details=None):
        """Log user activity"""
        activity = {
            "timestamp": datetime.now().isoformat(),
            "user": user_email,
            "action": action,
            "details": details or {}
        }
        
        # Log to file
        logger.info(f"User Activity: {json.dumps(activity)}")
        
        # Store in session state for analytics
        if 'activity_log' not in st.session_state:
            st.session_state.activity_log = []
        st.session_state.activity_log.append(activity)
        
        return activity
    
    @staticmethod
    def get_activity_summary():
        """Get summary of user activities"""
        if 'activity_log' not in st.session_state:
            return {"total_activities": 0, "activities": []}
        
        activities = st.session_state.activity_log
        
        # Group by action type
        action_counts = {}
        for activity in activities:
            action = activity.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
        
        return {
            "total_activities": len(activities),
            "action_counts": action_counts,
            "recent_activities": activities[-10:] if activities else []
        }

# Error tracking
class ErrorTracker:
    """Track and report errors"""
    
    @staticmethod
    def log_error(logger, error_type, error_message, user_email=None, context=None):
        """Log error with context"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": str(error_message),
            "user": user_email,
            "context": context or {}
        }
        
        # Log to error file
        logger.error(f"Application Error: {json.dumps(error_data)}")
        
        # Store in session state for reporting
        if 'error_log' not in st.session_state:
            st.session_state.error_log = []
        st.session_state.error_log.append(error_data)
        
        return error_data
    
    @staticmethod
    def get_error_summary():
        """Get summary of errors"""
        if 'error_log' not in st.session_state:
            return {"total_errors": 0, "errors": []}
        
        errors = st.session_state.error_log
        
        # Group by error type
        error_counts = {}
        for error in errors:
            error_type = error.get("type", "unknown")
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": len(errors),
            "error_counts": error_counts,
            "recent_errors": errors[-10:] if errors else []
        }

# Monitoring dashboard
def show_monitoring_dashboard(logger):
    """Display monitoring dashboard in Streamlit"""
    st.title("📊 System Monitoring Dashboard")
    
    # System Health
    st.header("🏥 System Health")
    health = PerformanceMonitor.check_health()
    
    if health["healthy"]:
        st.success("✅ System is healthy")
    else:
        st.error("⚠️ System health issues detected")
        for warning in health["warnings"]:
            st.warning(warning)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    metrics = health["metrics"]
    
    with col1:
        st.metric("CPU Usage", f"{metrics['cpu_percent']}%")
    with col2:
        st.metric("Memory Usage", f"{metrics['memory_percent']}%")
    with col3:
        st.metric("Disk Usage", f"{metrics['disk_usage']}%")
    with col4:
        st.metric("Process Count", metrics['process_count'])
    
    # User Activity
    st.header("👥 User Activity")
    activity_summary = ActivityTracker.get_activity_summary()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Activities", activity_summary["total_activities"])
    with col2:
        if activity_summary["action_counts"]:
            st.write("**Activity Breakdown:**")
            for action, count in activity_summary["action_counts"].items():
                st.write(f"- {action}: {count}")
    
    # Error Tracking
    st.header("🚨 Error Tracking")
    error_summary = ErrorTracker.get_error_summary()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Errors", error_summary["total_errors"])
    with col2:
        if error_summary["error_counts"]:
            st.write("**Error Types:**")
            for error_type, count in error_summary["error_counts"].items():
                st.write(f"- {error_type}: {count}")
    
    # Recent Activities
    if st.checkbox("Show Recent Activities"):
        st.subheader("Recent User Activities")
        for activity in activity_summary["recent_activities"][-5:]:
            st.write(f"- {activity['timestamp']}: {activity['user']} - {activity['action']}")
    
    # Recent Errors
    if st.checkbox("Show Recent Errors"):
        st.subheader("Recent Errors")
        for error in error_summary["recent_errors"][-5:]:
            st.write(f"- {error['timestamp']}: {error['type']} - {error['message']}")
    
    # Export Logs
    st.header("📁 Export Logs")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Activity Log"):
            activity_json = json.dumps(activity_summary, indent=2)
            st.download_button(
                "Download Activity Log",
                activity_json,
                f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
    
    with col2:
        if st.button("Export Error Log"):
            error_json = json.dumps(error_summary, indent=2)
            st.download_button(
                "Download Error Log",
                error_json,
                f"error_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )
    
    with col3:
        if st.button("Export System Metrics"):
            metrics_json = json.dumps(metrics, indent=2)
            st.download_button(
                "Download System Metrics",
                metrics_json,
                f"system_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "application/json"
            )

# Initialize monitoring
logger = setup_logging()
logger.info("=== Monitoring System Initialized ===")

# Export for use in main application
__all__ = [
    'setup_logging',
    'PerformanceMonitor',
    'ActivityTracker',
    'ErrorTracker',
    'show_monitoring_dashboard',
    'logger'
]