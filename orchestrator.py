#!/usr/bin/env python3
"""
LangGraph Orchestrator with Human-in-the-Loop Capabilities
This is the core orchestration engine for the AI Data Analysis Platform
"""

import asyncio
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict

import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from langgraph.graph import StateGraph, END
# Use memory checkpoint for compatibility  
from langgraph.checkpoint.memory import MemorySaver

# Configure paths
DB_PATH = Path("orchestrator.db")
CHECKPOINT_PATH = Path("checkpoints.db")
LOGS_PATH = Path("logs")
LOGS_PATH.mkdir(exist_ok=True)


# ====================
# Enums and Models
# ====================

class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_HUMAN_REVIEW = "awaiting_human_review"
    HUMAN_APPROVED = "human_approved"
    HUMAN_REJECTED = "human_rejected"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(int, Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class ReviewType(str, Enum):
    """Types of human review"""
    APPROVAL = "approval"
    CORRECTION = "correction"
    VALIDATION = "validation"
    QUALITY_CHECK = "quality_check"
    COMPLIANCE = "compliance"


class AnalysisTask(BaseModel):
    """Task model for analysis requests"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str
    data_path: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    confidence_threshold: float = 0.7
    require_human_review: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    human_feedback: Optional[str] = None
    reviewer_id: Optional[str] = None


class HumanReviewRequest(BaseModel):
    """Request for human review"""
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    review_type: ReviewType
    context: Dict[str, Any]
    confidence_score: float
    ai_recommendation: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    decision: Optional[str] = None
    feedback: Optional[str] = None
    reviewer_id: Optional[str] = None


# ====================
# State Management
# ====================

class WorkflowState(TypedDict):
    """State for LangGraph workflow"""
    task_id: str
    task_type: str
    data: Optional[pd.DataFrame]
    parameters: Dict[str, Any]
    confidence_score: float
    requires_human_review: bool
    human_decision: Optional[str]
    human_feedback: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    status: str
    history: List[Dict[str, Any]]


# ====================
# Database Manager
# ====================

class DatabaseManager:
    """Manages persistence for tasks and reviews"""
    
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                task_type TEXT NOT NULL,
                data_path TEXT,
                parameters TEXT,
                status TEXT NOT NULL,
                priority INTEGER,
                confidence_threshold REAL,
                require_human_review BOOLEAN,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                result TEXT,
                human_feedback TEXT,
                reviewer_id TEXT
            )
        """)
        
        # Reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id TEXT PRIMARY KEY,
                task_id TEXT,
                review_type TEXT,
                context TEXT,
                confidence_score REAL,
                ai_recommendation TEXT,
                deadline TIMESTAMP,
                priority INTEGER,
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                decision TEXT,
                feedback TEXT,
                reviewer_id TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            )
        """)
        
        # Audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                log_id TEXT PRIMARY KEY,
                task_id TEXT,
                action TEXT,
                actor TEXT,
                details TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks (task_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_task(self, task: AnalysisTask):
        """Save or update a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.task_id,
            task.task_type,
            task.data_path,
            json.dumps(task.parameters),
            task.status.value,
            task.priority.value,
            task.confidence_threshold,
            task.require_human_review,
            task.created_at.isoformat(),
            task.updated_at.isoformat(),
            task.completed_at.isoformat() if task.completed_at else None,
            task.error_message,
            json.dumps(task.result) if task.result else None,
            task.human_feedback,
            task.reviewer_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_task(self, task_id: str) -> Optional[AnalysisTask]:
        """Retrieve a task by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return AnalysisTask(
            task_id=row[0],
            task_type=row[1],
            data_path=row[2],
            parameters=json.loads(row[3]) if row[3] else {},
            status=TaskStatus(row[4]),
            priority=TaskPriority(row[5]),
            confidence_threshold=row[6],
            require_human_review=row[7],
            created_at=datetime.fromisoformat(row[8]),
            updated_at=datetime.fromisoformat(row[9]),
            completed_at=datetime.fromisoformat(row[10]) if row[10] else None,
            error_message=row[11],
            result=json.loads(row[12]) if row[12] else None,
            human_feedback=row[13],
            reviewer_id=row[14]
        )
    
    def log_audit(self, task_id: str, action: str, actor: str, details: Dict[str, Any]):
        """Log an audit entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO audit_log VALUES (?, ?, ?, ?, ?, ?)
        """, (
            str(uuid.uuid4()),
            task_id,
            action,
            actor,
            json.dumps(details),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_review_request(self, review: HumanReviewRequest):
        """Save a human review request"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO reviews VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            review.review_id,
            review.task_id,
            review.review_type.value,
            json.dumps(review.context),
            review.confidence_score,
            review.ai_recommendation,
            review.deadline.isoformat() if review.deadline else None,
            review.priority.value,
            review.created_at.isoformat(),
            review.completed_at.isoformat() if review.completed_at else None,
            review.decision,
            review.feedback,
            review.reviewer_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_pending_reviews(self) -> List[HumanReviewRequest]:
        """Get all pending review requests"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reviews WHERE decision IS NULL
            ORDER BY priority DESC, created_at ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        reviews = []
        for row in rows:
            reviews.append(HumanReviewRequest(
                review_id=row[0],
                task_id=row[1],
                review_type=ReviewType(row[2]),
                context=json.loads(row[3]),
                confidence_score=row[4],
                ai_recommendation=row[5],
                deadline=datetime.fromisoformat(row[6]) if row[6] else None,
                priority=TaskPriority(row[7]),
                created_at=datetime.fromisoformat(row[8]),
                completed_at=datetime.fromisoformat(row[9]) if row[9] else None,
                decision=row[10],
                feedback=row[11],
                reviewer_id=row[12]
            ))
        
        return reviews
    
    def get_task_audit_trail(self, task_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM audit_log WHERE task_id = ?
            ORDER BY timestamp DESC
        """, (task_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        audit_trail = []
        for row in rows:
            audit_trail.append({
                "log_id": row[0],
                "task_id": row[1],
                "action": row[2],
                "actor": row[3],
                "details": json.loads(row[4]) if row[4] else {},
                "timestamp": row[5]
            })
        
        return audit_trail


# ====================
# Workflow Nodes
# ====================

class WorkflowNodes:
    """Defines the nodes for the LangGraph workflow"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    async def data_validation_node(self, state: WorkflowState) -> Dict:
        """Validate input data"""
        try:
            # Load data if path provided
            if "data_path" in state["parameters"]:
                data_path = Path(state["parameters"]["data_path"])
                if data_path.suffix == ".csv":
                    state["data"] = pd.read_csv(data_path)
                elif data_path.suffix in [".xlsx", ".xls"]:
                    state["data"] = pd.read_excel(data_path)
                else:
                    raise ValueError(f"Unsupported file type: {data_path.suffix}")
            
            # Basic validation
            if state["data"] is not None:
                if state["data"].empty:
                    raise ValueError("Data is empty")
                if state["data"].shape[0] > 1000000:
                    state["requires_human_review"] = True
                    state["confidence_score"] = 0.5
            
            state["status"] = "data_validated"
            state["history"].append({
                "node": "data_validation",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            
        except Exception as e:
            state["error"] = str(e)
            state["status"] = "validation_failed"
            state["history"].append({
                "node": "data_validation",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            })
        
        return state
    
    async def ai_analysis_node(self, state: WorkflowState) -> Dict:
        """Perform AI analysis"""
        try:
            # Extract confidence from parameters if provided, otherwise simulate
            confidence = state["parameters"].get("confidence_score", 0.85)
            
            # Simulate AI analysis with confidence scoring
            analysis_result = {
                "summary": "Data analysis completed",
                "insights": ["Pattern 1", "Pattern 2", "Pattern 3"],
                "recommendations": ["Action 1", "Action 2"],
                "confidence": confidence,
                "recommendation": "Proceed with analysis" if confidence > 0.7 else "Requires human review"
            }
            
            state["result"] = analysis_result
            state["confidence_score"] = confidence
            
            # Check if human review needed based on confidence threshold
            threshold = state["parameters"].get("confidence_threshold", 0.7)
            if confidence < threshold or state.get("requires_human_review"):
                state["requires_human_review"] = True
            
            state["status"] = "analysis_complete"
            state["history"].append({
                "node": "ai_analysis",
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "confidence": state["confidence_score"]
            })
            
        except Exception as e:
            state["error"] = str(e)
            state["status"] = "analysis_failed"
            state["history"].append({
                "node": "ai_analysis",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            })
        
        return state
    
    async def human_review_node(self, state: WorkflowState) -> Dict:
        """Request human review and wait for decision"""
        try:
            # Update task status to awaiting review
            task = self.db.get_task(state["task_id"])
            if task:
                task.status = TaskStatus.AWAITING_HUMAN_REVIEW
                task.updated_at = datetime.now()
                self.db.save_task(task)
            
            # Create review request
            review = HumanReviewRequest(
                task_id=state["task_id"],
                review_type=ReviewType.APPROVAL,
                context={
                    "analysis_result": state["result"],
                    "confidence_score": state["confidence_score"],
                    "data_shape": state["data"].shape if state["data"] is not None else None
                },
                confidence_score=state["confidence_score"],
                ai_recommendation=state["result"].get("recommendation") if state["result"] else None,
                priority=TaskPriority.HIGH if state["confidence_score"] < 0.5 else TaskPriority.MEDIUM
            )
            
            # Store review request in database
            self.db.save_review_request(review)
            
            # Log audit trail
            self.db.log_audit(
                state["task_id"],
                "human_review_requested",
                "system",
                {"review_id": review.review_id, "confidence": state["confidence_score"]}
            )
            
            # Mark state as awaiting review
            state["awaiting_human_review"] = True
            state["review_id"] = review.review_id
            state["status"] = "awaiting_human_review"
            state["history"].append({
                "node": "human_review",
                "timestamp": datetime.now().isoformat(),
                "status": "awaiting_review",
                "review_id": review.review_id
            })
            
            # In production, this would wait for actual human input
            # For testing, check if a decision has been provided
            if not state.get("human_decision"):
                # Wait for human decision (will be set via API)
                state["human_decision"] = None
                state["human_feedback"] = None
            
        except Exception as e:
            state["error"] = str(e)
            state["status"] = "review_failed"
            state["history"].append({
                "node": "human_review",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            })
        
        return state
    
    async def finalization_node(self, state: WorkflowState) -> Dict:
        """Finalize the workflow"""
        try:
            # Update task in database
            task = self.db.get_task(state["task_id"])
            if task:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.result = state["result"]
                task.human_feedback = state.get("human_feedback")
                self.db.save_task(task)
            
            state["status"] = "completed"
            state["history"].append({
                "node": "finalization",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            })
            
            # Log audit
            self.db.log_audit(
                state["task_id"],
                "workflow_completed",
                "system",
                {"result": state["result"], "confidence": state["confidence_score"]}
            )
            
        except Exception as e:
            state["error"] = str(e)
            state["status"] = "finalization_failed"
            state["history"].append({
                "node": "finalization",
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            })
        
        return state


# ====================
# Orchestrator
# ====================

class LangGraphOrchestrator:
    """Main orchestration engine using LangGraph"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.nodes = WorkflowNodes(self.db)
        
        # Initialize checkpoint storage first
        self.checkpointer = MemorySaver()  # Use memory saver for simplicity
        
        # Build workflow after checkpointer is ready
        self.workflow = self._build_workflow()
        self.active_workflows = {}
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("data_validation", self.nodes.data_validation_node)
        workflow.add_node("ai_analysis", self.nodes.ai_analysis_node)
        workflow.add_node("human_review", self.nodes.human_review_node)
        workflow.add_node("finalization", self.nodes.finalization_node)
        
        # Add edges
        workflow.set_entry_point("data_validation")
        
        # Conditional routing based on validation
        workflow.add_conditional_edges(
            "data_validation",
            lambda x: "ai_analysis" if not x.get("error") else END,
            {
                "ai_analysis": "ai_analysis",
                END: END
            }
        )
        
        # Conditional routing based on confidence
        workflow.add_conditional_edges(
            "ai_analysis",
            lambda x: "human_review" if x.get("requires_human_review") else "finalization",
            {
                "human_review": "human_review",
                "finalization": "finalization"
            }
        )
        
        # Human review outcome
        workflow.add_conditional_edges(
            "human_review",
            lambda x: "finalization" if x.get("human_decision") == "approved" else END,
            {
                "finalization": "finalization",
                END: END
            }
        )
        
        # Finalization always ends
        workflow.add_edge("finalization", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def execute_task(self, task: AnalysisTask):
        """Execute a task through the workflow - yields updates"""
        # Initialize state
        initial_state = WorkflowState(
            task_id=task.task_id,
            task_type=task.task_type,
            data=None,
            parameters=task.parameters,
            confidence_score=1.0,
            requires_human_review=task.require_human_review,
            human_decision=None,
            human_feedback=None,
            result=None,
            error=None,
            status="initialized",
            history=[]
        )
        
        # Save task to database
        self.db.save_task(task)
        
        # Execute workflow
        config = {"configurable": {"thread_id": task.task_id}}
        
        try:
            # Run the workflow
            async for output in self.workflow.astream(initial_state, config):
                # Update task status in database
                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = datetime.now()
                self.db.save_task(task)
                
                # Yield intermediate results for real-time updates
                yield output
            
            # Get final state
            final_state = await self.workflow.aget_state(config)
            
            # Update task with final results
            # Check if awaiting human review
            if final_state.values.get("awaiting_human_review"):
                task.status = TaskStatus.AWAITING_HUMAN_REVIEW
            elif final_state.values.get("human_decision") == "rejected":
                task.status = TaskStatus.HUMAN_REJECTED
                task.completed_at = datetime.now()
            elif final_state.values.get("error"):
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
            else:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
            
            task.result = final_state.values.get("result")
            task.error_message = final_state.values.get("error")
            task.human_feedback = final_state.values.get("human_feedback")
            self.db.save_task(task)
            
            yield final_state.values
            
        except Exception as e:
            # Handle workflow errors
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self.db.save_task(task)
            
            raise


# ====================
# FastAPI Application
# ====================

app = FastAPI(title="LangGraph Orchestrator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = LangGraphOrchestrator()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()


# ====================
# API Endpoints
# ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LangGraph Orchestrator",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

# Simpler task endpoints for compatibility
@app.post("/tasks")
async def submit_task_simple(task_data: Dict[str, Any]):
    """Submit a new task (simplified endpoint)"""
    # Ensure confidence_threshold is available in parameters if provided
    if "confidence_threshold" in task_data and "parameters" in task_data:
        task_data["parameters"]["confidence_threshold"] = task_data["confidence_threshold"]
    
    task = AnalysisTask(**task_data)
    
    # Save task to database
    orchestrator.db.save_task(task)
    
    # Start async processing  
    asyncio.create_task(process_task_async(task))
    
    return {"task_id": task.task_id, "status": "accepted"}

@app.get("/tasks/{task_id}")
async def get_task_simple(task_id: str):
    """Get task status (simplified endpoint)"""
    task = orchestrator.db.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task.dict()

@app.post("/tasks/{task_id}/approve")
async def approve_task_simple(task_id: str, data: Dict[str, Any] = {}):
    """Approve a task awaiting human review (simplified endpoint)"""
    task = orchestrator.db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task with approval
    task.status = TaskStatus.HUMAN_APPROVED
    task.human_feedback = data.get("feedback", "Approved")
    task.reviewer_id = data.get("reviewer_id", "test_reviewer")
    task.updated_at = datetime.now()
    orchestrator.db.save_task(task)
    
    # Log audit
    orchestrator.db.log_audit(
        task_id,
        "task_approved",
        task.reviewer_id,
        {"feedback": task.human_feedback}
    )
    
    return {"status": "approved", "task_id": task_id}

@app.post("/tasks/{task_id}/reject")
async def reject_task_simple(task_id: str, data: Dict[str, Any] = {}):
    """Reject a task awaiting human review (simplified endpoint)"""
    task = orchestrator.db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task with rejection  
    task.status = TaskStatus.HUMAN_REJECTED
    task.human_feedback = data.get("feedback", "Rejected")
    task.reviewer_id = data.get("reviewer_id", "test_reviewer")
    task.updated_at = datetime.now()
    orchestrator.db.save_task(task)
    
    # Log audit
    orchestrator.db.log_audit(
        task_id,
        "task_rejected",
        task.reviewer_id,
        {"feedback": task.human_feedback}
    )
    
    return {"status": "rejected", "task_id": task_id}

@app.get("/tasks/{task_id}/audit")
async def get_task_audit_simple(task_id: str):
    """Get audit trail for a task (simplified endpoint)"""
    audit_trail = orchestrator.db.get_task_audit_trail(task_id)
    
    if not audit_trail:
        # Return minimal audit info if no trail exists
        task = orchestrator.db.get_task(task_id)
        if task:
            return {
                "task_id": task_id,
                "reviewer_id": task.reviewer_id,
                "decision": "approved" if task.status == TaskStatus.HUMAN_APPROVED else "rejected" if task.status == TaskStatus.HUMAN_REJECTED else None,
                "feedback": task.human_feedback
            }
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Return the most recent approval/rejection from audit trail
    for entry in audit_trail:
        if entry["action"] in ["task_approved", "task_rejected"]:
            return {
                "task_id": task_id,
                "reviewer_id": entry["actor"],
                "decision": "approved" if entry["action"] == "task_approved" else "rejected",
                "feedback": entry["details"].get("feedback", "")
            }
    
    return {"task_id": task_id, "decision": None}

@app.get("/pending-reviews")
async def get_pending_reviews():
    """Get all tasks pending human review"""
    reviews = orchestrator.db.get_pending_reviews()
    return {"reviews": [r.dict() for r in reviews], "count": len(reviews)}


@app.post("/api/v1/tasks/submit")
async def submit_task(task: AnalysisTask):
    """Submit a new task for processing"""
    try:
        # Start workflow execution in background
        asyncio.create_task(process_task_async(task))
        
        return {
            "task_id": task.task_id,
            "status": "submitted",
            "message": "Task submitted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def process_task_async(task: AnalysisTask):
    """Process task asynchronously and send updates via WebSocket"""
    try:
        async for update in orchestrator.execute_task(task):
            # Send real-time updates via WebSocket
            await manager.broadcast(json.dumps({
                "task_id": task.task_id,
                "update": update,
                "timestamp": datetime.now().isoformat()
            }))
    except Exception as e:
        await manager.broadcast(json.dumps({
            "task_id": task.task_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))


@app.get("/api/v1/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and details"""
    task = orchestrator.db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task.dict()


@app.get("/api/v1/tasks/{task_id}/history")
async def get_task_history(task_id: str):
    """Get task execution history"""
    # Get checkpoint history from LangGraph
    config = {"configurable": {"thread_id": task_id}}
    try:
        state = await orchestrator.workflow.aget_state(config)
        return {
            "task_id": task_id,
            "history": state.values.get("history", []),
            "current_status": state.values.get("status")
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/v1/tasks/{task_id}/approve")
async def approve_task(task_id: str, feedback: str = ""):
    """Approve a task awaiting human review"""
    task = orchestrator.db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.AWAITING_HUMAN_REVIEW:
        raise HTTPException(status_code=400, detail="Task is not awaiting review")
    
    # Update task with approval
    task.status = TaskStatus.HUMAN_APPROVED
    task.human_feedback = feedback
    task.reviewer_id = "user"  # In production, get from auth
    task.updated_at = datetime.now()
    orchestrator.db.save_task(task)
    
    # Resume workflow
    config = {"configurable": {"thread_id": task_id}}
    state = await orchestrator.workflow.aget_state(config)
    state.values["human_decision"] = "approved"
    state.values["human_feedback"] = feedback
    
    # Continue workflow execution
    asyncio.create_task(resume_workflow(task_id, state.values))
    
    return {"status": "approved", "message": "Task approved successfully"}


@app.post("/api/v1/tasks/{task_id}/reject")
async def reject_task(task_id: str, feedback: str = ""):
    """Reject a task awaiting human review"""
    task = orchestrator.db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.AWAITING_HUMAN_REVIEW:
        raise HTTPException(status_code=400, detail="Task is not awaiting review")
    
    # Update task with rejection
    task.status = TaskStatus.HUMAN_REJECTED
    task.human_feedback = feedback
    task.reviewer_id = "user"  # In production, get from auth
    task.updated_at = datetime.now()
    task.completed_at = datetime.now()
    orchestrator.db.save_task(task)
    
    return {"status": "rejected", "message": "Task rejected successfully"}


async def resume_workflow(task_id: str, state: Dict):
    """Resume a paused workflow after human review"""
    config = {"configurable": {"thread_id": task_id}}
    async for update in orchestrator.workflow.astream(None, config, state):
        await manager.broadcast(json.dumps({
            "task_id": task_id,
            "update": update,
            "timestamp": datetime.now().isoformat()
        }))


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for now
            await manager.send_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get system metrics"""
    conn = sqlite3.connect(orchestrator.db.db_path)
    cursor = conn.cursor()
    
    # Get task statistics
    cursor.execute("""
        SELECT status, COUNT(*) 
        FROM tasks 
        GROUP BY status
    """)
    status_counts = dict(cursor.fetchall())
    
    # Get average processing time
    cursor.execute("""
        SELECT AVG((julianday(completed_at) - julianday(created_at)) * 24 * 60 * 60)
        FROM tasks
        WHERE completed_at IS NOT NULL
    """)
    avg_processing_time = cursor.fetchone()[0]
    
    # Get human review statistics
    cursor.execute("""
        SELECT COUNT(*)
        FROM tasks
        WHERE human_feedback IS NOT NULL
    """)
    human_reviewed_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "task_statistics": status_counts,
        "average_processing_time_seconds": avg_processing_time,
        "human_reviewed_tasks": human_reviewed_count,
        "active_connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }


# ====================
# Main Entry Point
# ====================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LangGraph Orchestrator")
    parser.add_argument("--port", type=int, default=8000, help="Port to run on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║        LangGraph Orchestrator with HITL Started         ║
    ╠══════════════════════════════════════════════════════════╣
    ║  API: http://localhost:{args.port}                           ║
    ║  WebSocket: ws://localhost:{args.port}/ws/{{client_id}}        ║
    ║  Docs: http://localhost:{args.port}/docs                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "orchestrator:app",
        host="0.0.0.0",
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )