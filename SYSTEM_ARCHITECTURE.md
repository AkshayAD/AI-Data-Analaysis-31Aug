# 🏗️ AI Data Analysis Platform - System Architecture & Human-in-Loop Design

## 📊 PART 1: CURRENT APPLICATION FLOW DIAGRAM

```mermaid
graph TB
    Start([User Access Application]) --> Upload{Upload Data?}
    Upload -->|Yes| FileValidation[File Validation<br/>- Size Check ≤200MB<br/>- Type Check CSV/Excel<br/>- Encoding Detection]
    Upload -->|No| SampleData[Load Sample Data]
    
    FileValidation --> LoadData[Load into DataFrame<br/>- Memory Management<br/>- Column Detection<br/>- Row Counting]
    SampleData --> LoadData
    
    LoadData --> SessionState[Store in Session State<br/>- uploaded_data<br/>- analysis_results<br/>- current_step]
    
    SessionState --> SelectStep{Select Analysis Step}
    
    SelectStep -->|Step 1| DataOverview[Data Overview<br/>Features:<br/>• Basic Metrics<br/>• Column Types<br/>• Memory Usage<br/>• Summary Stats]
    
    SelectStep -->|Step 2| QualityAnalysis[Quality Analysis<br/>Features:<br/>• Duplicate Detection<br/>• Missing Values<br/>• Outlier Detection<br/>• Type Consistency]
    
    SelectStep -->|Step 3| StatAnalysis[Statistical Analysis<br/>Features:<br/>• Correlation Matrix<br/>• Distribution Analysis<br/>• Strong Correlations<br/>• Skewness/Kurtosis]
    
    SelectStep -->|Step 4| Recommendations[AI Recommendations<br/>Features:<br/>• Action Plan<br/>• Priorities<br/>• Business Insights<br/>• Next Steps]
    
    DataOverview --> GeminiAPI1[Gemini AI Call<br/>Context: Data Summary<br/>Output: Key Findings]
    QualityAnalysis --> GeminiAPI2[Gemini AI Call<br/>Context: Quality Issues<br/>Output: Cleaning Recommendations]
    StatAnalysis --> GeminiAPI3[Gemini AI Call<br/>Context: Patterns<br/>Output: Statistical Insights]
    Recommendations --> GeminiAPI4[Gemini AI Call<br/>Context: All Previous Steps<br/>Output: Action Plan]
    
    GeminiAPI1 --> Visualizations1[Create Visualizations<br/>• Data Types Pie Chart<br/>• Missing Values Bar Chart]
    GeminiAPI2 --> Visualizations2[Create Visualizations<br/>• Outlier Box Plots<br/>• Quality Metrics]
    GeminiAPI3 --> Visualizations3[Create Visualizations<br/>• Correlation Heatmap<br/>• Scatter Plots]
    GeminiAPI4 --> Visualizations4[Create Visualizations<br/>• Completion Status<br/>• Priority Matrix]
    
    Visualizations1 --> DisplayResults[Display Results<br/>• 4 Tabs Interface<br/>• Charts Tab<br/>• AI Insights Tab<br/>• Metrics Tab<br/>• Export Tab]
    Visualizations2 --> DisplayResults
    Visualizations3 --> DisplayResults
    Visualizations4 --> DisplayResults
    
    DisplayResults --> Export{Export Options}
    Export -->|JSON| ExportJSON[Download JSON Report]
    Export -->|CSV| ExportCSV[Download CSV Metrics]
    Export -->|TXT| ExportTXT[Download Text Summary]
    Export -->|Complete| ExportFull[Full Analysis Report]
    
    DisplayResults --> NextAction{Next Action?}
    NextAction -->|Continue| SelectStep
    NextAction -->|New Analysis| Start
    NextAction -->|End| End([Session Complete])
```

## 🔄 PART 2: HUMAN-IN-THE-LOOP SYSTEM DESIGN WITH MARIMO

### Architecture Overview

```mermaid
graph LR
    subgraph Frontend[Streamlit Frontend]
        UI[User Interface<br/>Port 8504]
        SessionMgr[Session Manager]
        FileUpload[File Handler]
    end
    
    subgraph Orchestrator[Python Orchestrator Service]
        TaskQueue[Task Queue<br/>Redis/RQ]
        WorkflowEngine[Workflow Engine<br/>Prefect/Dagster]
        StateManager[State Manager]
        APIGateway[API Gateway<br/>FastAPI]
    end
    
    subgraph MarimoEngine[Marimo Notebook Engine]
        MarimoServer[Marimo Server<br/>Port 2718]
        NotebookPool[Notebook Pool<br/>• Data Exploration<br/>• Statistical Analysis<br/>• ML Models<br/>• Custom Analysis]
        KernelManager[Kernel Manager]
    end
    
    subgraph HumanLoop[Human-in-Loop Layer]
        ReviewQueue[Review Queue]
        ApprovalGate[Approval Gates]
        FeedbackLoop[Feedback System]
        AuditLog[Audit Trail]
    end
    
    subgraph AIServices[AI Services]
        Gemini[Gemini API]
        LocalLLM[Local LLM<br/>Ollama/LlamaCpp]
        EmbeddingService[Embedding Service]
        VectorDB[Vector Store<br/>ChromaDB/Qdrant]
    end
    
    subgraph DataLayer[Data Layer]
        PostgreSQL[(PostgreSQL<br/>Metadata)]
        MinIO[MinIO/S3<br/>File Storage]
        Redis[(Redis<br/>Cache & Queue)]
    end
    
    UI <--> APIGateway
    APIGateway <--> TaskQueue
    TaskQueue <--> WorkflowEngine
    WorkflowEngine <--> MarimoServer
    WorkflowEngine <--> ReviewQueue
    ReviewQueue <--> ApprovalGate
    ApprovalGate <--> FeedbackLoop
    WorkflowEngine <--> Gemini
    MarimoServer <--> KernelManager
    APIGateway <--> StateManager
    StateManager <--> PostgreSQL
    FileUpload <--> MinIO
    TaskQueue <--> Redis
    FeedbackLoop <--> AuditLog
    AuditLog <--> PostgreSQL
```

## 📋 PART 3: DETAILED IMPLEMENTATION PLAN

### Phase 1: Core Infrastructure (Week 1)

#### 1.1 Backend Services Setup
```python
# File: backend/orchestrator.py
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisTask(BaseModel):
    task_id: str
    task_type: str
    data_path: str
    parameters: Dict[str, Any]
    status: TaskStatus
    marimo_notebook: Optional[str]
    human_review_required: bool
    approval_metadata: Optional[Dict]
    result_path: Optional[str]

class OrchestrationService:
    def __init__(self):
        self.app = FastAPI()
        self.task_queue = []
        self.active_sessions = {}
        self.marimo_pool = MarimoNotebookPool()
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.post("/api/v1/analysis/submit")
        async def submit_analysis(task: AnalysisTask):
            # Queue task for processing
            pass
        
        @self.app.get("/api/v1/analysis/{task_id}/status")
        async def get_task_status(task_id: str):
            # Return current task status
            pass
        
        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint(websocket: WebSocket, session_id: str):
            # Real-time updates for human-in-loop
            pass
```

#### 1.2 Marimo Integration Service
```python
# File: backend/marimo_service.py
import marimo as mo
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio

class MarimoNotebookPool:
    def __init__(self, pool_size: int = 5):
        self.pool_size = pool_size
        self.available_kernels = []
        self.busy_kernels = {}
        self.notebook_templates = self.load_templates()
    
    def load_templates(self) -> Dict[str, Path]:
        """Load predefined Marimo notebook templates"""
        templates = {
            "data_exploration": Path("notebooks/data_exploration.py"),
            "statistical_analysis": Path("notebooks/statistical_analysis.py"),
            "ml_pipeline": Path("notebooks/ml_pipeline.py"),
            "custom_analysis": Path("notebooks/custom_analysis.py"),
            "human_review": Path("notebooks/human_review.py")
        }
        return templates
    
    async def execute_notebook(
        self,
        notebook_type: str,
        data_path: str,
        parameters: Dict[str, Any],
        require_human_review: bool = False
    ) -> Dict[str, Any]:
        """Execute a Marimo notebook with given parameters"""
        
        # Create dynamic notebook with parameters
        notebook_path = self.create_dynamic_notebook(
            notebook_type, data_path, parameters
        )
        
        if require_human_review:
            # Launch interactive Marimo session
            result = await self.launch_interactive_session(notebook_path)
        else:
            # Execute headless
            result = await self.execute_headless(notebook_path)
        
        return result
    
    def create_dynamic_notebook(
        self,
        notebook_type: str,
        data_path: str,
        parameters: Dict[str, Any]
    ) -> Path:
        """Generate a Marimo notebook with injected parameters"""
        
        template = self.notebook_templates[notebook_type]
        
        # Dynamic notebook content
        notebook_content = f'''
import marimo as mo
import pandas as pd
import plotly.express as px
from pathlib import Path

# Injected parameters
DATA_PATH = "{data_path}"
PARAMETERS = {json.dumps(parameters)}

# Load data
df = pd.read_csv(DATA_PATH)

# Analysis cells will be added here based on template
'''
        
        # Add template-specific cells
        with open(template, 'r') as f:
            template_content = f.read()
            notebook_content += template_content
        
        # Save dynamic notebook
        dynamic_path = Path(f"temp/notebook_{notebook_type}_{id(parameters)}.py")
        dynamic_path.write_text(notebook_content)
        
        return dynamic_path
```

### Phase 2: Human-in-Loop Components (Week 2)

#### 2.1 Review Queue System
```python
# File: backend/human_loop.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio
from asyncio import Queue

@dataclass
class ReviewRequest:
    request_id: str
    task_id: str
    review_type: str  # "approval", "correction", "validation"
    data_snapshot: Dict[str, Any]
    marimo_notebook_url: str
    created_at: datetime
    deadline: Optional[datetime]
    priority: int  # 1-5, 5 being highest
    reviewer_notes: Optional[str]
    decision: Optional[str]  # "approved", "rejected", "modify"
    feedback: Optional[str]

class HumanReviewQueue:
    def __init__(self):
        self.pending_reviews: Queue = Queue()
        self.active_reviews: Dict[str, ReviewRequest] = {}
        self.completed_reviews: List[ReviewRequest] = []
        self.websocket_connections = {}
    
    async def submit_for_review(
        self,
        task_id: str,
        review_type: str,
        data: Dict[str, Any],
        notebook_url: str,
        priority: int = 3
    ) -> str:
        """Submit a task for human review"""
        
        review = ReviewRequest(
            request_id=self.generate_review_id(),
            task_id=task_id,
            review_type=review_type,
            data_snapshot=data,
            marimo_notebook_url=notebook_url,
            created_at=datetime.now(),
            deadline=None,
            priority=priority,
            reviewer_notes=None,
            decision=None,
            feedback=None
        )
        
        await self.pending_reviews.put((priority, review))
        await self.notify_reviewers(review)
        
        return review.request_id
    
    async def notify_reviewers(self, review: ReviewRequest):
        """Send notifications to available reviewers"""
        
        notification = {
            "type": "new_review",
            "review_id": review.request_id,
            "task_id": review.task_id,
            "priority": review.priority,
            "review_type": review.review_type,
            "notebook_url": review.marimo_notebook_url
        }
        
        # Send to all connected WebSocket clients
        for session_id, ws in self.websocket_connections.items():
            await ws.send_json(notification)
    
    async def process_review_decision(
        self,
        review_id: str,
        decision: str,
        feedback: Optional[str] = None,
        modifications: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process human reviewer's decision"""
        
        review = self.active_reviews.get(review_id)
        if not review:
            raise ValueError(f"Review {review_id} not found")
        
        review.decision = decision
        review.feedback = feedback
        
        if decision == "approved":
            # Continue with automated pipeline
            result = await self.continue_pipeline(review.task_id)
        elif decision == "rejected":
            # Stop pipeline and log reason
            result = await self.stop_pipeline(review.task_id, feedback)
        elif decision == "modify":
            # Apply modifications and resubmit
            result = await self.modify_and_resubmit(
                review.task_id, modifications
            )
        
        self.completed_reviews.append(review)
        del self.active_reviews[review_id]
        
        return result
```

