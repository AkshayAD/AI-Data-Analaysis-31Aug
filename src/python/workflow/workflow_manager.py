#!/usr/bin/env python3
"""
Workflow Manager: Orchestrates the complete flow from manager planning 
to automated Marimo analysis and results aggregation
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from agents import DataAnalysisAgent, MLAgent, VisualizationAgent
from agents.orchestrator import AgentOrchestrator
from marimo_integration import NotebookRunner, NotebookBuilder
from marimo_integration.simple_notebook import create_working_marimo_notebook

class SimpleNotebookGenerator:
    """Wrapper for notebook generation"""
    def generate_notebook(self, data_path: str, analysis_type: str, output_var: str, additional_code: str = "") -> str:
        """Generate a Marimo notebook with the specified analysis"""
        notebook_content = f'''import marimo as mo

app = mo.App()

@app.cell
def __():
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
    return pd, np, plt, sns, stats, train_test_split, RandomForestRegressor, RandomForestClassifier, IsolationForest, KMeans, StandardScaler, mean_squared_error, accuracy_score, r2_score

@app.cell
def __(pd):
    # Load data
    df = pd.read_csv('{data_path}')
    print(f"Loaded {{len(df)}} rows and {{len(df.columns)}} columns")
    return df,

@app.cell  
def __(df, pd, np, plt, sns, stats):
    # Analysis code
    {additional_code}
    
    # Return the output variable
    return {output_var},

if __name__ == "__main__":
    app.run()
'''
        return notebook_content

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of analysis tasks"""
    DATA_PROFILING = "data_profiling"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    TIME_SERIES_ANALYSIS = "time_series"
    PREDICTIVE_MODELING = "predictive_modeling"
    ANOMALY_DETECTION = "anomaly_detection"
    SEGMENTATION = "segmentation"
    VISUALIZATION = "visualization"
    CUSTOM = "custom"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    MARIMO_RUNNING = "marimo_running"
    COMPLETED = "completed"
    FAILED = "failed"
    APPROVED = "approved"
    REJECTED = "rejected"

class UserRole(Enum):
    """User roles in the workflow"""
    MANAGER = "manager"
    SENIOR_ANALYST = "senior_analyst"
    ANALYST = "analyst"
    ASSOCIATE = "associate"
    VIEWER = "viewer"

@dataclass
class User:
    """User in the workflow system"""
    id: str
    name: str
    email: str
    role: UserRole
    skills: List[str] = field(default_factory=list)
    workload: int = 0  # Current number of tasks
    max_workload: int = 5

@dataclass
class AnalysisTask:
    """Individual analysis task"""
    id: str
    name: str
    description: str
    task_type: TaskType
    status: TaskStatus
    assigned_to: Optional[str] = None
    created_by: str = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    deadline: Optional[datetime] = None
    priority: int = 1  # 1-5, 5 being highest
    data_source: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    marimo_notebook_path: Optional[str] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # Task IDs this depends on
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['task_type'] = self.task_type.value
        data['status'] = self.status.value
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        if self.deadline:
            data['deadline'] = self.deadline.isoformat()
        return data

@dataclass
class AnalysisPlan:
    """Manager's analysis plan"""
    id: str
    name: str
    description: str
    created_by: str
    created_at: datetime
    objectives: List[str]
    data_sources: List[str]
    tasks: List[AnalysisTask]
    timeline: Dict[str, datetime]  # milestones
    status: str = "draft"  # draft, active, completed, cancelled
    approval_required: bool = True
    approved_by: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['tasks'] = [task.to_dict() for task in self.tasks]
        data['timeline'] = {k: v.isoformat() for k, v in self.timeline.items()}
        return data

