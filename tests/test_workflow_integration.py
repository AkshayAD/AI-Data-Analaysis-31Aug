#!/usr/bin/env python3
"""
Tests for Workflow Manager and Marimo Integration
"""

import pytest
import tempfile
import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import numpy as np
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src" / "python"))

from workflow.workflow_manager import (
    WorkflowManager, AnalysisPlan, AnalysisTask, User,
    TaskType, TaskStatus, UserRole
)

class TestWorkflowManager:
    """Test workflow management functionality"""
    
    @pytest.fixture
    def workflow_manager(self):
        """Create workflow manager with temp directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield WorkflowManager(workspace_path=tmpdir)
    
    @pytest.fixture
    def sample_users(self, workflow_manager):
        """Create sample users"""
        manager = User(
            id="mgr_001",
            name="Test Manager",
            email="manager@test.com",
            role=UserRole.MANAGER
        )
        workflow_manager.register_user(manager)
        
        analyst = User(
            id="ana_001",
            name="Test Analyst",
            email="analyst@test.com",
            role=UserRole.ANALYST,
            skills=["data_profiling", "statistical_analysis"]
        )
        workflow_manager.register_user(analyst)
        
        associate = User(
            id="aso_001",
            name="Test Associate",
            email="associate@test.com",
            role=UserRole.ASSOCIATE,
            skills=["visualization", "segmentation"]
        )
        workflow_manager.register_user(associate)
        
        return {'manager': manager, 'analyst': analyst, 'associate': associate}
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=100),
                'sales': np.random.randint(1000, 5000, 100),
                'customers': np.random.randint(50, 200, 100),
                'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
                'product': np.random.choice(['A', 'B', 'C'], 100)
            })
            df.to_csv(f.name, index=False)
            return f.name
    
    def test_user_registration(self, workflow_manager):
        """Test user registration"""
        user = User(
            id="test_001",
            name="Test User",
            email="test@example.com",
            role=UserRole.ANALYST
        )
        
        user_id = workflow_manager.register_user(user)
        
        assert user_id == "test_001"
        assert "test_001" in workflow_manager.users
        assert workflow_manager.users["test_001"].name == "Test User"
    
    def test_plan_creation(self, workflow_manager, sample_users):
        """Test creating analysis plan"""
        plan = workflow_manager.create_plan(
            name="Test Analysis Plan",
            description="Test plan for unit testing",
            objectives=[
                "Analyze data quality",
                "Identify trends",
                "Detect anomalies"
            ],
            data_sources=["test_data.csv"],
            created_by=sample_users['manager'].id,
            auto_generate_tasks=True
        )
        
        assert plan.name == "Test Analysis Plan"
        assert len(plan.objectives) == 3
        assert len(plan.tasks) > 0
        assert plan.status == "draft"
        
        # Check task generation
        task_types = [task.task_type for task in plan.tasks]
        assert TaskType.DATA_PROFILING in task_types
        assert TaskType.ANOMALY_DETECTION in task_types
    
    def test_task_generation_from_objectives(self, workflow_manager):
        """Test automatic task generation"""
        objectives = [
            "Check data quality and completeness",
            "Analyze trends over time",
            "Build predictive model for sales",
            "Segment customers by behavior",
            "Find correlations between features"
        ]
        
        tasks = workflow_manager._generate_tasks_from_objectives(
            objectives, ["data.csv"]
        )
        
        # Check task types are appropriate
        task_types = [task.task_type for task in tasks]
        
        assert TaskType.DATA_PROFILING in task_types
        assert TaskType.TIME_SERIES_ANALYSIS in task_types
        assert TaskType.PREDICTIVE_MODELING in task_types
        assert TaskType.SEGMENTATION in task_types
        assert TaskType.CORRELATION_ANALYSIS in task_types
        
        # Check dependencies
        profiling_tasks = [t for t in tasks if t.task_type == TaskType.DATA_PROFILING]
        other_tasks = [t for t in tasks if t.task_type != TaskType.DATA_PROFILING]
        
        # Other tasks should depend on profiling
        for task in other_tasks:
            if task.data_source == profiling_tasks[0].data_source:
                assert any(prof.id in task.dependencies for prof in profiling_tasks)
    
    def test_task_assignment(self, workflow_manager, sample_users):
        """Test task assignment to users"""
        # Create a task
        task = AnalysisTask(
            id="task_001",
            name="Test Task",
            description="Test task description",
            task_type=TaskType.DATA_PROFILING,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        workflow_manager.tasks[task.id] = task
        
        # Assign to analyst
        success = workflow_manager.assign_task(task.id, sample_users['analyst'].id)
        
        assert success
        assert task.assigned_to == sample_users['analyst'].id
        assert task.status == TaskStatus.ASSIGNED
        assert workflow_manager.users[sample_users['analyst'].id].workload == 1
    
    def test_auto_assignment(self, workflow_manager, sample_users):
        """Test automatic task assignment"""
        # Create plan with tasks
        plan = workflow_manager.create_plan(
            name="Auto Assignment Test",
            description="Test automatic assignment",
            objectives=["Analyze data", "Create visualizations"],
            data_sources=["test.csv"],
            created_by=sample_users['manager'].id,
            auto_generate_tasks=True
        )
        
        # Approve plan to add tasks to queue
        workflow_manager.approve_plan(plan.id, sample_users['manager'].id)
        
        # Auto-assign tasks
        assignments = workflow_manager.auto_assign_tasks()
        
        assert len(assignments) > 0
        
        # Check assignments are valid
        for task_id, user_id in assignments.items():
            assert task_id in workflow_manager.tasks
            assert user_id in workflow_manager.users
            task = workflow_manager.tasks[task_id]
            assert task.assigned_to == user_id
            assert task.status == TaskStatus.ASSIGNED
    
    def test_marimo_notebook_generation(self, workflow_manager, sample_data):
        """Test Marimo notebook generation for different task types"""
        task_types_to_test = [
            TaskType.DATA_PROFILING,
            TaskType.STATISTICAL_ANALYSIS,
            TaskType.CORRELATION_ANALYSIS,
            TaskType.VISUALIZATION,
            TaskType.PREDICTIVE_MODELING,
            TaskType.ANOMALY_DETECTION,
            TaskType.SEGMENTATION
        ]
        
        for task_type in task_types_to_test:
            task = AnalysisTask(
                id=f"task_{task_type.value}",
                name=f"Test {task_type.value}",
                description=f"Test task for {task_type.value}",
                task_type=task_type,
                status=TaskStatus.PENDING,
                created_at=datetime.now(),
                data_source=sample_data,
                parameters={'test': True}
            )
            
            notebook_path = workflow_manager.generate_marimo_notebook(task)
            
            assert Path(notebook_path).exists()
            assert task.marimo_notebook_path == notebook_path
            
            # Check notebook content
            with open(notebook_path, 'r') as f:
                content = f.read()
                assert 'import marimo as mo' in content
                assert 'import pandas as pd' in content
                assert task_type.value in content.lower()
    
    @pytest.mark.asyncio
    async def test_task_execution(self, workflow_manager, sample_data):
        """Test task execution with Marimo"""
        task = AnalysisTask(
            id="exec_task_001",
            name="Execution Test Task",
            description="Test task execution",
            task_type=TaskType.DATA_PROFILING,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            data_source=sample_data
        )
        workflow_manager.tasks[task.id] = task
        
        # Execute task
        result = await workflow_manager.execute_task(task.id)
        
        # Check task status updated
        assert task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
        
        if task.status == TaskStatus.COMPLETED:
            assert task.completed_at is not None
            assert task.started_at is not None
            assert 'error' not in result
    
    def test_plan_execution(self, workflow_manager, sample_users, sample_data):
        """Test complete plan execution"""
        # Create plan
        plan = workflow_manager.create_plan(
            name="Execution Test Plan",
            description="Test complete plan execution",
            objectives=["Profile data", "Visualize patterns"],
            data_sources=[sample_data],
            created_by=sample_users['manager'].id,
            auto_generate_tasks=True
        )
        
        # Approve plan
        workflow_manager.approve_plan(plan.id, sample_users['manager'].id)
        
        # Execute plan
        results = workflow_manager.execute_plan(plan.id)
        
        assert 'plan_id' in results
        assert 'tasks' in results
        assert 'summary' in results
        
        # Check summary
        summary = results['summary']
        assert 'completed_tasks' in summary
        assert 'failed_tasks' in summary
        assert 'key_findings' in summary
        assert 'recommendations' in summary
    
    def test_results_aggregation(self, workflow_manager):
        """Test results aggregation from multiple tasks"""
        # Create mock plan and task results
        plan = AnalysisPlan(
            id="agg_plan",
            name="Aggregation Test",
            description="Test aggregation",
            created_by="mgr_001",
            created_at=datetime.now(),
            objectives=["Test"],
            data_sources=["test.csv"],
            tasks=[],
            timeline={}
        )
        
        # Mock task results
        task_results = {
            'task_1': {
                'shape': (1000, 10),
                'missing': {'col1': 5, 'col2': 10}
            },
            'task_2': {
                'score': 0.85,
                'top_features': [('feature1', 0.4), ('feature2', 0.3)]
            },
            'task_3': {
                'anomaly_percentage': 2.5,
                'anomalies_detected': 25
            },
            'task_4': {
                'n_clusters': 4,
                'cluster_sizes': {0: 250, 1: 250, 2: 250, 3: 250}
            }
        }
        
        # Create corresponding tasks
        workflow_manager.tasks['task_1'] = AnalysisTask(
            id='task_1', name='Profiling', description='',
            task_type=TaskType.DATA_PROFILING, status=TaskStatus.COMPLETED,
            created_at=datetime.now()
        )
        workflow_manager.tasks['task_2'] = AnalysisTask(
            id='task_2', name='Modeling', description='',
            task_type=TaskType.PREDICTIVE_MODELING, status=TaskStatus.COMPLETED,
            created_at=datetime.now()
        )
        workflow_manager.tasks['task_3'] = AnalysisTask(
            id='task_3', name='Anomaly', description='',
            task_type=TaskType.ANOMALY_DETECTION, status=TaskStatus.COMPLETED,
            created_at=datetime.now()
        )
        workflow_manager.tasks['task_4'] = AnalysisTask(
            id='task_4', name='Segmentation', description='',
            task_type=TaskType.SEGMENTATION, status=TaskStatus.COMPLETED,
            created_at=datetime.now()
        )
        
        plan.tasks = list(workflow_manager.tasks.values())
        
        # Aggregate results
        summary = workflow_manager._aggregate_results(plan, task_results)
        
        assert summary['completed_tasks'] == 4
        assert summary['failed_tasks'] == 0
        assert len(summary['key_findings']) > 0
        assert 'data_shape' in summary['metrics']
        assert summary['metrics']['missing_values'] == 15
        
        # Check findings
        findings_text = ' '.join(summary['key_findings'])
        assert 'Anomalies detected: 2.50%' in findings_text
        assert 'Data segmented into 4 groups' in findings_text
    
    def test_workflow_persistence(self, workflow_manager, sample_users):
        """Test saving and loading workflow data"""
        # Create and save plan
        plan = workflow_manager.create_plan(
            name="Persistence Test",
            description="Test saving",
            objectives=["Test objective"],
            data_sources=["test.csv"],
            created_by=sample_users['manager'].id
        )
        
        # Check plan file exists
        plan_file = workflow_manager.plans_dir / f"{plan.id}.json"
        assert plan_file.exists()
        
        # Load plan
        loaded_data = workflow_manager.load_plan(plan.id)
        assert loaded_data is not None
        assert loaded_data['name'] == "Persistence Test"
    
    def test_dashboard_data(self, workflow_manager, sample_users):
        """Test dashboard data generation"""
        # Create some plans and tasks
        plan1 = workflow_manager.create_plan(
            name="Plan 1",
            description="Test plan 1",
            objectives=["Objective 1"],
            data_sources=["data1.csv"],
            created_by=sample_users['manager'].id
        )
        
        plan2 = workflow_manager.create_plan(
            name="Plan 2",
            description="Test plan 2",
            objectives=["Objective 2"],
            data_sources=["data2.csv"],
            created_by=sample_users['manager'].id
        )
        
        # Approve one plan
        workflow_manager.approve_plan(plan1.id, sample_users['manager'].id)
        
        # Get dashboard data
        dashboard = workflow_manager.get_dashboard_data()
        
        assert dashboard['plans']['total'] == 2
        assert dashboard['plans']['active'] == 1
        assert dashboard['tasks']['total'] > 0
        assert dashboard['users']['total'] == 3
        assert len(dashboard['recent_plans']) > 0
        assert len(dashboard['recent_tasks']) > 0

class TestEndToEndWorkflow:
    """Test complete end-to-end workflow"""
    
    def test_complete_workflow(self):
        """Test complete workflow from plan creation to results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            wf = WorkflowManager(workspace_path=tmpdir)
            
            # Create users
            manager = User(
                id="mgr_001",
                name="Manager",
                email="manager@test.com",
                role=UserRole.MANAGER
            )
            wf.register_user(manager)
            
            analyst = User(
                id="ana_001",
                name="Analyst",
                email="analyst@test.com",
                role=UserRole.ANALYST,
                skills=["data_profiling", "statistical_analysis", "visualization"]
            )
            wf.register_user(analyst)
            
            # Create sample data
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                df = pd.DataFrame({
                    'value1': np.random.randn(50),
                    'value2': np.random.randn(50),
                    'category': np.random.choice(['A', 'B', 'C'], 50)
                })
                df.to_csv(f.name, index=False)
                data_file = f.name
            
            # Manager creates plan
            plan = wf.create_plan(
                name="End-to-End Test",
                description="Complete workflow test",
                objectives=[
                    "Profile the dataset",
                    "Analyze statistical properties",
                    "Create visualizations"
                ],
                data_sources=[data_file],
                created_by=manager.id,
                auto_generate_tasks=True
            )
            
            assert len(plan.tasks) >= 3
            
            # Approve plan
            wf.approve_plan(plan.id, manager.id)
            assert plan.status == "active"
            
            # Auto-assign tasks
            assignments = wf.auto_assign_tasks()
            assert len(assignments) > 0
            
            # Check assignments
            for task_id in assignments:
                task = wf.tasks[task_id]
                assert task.assigned_to is not None
                assert task.status == TaskStatus.ASSIGNED
            
            # Generate notebooks for all tasks
            for task in plan.tasks:
                notebook_path = wf.generate_marimo_notebook(task)
                assert Path(notebook_path).exists()
            
            # Execute plan (would run Marimo notebooks)
            results = wf.execute_plan(plan.id)
            
            assert 'summary' in results
            assert results['summary']['total_tasks'] == len(plan.tasks)
            
            # Clean up
            Path(data_file).unlink()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])