#### 2.2 Interactive Marimo Session Manager
```python
# File: backend/marimo_interactive.py
import marimo as mo
from typing import Dict, Any, Optional
import asyncio
import uuid
import subprocess
import json

class InteractiveMarimoSession:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.port = self.allocate_port()
        self.process = None
        self.notebook_path = None
        self.state = "initialized"
    
    def allocate_port(self) -> int:
        """Allocate a unique port for this Marimo session"""
        # Port allocation logic
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    async def launch(
        self,
        notebook_path: Path,
        data_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Launch an interactive Marimo session"""
        
        self.notebook_path = notebook_path
        
        # Prepare context file
        context_path = Path(f"temp/context_{self.session_id}.json")
        context_path.write_text(json.dumps(data_context))
        
        # Launch Marimo server
        cmd = [
            "marimo", "edit",
            str(notebook_path),
            "--port", str(self.port),
            "--no-browser",
            "--headless"
        ]
        
        self.process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        self.state = "running"
        
        return {
            "session_id": self.session_id,
            "notebook_url": f"http://localhost:{self.port}",
            "state": self.state
        }
    
    async def get_notebook_state(self) -> Dict[str, Any]:
        """Get current state of the notebook"""
        # Connect to Marimo API and get cell states
        pass
    
    async def execute_cell(self, cell_id: str, code: str) -> Dict[str, Any]:
        """Execute a specific cell in the notebook"""
        # Send execution request to Marimo
        pass
    
    async def save_and_export(self) -> Dict[str, Any]:
        """Save notebook state and export results"""
        # Export notebook and results
        pass
    
    async def terminate(self):
        """Terminate the Marimo session"""
        if self.process:
            self.process.terminate()
            await self.process.wait()
        self.state = "terminated"
```

### Phase 3: Marimo Notebook Templates (Week 3)