class WorkflowManager:
    """Manages the complete workflow from planning to results"""
    
    def __init__(self, workspace_path: str = "./workflow_workspace"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Directories
        self.plans_dir = self.workspace_path / "plans"
        self.tasks_dir = self.workspace_path / "tasks"
        self.notebooks_dir = self.workspace_path / "notebooks"
        self.results_dir = self.workspace_path / "results"
        
        for dir_path in [self.plans_dir, self.tasks_dir, self.notebooks_dir, self.results_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # In-memory storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.plans: Dict[str, AnalysisPlan] = {}
        self.tasks: Dict[str, AnalysisTask] = {}
        
        # Components
        self.notebook_runner = NotebookRunner()
        self.notebook_builder = NotebookBuilder()
        self.notebook_generator = SimpleNotebookGenerator()
        self.orchestrator = AgentOrchestrator()
        
        # Task queue
        self.task_queue: List[str] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    # === User Management ===
    
    def register_user(self, user: User) -> str:
        """Register a new user"""
        self.users[user.id] = user
        logger.info(f"Registered user: {user.name} ({user.role.value})")
        return user.id
    
    def get_available_associates(self, task_type: TaskType = None) -> List[User]:
        """Get available associates for task assignment"""
        available = []
        
        for user in self.users.values():
            # Check role
            if user.role not in [UserRole.ASSOCIATE, UserRole.ANALYST]:
                continue
            
            # Check workload
            if user.workload >= user.max_workload:
                continue
            
            # Check skills if specified
            if task_type and task_type.value not in user.skills:
                continue
            
            available.append(user)
        
        # Sort by workload (least busy first)
        available.sort(key=lambda x: x.workload)
        return available
    
    # === Plan Management ===
    
    def create_plan(
        self,
        name: str,
        description: str,
        objectives: List[str],
        data_sources: List[str],
        created_by: str,
        timeline: Dict[str, datetime] = None,
        auto_generate_tasks: bool = True
    ) -> AnalysisPlan:
        """Create a new analysis plan"""
        
        plan_id = str(uuid.uuid4())
        
        # Generate tasks if requested
        tasks = []
        if auto_generate_tasks:
            tasks = self._generate_tasks_from_objectives(objectives, data_sources)
        
        plan = AnalysisPlan(
            id=plan_id,
            name=name,
            description=description,
            created_by=created_by,
            created_at=datetime.now(),
            objectives=objectives,
            data_sources=data_sources,
            tasks=tasks,
            timeline=timeline or {},
            status="draft"
        )
        
        self.plans[plan_id] = plan
        
        # Save plan
        self._save_plan(plan)
        
        logger.info(f"Created plan: {name} with {len(tasks)} tasks")
        return plan
    
    def _generate_tasks_from_objectives(
        self,
        objectives: List[str],
        data_sources: List[str]
    ) -> List[AnalysisTask]:
        """Generate tasks based on objectives"""
        tasks = []
        
        # Standard task templates based on common objectives
        task_templates = {
            "data quality": [TaskType.DATA_PROFILING, TaskType.ANOMALY_DETECTION],
            "trends": [TaskType.TIME_SERIES_ANALYSIS, TaskType.VISUALIZATION],
            "prediction": [TaskType.PREDICTIVE_MODELING, TaskType.STATISTICAL_ANALYSIS],
            "segmentation": [TaskType.SEGMENTATION, TaskType.VISUALIZATION],
            "correlation": [TaskType.CORRELATION_ANALYSIS, TaskType.STATISTICAL_ANALYSIS],
            "performance": [TaskType.STATISTICAL_ANALYSIS, TaskType.VISUALIZATION],
            "anomaly": [TaskType.ANOMALY_DETECTION, TaskType.DATA_PROFILING]
        }
        
        for obj in objectives:
            obj_lower = obj.lower()
            
            # Find matching templates
            matched_types = []
            for keyword, types in task_templates.items():
                if keyword in obj_lower:
                    matched_types.extend(types)
            
            # Default to data profiling if no match
            if not matched_types:
                matched_types = [TaskType.DATA_PROFILING]
            
            # Create tasks for each type
            for task_type in set(matched_types):
                task = AnalysisTask(
                    id=str(uuid.uuid4()),
                    name=f"{task_type.value.replace('_', ' ').title()} - {obj[:50]}",
                    description=f"Perform {task_type.value} for objective: {obj}",
                    task_type=task_type,
                    status=TaskStatus.PENDING,
                    created_at=datetime.now(),
                    priority=3,
                    data_source=data_sources[0] if data_sources else None,
                    parameters={
                        'objective': obj,
                        'data_sources': data_sources
                    }
                )
                tasks.append(task)
        
        # Add dependencies (data profiling should come first)
        profiling_tasks = [t for t in tasks if t.task_type == TaskType.DATA_PROFILING]
        other_tasks = [t for t in tasks if t.task_type != TaskType.DATA_PROFILING]
        
        for task in other_tasks:
            for prof_task in profiling_tasks:
                if prof_task.data_source == task.data_source:
                    task.dependencies.append(prof_task.id)
        
        return tasks
    
    def approve_plan(self, plan_id: str, approver_id: str) -> bool:
        """Approve a plan for execution"""
        if plan_id not in self.plans:
            return False
        
        plan = self.plans[plan_id]
        plan.status = "active"
        plan.approved_by = approver_id
        
        # Add tasks to system
        for task in plan.tasks:
            self.tasks[task.id] = task
            self.task_queue.append(task.id)
        
        logger.info(f"Plan {plan.name} approved by {approver_id}")
        return True
    
    # === Task Assignment ===
    
    def assign_task(self, task_id: str, user_id: str) -> bool:
        """Assign a task to a user"""
        if task_id not in self.tasks or user_id not in self.users:
            return False
        
        task = self.tasks[task_id]
        user = self.users[user_id]
        
        # Check workload
        if user.workload >= user.max_workload:
            logger.warning(f"User {user.name} at max workload")
            return False
        
        task.assigned_to = user_id
        task.status = TaskStatus.ASSIGNED
        user.workload += 1
        
        logger.info(f"Task {task.name} assigned to {user.name}")
        return True
    
    def auto_assign_tasks(self) -> Dict[str, str]:
        """Automatically assign pending tasks to available associates"""
        assignments = {}
        
        for task_id in self.task_queue:
            if task_id not in self.tasks:
                continue
            
            task = self.tasks[task_id]
            
            if task.status != TaskStatus.PENDING:
                continue
            
            # Check dependencies
            if not self._check_dependencies(task):
                continue
            
            # Find available associate
            available = self.get_available_associates(task.task_type)
            
            if available:
                user = available[0]  # Take least busy
                if self.assign_task(task_id, user.id):
                    assignments[task_id] = user.id
        
        logger.info(f"Auto-assigned {len(assignments)} tasks")
        return assignments
    
    def _check_dependencies(self, task: AnalysisTask) -> bool:
        """Check if task dependencies are met"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.APPROVED]:
                    return False
        return True
    
    # === Marimo Integration ===
    
    def generate_marimo_notebook(self, task: AnalysisTask) -> str:
        """Generate a Marimo notebook for a task"""
        
        notebook_path = self.notebooks_dir / f"{task.id}.py"
        
        # Generate based on task type
        if task.task_type == TaskType.DATA_PROFILING:
            content = self._generate_profiling_notebook(task)
        elif task.task_type == TaskType.STATISTICAL_ANALYSIS:
            content = self._generate_statistical_notebook(task)
        elif task.task_type == TaskType.CORRELATION_ANALYSIS:
            content = self._generate_correlation_notebook(task)
        elif task.task_type == TaskType.TIME_SERIES_ANALYSIS:
            content = self._generate_timeseries_notebook(task)
        elif task.task_type == TaskType.PREDICTIVE_MODELING:
            content = self._generate_predictive_notebook(task)
        elif task.task_type == TaskType.ANOMALY_DETECTION:
            content = self._generate_anomaly_notebook(task)
        elif task.task_type == TaskType.SEGMENTATION:
            content = self._generate_segmentation_notebook(task)
        elif task.task_type == TaskType.VISUALIZATION:
            content = self._generate_visualization_notebook(task)
        else:
            content = self._generate_custom_notebook(task)
        
        # Save notebook
        with open(notebook_path, 'w') as f:
            f.write(content)
        
        task.marimo_notebook_path = str(notebook_path)
        logger.info(f"Generated Marimo notebook for task {task.id}")
        
        return str(notebook_path)
    
    def _generate_profiling_notebook(self, task: AnalysisTask) -> str:
        """Generate data profiling notebook"""
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="profiling",
            output_var="profiling_results",
            additional_code="""
# Data Profiling Analysis
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"Data types:\\n{df.dtypes}")
print(f"Missing values:\\n{df.isnull().sum()}")
print(f"Summary statistics:\\n{df.describe()}")

# Create profiling report
profiling_results = {
    'shape': df.shape,
    'columns': list(df.columns),
    'dtypes': df.dtypes.to_dict(),
    'missing': df.isnull().sum().to_dict(),
    'summary': df.describe().to_dict(),
    'memory_usage': df.memory_usage().sum() / 1024**2  # MB
}
"""
        )
    
    def _generate_statistical_notebook(self, task: AnalysisTask) -> str:
        """Generate statistical analysis notebook"""
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="statistical",
            output_var="statistical_results",
            additional_code="""
# Statistical Analysis
from scipy import stats
import numpy as np

numerical_cols = df.select_dtypes(include=[np.number]).columns

# Perform statistical tests
statistical_results = {}

for col in numerical_cols:
    # Normality test
    statistic, p_value = stats.normaltest(df[col].dropna())
    
    statistical_results[col] = {
        'mean': df[col].mean(),
        'median': df[col].median(),
        'std': df[col].std(),
        'skew': df[col].skew(),
        'kurtosis': df[col].kurtosis(),
        'normality_test': {'statistic': statistic, 'p_value': p_value},
        'is_normal': p_value > 0.05
    }

print("Statistical Analysis Complete")
"""
        )
    
    def _generate_correlation_notebook(self, task: AnalysisTask) -> str:
        """Generate correlation analysis notebook"""
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="correlation",
            output_var="correlation_results",
            additional_code="""
# Correlation Analysis
import seaborn as sns
import matplotlib.pyplot as plt

# Calculate correlations
numerical_df = df.select_dtypes(include=[np.number])
correlation_matrix = numerical_df.corr()

# Find strong correlations
strong_correlations = []
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        if abs(correlation_matrix.iloc[i, j]) > 0.5:
            strong_correlations.append({
                'var1': correlation_matrix.columns[i],
                'var2': correlation_matrix.columns[j],
                'correlation': correlation_matrix.iloc[i, j]
            })

# Create heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.tight_layout()

correlation_results = {
    'correlation_matrix': correlation_matrix.to_dict(),
    'strong_correlations': strong_correlations,
    'highly_correlated_pairs': len(strong_correlations)
}
"""
        )
    
    def _generate_timeseries_notebook(self, task: AnalysisTask) -> str:
        """Generate time series analysis notebook"""
        date_column = task.parameters.get('date_column', 'date')
        value_column = task.parameters.get('value_column', 'value')
        
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="timeseries",
            output_var="timeseries_results",
            additional_code=f"""
# Time Series Analysis
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

# Convert to datetime if needed
if '{date_column}' in df.columns:
    df['{date_column}'] = pd.to_datetime(df['{date_column}'])
    df = df.sort_values('{date_column}')
    df = df.set_index('{date_column}')

# Select value column
if '{value_column}' in df.columns:
    ts_data = df['{value_column}']
else:
    # Use first numeric column
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    ts_data = df[numeric_cols[0]] if len(numeric_cols) > 0 else df.iloc[:, 0]

# Perform decomposition if enough data
timeseries_results = {{
    'data_points': len(ts_data),
    'start_date': str(ts_data.index[0]),
    'end_date': str(ts_data.index[-1]),
    'mean': ts_data.mean(),
    'std': ts_data.std(),
    'trend': 'increasing' if ts_data.iloc[-1] > ts_data.iloc[0] else 'decreasing'
}}

if len(ts_data) > 24:  # Need enough data for decomposition
    decomposition = seasonal_decompose(ts_data, model='additive', period=min(12, len(ts_data)//2))
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    ts_data.plot(ax=axes[0], title='Original')
    decomposition.trend.plot(ax=axes[1], title='Trend')
    decomposition.seasonal.plot(ax=axes[2], title='Seasonal')
    decomposition.resid.plot(ax=axes[3], title='Residual')
    plt.tight_layout()
    
    timeseries_results['has_seasonality'] = True
    timeseries_results['trend_strength'] = decomposition.trend.std() / ts_data.std()
"""
        )
    
    def _generate_predictive_notebook(self, task: AnalysisTask) -> str:
        """Generate predictive modeling notebook"""
        target = task.parameters.get('target_column', 'target')
        
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="predictive",
            output_var="model_results",
            additional_code=f"""
# Predictive Modeling
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_squared_error, accuracy_score, r2_score
import numpy as np

# Prepare data
target_col = '{target}' if '{target}' in df.columns else df.columns[-1]
feature_cols = [col for col in df.select_dtypes(include=[np.number]).columns if col != target_col]

if len(feature_cols) == 0:
    model_results = {{'error': 'No numeric features found'}}
else:
    X = df[feature_cols].fillna(0)
    y = df[target_col]
    
    # Check if regression or classification
    if y.dtype == 'object' or y.nunique() < 10:
        # Classification
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        metric = 'accuracy'
    else:
        # Regression
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        metric = 'r2_score'
    
    # Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred = model.predict(X_test)
    
    # Evaluate
    if metric == 'accuracy':
        score = accuracy_score(y_test, y_pred)
    else:
        score = r2_score(y_test, y_pred)
    
    # Feature importance
    feature_importance = dict(zip(feature_cols, model.feature_importances_))
    
    model_results = {{
        'model_type': type(model).__name__,
        'metric': metric,
        'score': score,
        'n_features': len(feature_cols),
        'n_samples_train': len(X_train),
        'n_samples_test': len(X_test),
        'feature_importance': feature_importance,
        'top_features': sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
    }}
    
    print(f"Model Score ({{metric}}): {{score:.4f}}")
"""
        )
    
    def _generate_anomaly_notebook(self, task: AnalysisTask) -> str:
        """Generate anomaly detection notebook"""
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="anomaly",
            output_var="anomaly_results",
            additional_code="""
# Anomaly Detection
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np

# Select numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
X = df[numeric_cols].fillna(0)

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Isolation Forest
iso_forest = IsolationForest(contamination=0.1, random_state=42)
anomaly_labels = iso_forest.fit_predict(X_scaled)

# Get anomalies
anomalies = df[anomaly_labels == -1]
normal = df[anomaly_labels == 1]

# Statistical outliers (IQR method)
Q1 = df[numeric_cols].quantile(0.25)
Q3 = df[numeric_cols].quantile(0.75)
IQR = Q3 - Q1
outliers_mask = ((df[numeric_cols] < (Q1 - 1.5 * IQR)) | (df[numeric_cols] > (Q3 + 1.5 * IQR))).any(axis=1)
statistical_outliers = df[outliers_mask]

anomaly_results = {
    'total_records': len(df),
    'anomalies_detected': len(anomalies),
    'anomaly_percentage': len(anomalies) / len(df) * 100,
    'statistical_outliers': len(statistical_outliers),
    'anomaly_indices': anomalies.index.tolist()[:100],  # First 100
    'anomaly_summary': anomalies[numeric_cols].describe().to_dict() if len(anomalies) > 0 else {}
}

print(f"Anomalies detected: {len(anomalies)} ({anomaly_results['anomaly_percentage']:.2f}%)")
"""
        )
    
    def _generate_segmentation_notebook(self, task: AnalysisTask) -> str:
        """Generate segmentation notebook"""
        n_clusters = task.parameters.get('n_clusters', 4)
        
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="segmentation",
            output_var="segmentation_results",
            additional_code=f"""
# Customer/Data Segmentation
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Select features for clustering
numeric_cols = df.select_dtypes(include=[np.number]).columns
X = df[numeric_cols].fillna(0)

# Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Determine optimal clusters using elbow method
inertias = []
K_range = range(2, min(10, len(df)//10))
for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(X_scaled)
    inertias.append(kmeans.inertia_)

# Use specified or optimal number of clusters
n_clusters = {n_clusters}
kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# Add clusters to dataframe
df['cluster'] = clusters

# Analyze segments
segment_profiles = []
for cluster_id in range(n_clusters):
    cluster_data = df[df['cluster'] == cluster_id]
    profile = {{
        'cluster_id': cluster_id,
        'size': len(cluster_data),
        'percentage': len(cluster_data) / len(df) * 100,
        'mean_values': cluster_data[numeric_cols].mean().to_dict()
    }}
    segment_profiles.append(profile)

segmentation_results = {{
    'n_clusters': n_clusters,
    'cluster_sizes': df['cluster'].value_counts().to_dict(),
    'segment_profiles': segment_profiles,
    'inertia': kmeans.inertia_,
    'silhouette_score': 0.0  # Would calculate if needed
}}

# Visualize
if len(numeric_cols) >= 2:
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(X.iloc[:, 0], X.iloc[:, 1], c=clusters, cmap='viridis')
    plt.colorbar(scatter)
    plt.xlabel(numeric_cols[0])
    plt.ylabel(numeric_cols[1])
    plt.title(f'Segmentation Results ({{n_clusters}} clusters)')
    plt.show()

print(f"Created {{n_clusters}} segments")
"""
        )
    
    def _generate_visualization_notebook(self, task: AnalysisTask) -> str:
        """Generate visualization notebook"""
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="visualization",
            output_var="visualization_results",
            additional_code="""
# Data Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Create multiple visualizations
num_plots = 0

# 1. Distribution plots for numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0:
    fig, axes = plt.subplots(min(3, len(numeric_cols)), 2, figsize=(12, 4*min(3, len(numeric_cols))))
    axes = axes.flatten() if len(numeric_cols) > 1 else [axes]
    
    for i, col in enumerate(numeric_cols[:6]):
        axes[i].hist(df[col].dropna(), bins=30, edgecolor='black')
        axes[i].set_title(f'Distribution of {col}')
        axes[i].set_xlabel(col)
        axes[i].set_ylabel('Frequency')
        num_plots += 1
    
    plt.tight_layout()
    plt.show()

# 2. Correlation heatmap
if len(numeric_cols) > 1:
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[numeric_cols].corr(), annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Heatmap')
    plt.show()
    num_plots += 1

# 3. Time series plot if date column exists
date_cols = df.select_dtypes(include=['datetime64']).columns
if len(date_cols) > 0 and len(numeric_cols) > 0:
    plt.figure(figsize=(12, 6))
    for col in numeric_cols[:3]:
        plt.plot(df[date_cols[0]], df[col], label=col, alpha=0.7)
    plt.xlabel(date_cols[0])
    plt.ylabel('Values')
    plt.title('Time Series Plot')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    num_plots += 1

visualization_results = {
    'plots_created': num_plots,
    'numeric_columns': len(numeric_cols),
    'categorical_columns': len(df.select_dtypes(include=['object']).columns),
    'visualizations': ['distribution', 'correlation', 'timeseries'] if num_plots >= 3 else ['distribution', 'correlation']
}

print(f"Created {num_plots} visualizations")
"""
        )
    
    def _generate_custom_notebook(self, task: AnalysisTask) -> str:
        """Generate custom notebook based on parameters"""
        custom_code = task.parameters.get('custom_code', '# Custom analysis code here')
        
        return self.notebook_generator.generate_notebook(
            data_path=task.data_source or "data.csv",
            analysis_type="custom",
            output_var="custom_results",
            additional_code=custom_code
        )
    
    # === Task Execution ===
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a task by running its Marimo notebook"""
        if task_id not in self.tasks:
            return {'error': 'Task not found'}
        
        task = self.tasks[task_id]
        
        try:
            # Update status
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            
            # Generate Marimo notebook if not exists
            if not task.marimo_notebook_path:
                self.generate_marimo_notebook(task)
            
            # Update status
            task.status = TaskStatus.MARIMO_RUNNING
            
            # Run notebook
            logger.info(f"Running Marimo notebook for task {task.id}")
            result = self.notebook_runner.run_notebook(
                task.marimo_notebook_path,
                inputs={'task_id': task.id, 'parameters': task.parameters}
            )
            
            # Process results
            if 'error' in result:
                task.status = TaskStatus.FAILED
                task.error = result['error']
                logger.error(f"Task {task.id} failed: {result['error']}")
            else:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.results = result.get('output', {})
                
                # Save results
                self._save_task_results(task)
                logger.info(f"Task {task.id} completed successfully")
            
            # Update user workload
            if task.assigned_to and task.assigned_to in self.users:
                self.users[task.assigned_to].workload = max(0, self.users[task.assigned_to].workload - 1)
            
            return task.results or {'status': 'completed'}
            
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {'error': str(e)}
    
    def execute_plan(self, plan_id: str) -> Dict[str, Any]:
        """Execute all tasks in a plan"""
        if plan_id not in self.plans:
            return {'error': 'Plan not found'}
        
        plan = self.plans[plan_id]
        results = {'plan_id': plan_id, 'tasks': {}}
        
        # Auto-assign tasks
        self.auto_assign_tasks()
        
        # Execute tasks with dependency management
        completed_tasks = set()
        max_iterations = len(plan.tasks) * 2
        iteration = 0
        
        while len(completed_tasks) < len(plan.tasks) and iteration < max_iterations:
            iteration += 1
            tasks_to_execute = []
            
            for task in plan.tasks:
                if task.id in completed_tasks:
                    continue
                
                # Check dependencies
                deps_met = all(dep in completed_tasks for dep in task.dependencies)
                
                if deps_met:
                    tasks_to_execute.append(task)
            
            if not tasks_to_execute:
                break
            
            # Execute tasks in parallel
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def execute_batch():
                tasks = [self.execute_task(t.id) for t in tasks_to_execute]
                return await asyncio.gather(*tasks)
            
            batch_results = loop.run_until_complete(execute_batch())
            loop.close()
            
            # Process results
            for task, result in zip(tasks_to_execute, batch_results):
                results['tasks'][task.id] = result
                if 'error' not in result:
                    completed_tasks.add(task.id)
        
        # Update plan status
        if len(completed_tasks) == len(plan.tasks):
            plan.status = "completed"
            logger.info(f"Plan {plan.name} completed successfully")
        else:
            logger.warning(f"Plan {plan.name} partially completed: {len(completed_tasks)}/{len(plan.tasks)} tasks")
        
        # Generate aggregated results
        results['summary'] = self._aggregate_results(plan, results['tasks'])
        
        return results
    
    def _aggregate_results(self, plan: AnalysisPlan, task_results: Dict) -> Dict:
        """Aggregate results from all tasks"""
        summary = {
            'plan_name': plan.name,
            'total_tasks': len(plan.tasks),
            'completed_tasks': sum(1 for r in task_results.values() if 'error' not in r),
            'failed_tasks': sum(1 for r in task_results.values() if 'error' in r),
            'key_findings': [],
            'recommendations': [],
            'metrics': {}
        }
        
        # Extract key findings and metrics
        for task_id, result in task_results.items():
            if 'error' in result:
                continue
            
            task = self.tasks.get(task_id)
            if not task:
                continue
            
            # Extract based on task type
            if task.task_type == TaskType.DATA_PROFILING:
                if 'shape' in result:
                    summary['metrics']['data_shape'] = result['shape']
                if 'missing' in result:
                    summary['metrics']['missing_values'] = sum(result['missing'].values())
            
            elif task.task_type == TaskType.PREDICTIVE_MODELING:
                if 'score' in result:
                    summary['metrics'][f'model_score_{task.id[:8]}'] = result['score']
                if 'top_features' in result:
                    summary['key_findings'].append(f"Top predictive features: {result['top_features'][:3]}")
            
            elif task.task_type == TaskType.ANOMALY_DETECTION:
                if 'anomaly_percentage' in result:
                    summary['key_findings'].append(f"Anomalies detected: {result['anomaly_percentage']:.2f}%")
            
            elif task.task_type == TaskType.SEGMENTATION:
                if 'n_clusters' in result:
                    summary['key_findings'].append(f"Data segmented into {result['n_clusters']} groups")
        
        # Generate recommendations
        if summary['failed_tasks'] > 0:
            summary['recommendations'].append(f"Review and retry {summary['failed_tasks']} failed tasks")
        
        if 'missing_values' in summary['metrics'] and summary['metrics']['missing_values'] > 0:
            summary['recommendations'].append("Address missing values in the dataset")
        
        return summary
    
    # === Storage Methods ===
    
    def _save_plan(self, plan: AnalysisPlan):
        """Save plan to disk"""
        plan_file = self.plans_dir / f"{plan.id}.json"
        with open(plan_file, 'w') as f:
            json.dump(plan.to_dict(), f, indent=2)
    
    def _save_task_results(self, task: AnalysisTask):
        """Save task results to disk"""
        results_file = self.results_dir / f"{task.id}_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                'task': task.to_dict(),
                'results': task.results
            }, f, indent=2)
    
    def load_plan(self, plan_id: str) -> Optional[AnalysisPlan]:
        """Load plan from disk"""
        plan_file = self.plans_dir / f"{plan_id}.json"
        if plan_file.exists():
            with open(plan_file, 'r') as f:
                data = json.load(f)
                # Reconstruct plan (simplified, would need proper deserialization)
                return data
        return None
    
    # === Dashboard Methods ===
    
    def get_dashboard_data(self) -> Dict:
        """Get dashboard data for UI"""
        return {
            'plans': {
                'total': len(self.plans),
                'active': sum(1 for p in self.plans.values() if p.status == 'active'),
                'completed': sum(1 for p in self.plans.values() if p.status == 'completed')
            },
            'tasks': {
                'total': len(self.tasks),
                'pending': sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
                'in_progress': sum(1 for t in self.tasks.values() if t.status in [TaskStatus.IN_PROGRESS, TaskStatus.MARIMO_RUNNING]),
                'completed': sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED),
                'failed': sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
            },
            'users': {
                'total': len(self.users),
                'by_role': {role.value: sum(1 for u in self.users.values() if u.role == role) 
                           for role in UserRole}
            },
            'recent_plans': [p.to_dict() for p in sorted(self.plans.values(), 
                            key=lambda x: x.created_at, reverse=True)[:5]],
            'recent_tasks': [t.to_dict() for t in sorted(self.tasks.values(),
                            key=lambda x: x.created_at or datetime.min, reverse=True)[:10]]
        }

# === Example Usage ===

def example_workflow():
    """Example of complete workflow"""
    
    # Initialize workflow manager
    wf = WorkflowManager()
    
    # Register users
    manager = User(
        id="mgr_001",
        name="John Manager",
        email="john@company.com",
        role=UserRole.MANAGER
    )
    wf.register_user(manager)
    
    analyst1 = User(
        id="ana_001",
        name="Alice Analyst",
        email="alice@company.com",
        role=UserRole.ANALYST,
        skills=["data_profiling", "statistical_analysis", "visualization"]
    )
    wf.register_user(analyst1)
    
    analyst2 = User(
        id="ana_002",
        name="Bob Associate",
        email="bob@company.com",
        role=UserRole.ASSOCIATE,
        skills=["predictive_modeling", "segmentation"]
    )
    wf.register_user(analyst2)
    
    # Manager creates a plan
    plan = wf.create_plan(
        name="Q4 Sales Analysis",
        description="Comprehensive analysis of Q4 sales performance",
        objectives=[
            "Identify sales trends and patterns",
            "Detect anomalies in transaction data",
            "Predict next quarter revenue",
            "Segment customers by behavior"
        ],
        data_sources=["sales_q4.csv"],
        created_by=manager.id,
        auto_generate_tasks=True
    )
    
    print(f"Created plan with {len(plan.tasks)} tasks")
    
    # Approve and execute plan
    wf.approve_plan(plan.id, manager.id)
    
    # Auto-assign tasks
    assignments = wf.auto_assign_tasks()
    print(f"Assigned {len(assignments)} tasks")
    
    # Execute plan
    results = wf.execute_plan(plan.id)
    
    # Print summary
    if 'summary' in results:
        print("\n=== Plan Execution Summary ===")
        print(f"Completed: {results['summary']['completed_tasks']}/{results['summary']['total_tasks']} tasks")
        print("\nKey Findings:")
        for finding in results['summary']['key_findings']:
            print(f"  - {finding}")
        print("\nRecommendations:")
        for rec in results['summary']['recommendations']:
            print(f"  - {rec}")

if __name__ == "__main__":
    example_workflow()