#### 3.1 Data Exploration Notebook Template
```python
# File: notebooks/data_exploration.py
import marimo as mo
import pandas as pd
import plotly.express as px
import numpy as np
from typing import Dict, List, Any
import json

# Cell 1: Load Configuration
config = mo.md("""
# Data Exploration Notebook
This notebook provides interactive data exploration with human-in-loop controls.
""")

# Cell 2: Data Loading with Validation
data_loader = mo.ui.file_upload(
    accept=[".csv", ".parquet", ".json"],
    multiple=False,
    label="Upload dataset for exploration"
)

@mo.cell
def load_data():
    if data_loader.value:
        df = pd.read_csv(data_loader.value)
        return df
    return None

# Cell 3: Human Review Point - Data Quality Check
review_gate_1 = mo.ui.form({
    "data_quality": mo.ui.radio(
        ["Good", "Needs Cleaning", "Unacceptable"],
        label="Data Quality Assessment"
    ),
    "issues": mo.ui.text_area(
        label="Identified Issues",
        placeholder="List any data quality issues..."
    ),
    "action": mo.ui.select(
        ["Continue", "Clean Data", "Reject"],
        label="Recommended Action"
    )
})

@mo.cell
def quality_review(df):
    if df is not None:
        quality_report = {
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": df.duplicated().sum(),
            "dtypes": df.dtypes.to_dict(),
            "shape": df.shape
        }
        
        mo.md(f"""
        ## Data Quality Report
        - **Shape**: {quality_report['shape']}
        - **Duplicates**: {quality_report['duplicates']}
        - **Missing Values**: {sum(quality_report['missing_values'].values())}
        """)
        
        return quality_report

# Cell 4: Interactive Exploration Tools
exploration_controls = mo.ui.form({
    "x_axis": mo.ui.select([], label="X Axis"),
    "y_axis": mo.ui.select([], label="Y Axis"),
    "color": mo.ui.select([], label="Color By"),
    "chart_type": mo.ui.select(
        ["scatter", "line", "bar", "histogram", "box"],
        label="Chart Type"
    )
})

@mo.cell
def interactive_viz(df, controls):
    if df is not None and controls:
        # Update control options based on dataframe columns
        controls["x_axis"].options = df.columns.tolist()
        controls["y_axis"].options = df.columns.tolist()
        controls["color"].options = ["None"] + df.columns.tolist()
        
        if controls.submitted:
            chart_type = controls.value["chart_type"]
            x = controls.value["x_axis"]
            y = controls.value["y_axis"]
            color = controls.value["color"] if controls.value["color"] != "None" else None
            
            if chart_type == "scatter":
                fig = px.scatter(df, x=x, y=y, color=color)
            elif chart_type == "line":
                fig = px.line(df, x=x, y=y, color=color)
            elif chart_type == "bar":
                fig = px.bar(df, x=x, y=y, color=color)
            elif chart_type == "histogram":
                fig = px.histogram(df, x=x, color=color)
            elif chart_type == "box":
                fig = px.box(df, x=x, y=y, color=color)
            
            return fig

# Cell 5: Statistical Analysis with Human Validation
statistical_review = mo.ui.form({
    "correlation_threshold": mo.ui.slider(
        0.5, 1.0, 0.7,
        step=0.05,
        label="Correlation Threshold"
    ),
    "outlier_method": mo.ui.select(
        ["IQR", "Z-Score", "Isolation Forest"],
        label="Outlier Detection Method"
    ),
    "approve_findings": mo.ui.checkbox(
        label="Approve Statistical Findings"
    )
})

@mo.cell
def statistical_analysis(df, params):
    if df is not None and params.submitted:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Correlation analysis
        corr_matrix = df[numeric_cols].corr()
        high_corr = []
        threshold = params.value["correlation_threshold"]
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > threshold:
                    high_corr.append({
                        "var1": corr_matrix.columns[i],
                        "var2": corr_matrix.columns[j],
                        "correlation": corr_matrix.iloc[i, j]
                    })
        
        # Outlier detection
        outliers = detect_outliers(df, params.value["outlier_method"])
        
        return {
            "high_correlations": high_corr,
            "outliers": outliers,
            "approved": params.value["approve_findings"]
        }

# Cell 6: Export Results with Audit Trail
export_controls = mo.ui.form({
    "export_format": mo.ui.select(
        ["JSON", "CSV", "Parquet", "HTML Report"],
        label="Export Format"
    ),
    "include_viz": mo.ui.checkbox(
        label="Include Visualizations"
    ),
    "reviewer_name": mo.ui.text(
        label="Reviewer Name"
    ),
    "review_notes": mo.ui.text_area(
        label="Review Notes"
    )
})

@mo.cell
def export_results(df, analysis_results, export_params):
    if export_params.submitted:
        audit_trail = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "reviewer": export_params.value["reviewer_name"],
            "notes": export_params.value["review_notes"],
            "decisions": {
                "data_quality": review_gate_1.value,
                "statistical_approval": statistical_review.value
            }
        }
        
        export_package = {
            "data_summary": df.describe().to_dict() if df is not None else {},
            "analysis": analysis_results,
            "audit": audit_trail
        }
        
        # Export based on format
        format_type = export_params.value["export_format"]
        if format_type == "JSON":
            output_path = f"exports/analysis_{audit_trail['timestamp']}.json"
            with open(output_path, 'w') as f:
                json.dump(export_package, f, indent=2)
        
        mo.md(f"✅ Results exported to {output_path}")
        
        return export_package
```

### Phase 4: Integration Layer (Week 4)

#### 4.1 Streamlit-Orchestrator Bridge
```python
# File: streamlit_orchestrator_bridge.py
import streamlit as st
import requests
import asyncio
import websocket
import json
from typing import Dict, Any, Optional
import pandas as pd

class OrchestratorBridge:
    def __init__(self, orchestrator_url: str = "http://localhost:8000"):
        self.base_url = orchestrator_url
        self.session_id = st.session_state.get("session_id", None)
        self.ws_connection = None
        
    def submit_analysis_task(
        self,
        data: pd.DataFrame,
        analysis_type: str,
        parameters: Dict[str, Any],
        require_human_review: bool = False
    ) -> str:
        """Submit analysis task to orchestrator"""
        
        # Save data to temp location
        data_path = f"/tmp/data_{self.session_id}.csv"
        data.to_csv(data_path, index=False)
        
        # Prepare task request
        task_request = {
            "task_type": analysis_type,
            "data_path": data_path,
            "parameters": parameters,
            "human_review_required": require_human_review,
            "session_id": self.session_id
        }
        
        # Submit to orchestrator
        response = requests.post(
            f"{self.base_url}/api/v1/analysis/submit",
            json=task_request
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["task_id"]
        else:
            st.error(f"Failed to submit task: {response.text}")
            return None
    
    async def connect_websocket(self):
        """Establish WebSocket connection for real-time updates"""
        
        ws_url = f"ws://localhost:8000/ws/{self.session_id}"
        self.ws_connection = await websocket.connect(ws_url)
        
        # Listen for updates
        async for message in self.ws_connection:
            update = json.loads(message)
            self.handle_update(update)
    
    def handle_update(self, update: Dict[str, Any]):
        """Handle real-time updates from orchestrator"""
        
        update_type = update.get("type")
        
        if update_type == "task_status":
            # Update task status in UI
            st.session_state[f"task_{update['task_id']}_status"] = update["status"]
            
        elif update_type == "human_review_request":
            # Show human review interface
            self.show_review_interface(update)
            
        elif update_type == "marimo_notebook_ready":
            # Embed Marimo notebook in iframe
            self.embed_marimo_notebook(update["notebook_url"])
            
        elif update_type == "analysis_complete":
            # Display final results
            self.display_results(update["results"])
    
    def show_review_interface(self, review_request: Dict[str, Any]):
        """Display human review interface in Streamlit"""
        
        st.warning("🔍 Human Review Required")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Embed Marimo notebook
            st.components.v1.iframe(
                review_request["notebook_url"],
                height=600,
                scrolling=True
            )
        
        with col2:
            st.subheader("Review Controls")
            
            # Review form
            with st.form("review_form"):
                decision = st.radio(
                    "Decision",
                    ["Approve", "Reject", "Modify"],
                    help="Select your review decision"
                )
                
                feedback = st.text_area(
                    "Feedback",
                    placeholder="Provide feedback or reasoning..."
                )
                
                if decision == "Modify":
                    modifications = st.text_area(
                        "Modifications (JSON)",
                        placeholder='{"param1": "new_value"}'
                    )
                else:
                    modifications = None
                
                submit = st.form_submit_button("Submit Review")
                
                if submit:
                    self.submit_review_decision(
                        review_request["review_id"],
                        decision.lower(),
                        feedback,
                        json.loads(modifications) if modifications else None
                    )
```

#### 4.2 Workflow Definition System
```python
# File: workflows/analysis_workflow.py
from prefect import flow, task
from typing import Dict, Any, Optional
import pandas as pd

@task(name="data_validation", retries=2)
async def validate_data(data_path: str) -> Dict[str, Any]:
    """Validate input data"""
    df = pd.read_csv(data_path)
    
    validation_results = {
        "valid": True,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_percentage": (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100,
        "duplicate_rows": df.duplicated().sum()
    }
    
    # Check validation rules
    if validation_results["missing_percentage"] > 50:
        validation_results["valid"] = False
        validation_results["reason"] = "Too many missing values"
    
    return validation_results

@task(name="marimo_analysis")
async def run_marimo_analysis(
    data_path: str,
    notebook_type: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute Marimo notebook for analysis"""
    
    from backend.marimo_service import MarimoNotebookPool
    
    pool = MarimoNotebookPool()
    result = await pool.execute_notebook(
        notebook_type=notebook_type,
        data_path=data_path,
        parameters=parameters,
        require_human_review=parameters.get("require_review", False)
    )
    
    return result

@task(name="human_review_gate")
async def human_review_checkpoint(
    task_id: str,
    data: Dict[str, Any],
    notebook_url: str
) -> Dict[str, Any]:
    """Human review checkpoint"""
    
    from backend.human_loop import HumanReviewQueue
    
    queue = HumanReviewQueue()
    review_id = await queue.submit_for_review(
        task_id=task_id,
        review_type="analysis_validation",
        data=data,
        notebook_url=notebook_url,
        priority=3
    )
    
    # Wait for review decision
    decision = await queue.await_review_decision(review_id)
    
    return decision

@task(name="generate_report")
async def generate_final_report(
    analysis_results: Dict[str, Any],
    audit_trail: Dict[str, Any]
) -> str:
    """Generate final analysis report"""
    
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "analysis": analysis_results,
        "audit": audit_trail,
        "status": "completed"
    }
    
    # Save report
    report_path = f"reports/analysis_{report['timestamp']}.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return report_path

@flow(name="human_in_loop_analysis")
async def analysis_workflow(
    data_path: str,
    analysis_type: str,
    parameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Main analysis workflow with human-in-loop"""
    
    # Step 1: Validate data
    validation = await validate_data(data_path)
    
    if not validation["valid"]:
        return {"status": "failed", "reason": validation["reason"]}
    
    # Step 2: Run initial analysis in Marimo
    initial_analysis = await run_marimo_analysis(
        data_path=data_path,
        notebook_type=analysis_type,
        parameters=parameters
    )
    
    # Step 3: Human review checkpoint (if required)
    if parameters.get("require_human_review", False):
        review_decision = await human_review_checkpoint(
            task_id=initial_analysis["task_id"],
            data=initial_analysis["results"],
            notebook_url=initial_analysis["notebook_url"]
        )
        
        if review_decision["decision"] != "approved":
            return {
                "status": "rejected",
                "reason": review_decision["feedback"]
            }
    
    # Step 4: Generate final report
    report_path = await generate_final_report(
        analysis_results=initial_analysis["results"],
        audit_trail={
            "validation": validation,
            "review": review_decision if parameters.get("require_human_review") else None
        }
    )
    
    return {
        "status": "completed",
        "report_path": report_path,
        "results": initial_analysis["results"]
    }
```

### Phase 5: Deployment Configuration (Week 5)

#### 5.1 Docker Compose Setup
```yaml
# File: docker-compose.yml
version: '3.8'

services:
  # Streamlit Frontend
  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8504:8504"
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8000
      - MARIMO_URL=http://marimo:2718
    volumes:
      - ./data:/app/data
      - ./exports:/app/exports
    depends_on:
      - orchestrator
      - marimo
      - postgres
      - redis

  # FastAPI Orchestrator
  orchestrator:
    build:
      context: .
      dockerfile: Dockerfile.orchestrator
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/analysis_db
      - REDIS_URL=redis://redis:6379
      - MARIMO_SERVICE_URL=http://marimo:2718
    depends_on:
      - postgres
      - redis
      - marimo

  # Marimo Notebook Service
  marimo:
    build:
      context: .
      dockerfile: Dockerfile.marimo
    ports:
      - "2718:2718"
    volumes:
      - ./notebooks:/app/notebooks
      - ./data:/app/data
      - ./temp:/app/temp
    environment:
      - MARIMO_SERVER_PORT=2718
      - MARIMO_ALLOW_REMOTE=true

  # PostgreSQL Database
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=analysis_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis for Queue and Cache
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  # MinIO for Object Storage
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=admin
      - MINIO_ROOT_PASSWORD=admin123
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

  # Prefect Server for Workflow Orchestration
  prefect:
    image: prefecthq/prefect:2-python3.11
    ports:
      - "4200:4200"
    environment:
      - PREFECT_API_URL=http://localhost:4200/api
    command: prefect server start --host 0.0.0.0

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

#### 5.2 Kubernetes Deployment (Optional)
```yaml
# File: k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: analysis-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: analysis-platform
  template:
    metadata:
      labels:
        app: analysis-platform
    spec:
      containers:
      - name: streamlit
        image: analysis-platform/streamlit:latest
        ports:
        - containerPort: 8504
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1"
      
      - name: orchestrator
        image: analysis-platform/orchestrator:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
      
      - name: marimo
        image: analysis-platform/marimo:latest
        ports:
        - containerPort: 2718
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "4Gi"
            cpu: "2"
```

## 📊 PART 4: KEY FEATURES & CAPABILITIES

### System Features Matrix

| Component | Features | Technology | Purpose |
|-----------|----------|------------|---------|
| **Frontend** | • File Upload<br>• Real-time Updates<br>• Interactive Review UI<br>• Marimo Embedding | Streamlit, WebSocket | User Interface |
| **Orchestrator** | • Task Queue<br>• Workflow Management<br>• State Tracking<br>• API Gateway | FastAPI, Prefect, Redis | Process Control |
| **Marimo Engine** | • Interactive Notebooks<br>• Dynamic Execution<br>• Visualization<br>• Export Capabilities | Marimo, Python | Analysis Engine |
| **Human Loop** | • Review Queue<br>• Approval Gates<br>• Feedback System<br>• Audit Trail | Custom Python, PostgreSQL | Quality Control |
| **AI Services** | • Natural Language Analysis<br>• Pattern Recognition<br>• Recommendations<br>• Embeddings | Gemini API, Local LLM | Intelligence Layer |
| **Data Layer** | • File Storage<br>• Metadata DB<br>• Cache<br>• Message Queue | MinIO, PostgreSQL, Redis | Persistence |

### Human-in-Loop Decision Points

1. **Data Quality Gate**: Review data quality before processing
2. **Analysis Validation**: Verify statistical findings
3. **Model Approval**: Approve ML model selections
4. **Result Verification**: Confirm final insights
5. **Export Authorization**: Approve data exports

### Marimo Integration Points

1. **Data Exploration**: Interactive data discovery
2. **Statistical Analysis**: Dynamic statistical computations
3. **Machine Learning**: Model training and evaluation
4. **Visualization**: Interactive charts and plots
5. **Custom Analysis**: User-defined analysis workflows
6. **Review Interface**: Human validation notebooks

## 🚀 DEPLOYMENT STRATEGY

### Production Deployment Steps

1. **Infrastructure Setup**
   - Deploy PostgreSQL, Redis, MinIO
   - Configure networking and security
   - Set up monitoring and logging

2. **Service Deployment**
   - Build and push Docker images
   - Deploy orchestrator service
   - Launch Marimo notebook pools
   - Start Streamlit frontend

3. **Configuration**
   - Set environment variables
   - Configure API keys
   - Set up user authentication
   - Configure review workflows

4. **Testing**
   - Integration tests
   - Load testing
   - Security audit
   - User acceptance testing

5. **Go-Live**
   - Gradual rollout
   - Monitor performance
   - Collect user feedback
   - Iterate and improve

## 📈 SCALABILITY CONSIDERATIONS

- **Horizontal Scaling**: Add more Marimo notebook instances
- **Load Balancing**: Distribute requests across services
- **Caching**: Redis for frequently accessed data
- **Queue Management**: Async task processing
- **Resource Optimization**: Container resource limits
- **Database Pooling**: Connection pool management

This architecture provides a robust, scalable, and maintainable system for AI-powered data analysis with human-in-the-loop capabilities using Marimo notebooks.