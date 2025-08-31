#!/usr/bin/env python3
"""
Comprehensive test of the Enterprise AI Data Analysis Platform workflow
Tests complete end-to-end workflow with human-in-the-loop approval mechanisms
"""

import sys
import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add src/python to path
sys.path.append(str(Path(__file__).parent / "src" / "python"))

try:
    from integration.enterprise_integration import get_enterprise_integration
    print("✅ Successfully imported enterprise integration")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_authentication():
    """Test authentication system"""
    print("\n🔐 Testing Authentication System...")
    
    # Initialize enterprise integration
    integration = get_enterprise_integration()
    
    # Test valid login
    user_info = integration.auth_manager.authenticate(
        'manager@company.com', 'manager123'
    )
    
    if user_info:
        print(f"✅ Manager login successful: {user_info['name']}")
    else:
        print("❌ Manager login failed")
        return False
    
    # Test analyst login
    analyst_info = integration.auth_manager.authenticate(
        'analyst@company.com', 'analyst123'
    )
    
    if analyst_info:
        print(f"✅ Analyst login successful: {analyst_info['name']}")
    else:
        print("❌ Analyst login failed")
        return False
    
    return True

def test_plan_creation_and_approval():
    """Test plan creation and approval workflow"""
    print("\n📋 Testing Plan Creation & Approval Workflow...")
    
    integration = get_enterprise_integration()
    
    # Create a comprehensive analysis plan
    plan_result = integration.create_analysis_plan(
        user_email='manager@company.com',
        plan_name='Q4 Revenue Analysis & Q1 Forecast',
        objectives=[
            'Analyze Q4 revenue trends and seasonal patterns',
            'Identify top performing products and regions',
            'Predict Q1 revenue using machine learning models',
            'Segment customers based on purchase behavior',
            'Detect any anomalies or unusual patterns in sales'
        ],
        data_sources=['q4_sales_data.csv', 'customer_data.xlsx']
    )
    
    if 'error' in plan_result:
        print(f"❌ Plan creation failed: {plan_result['error']}")
        return None
    
    plan = plan_result['plan']
    approval_request_id = plan_result['approval_request_id']
    
    print(f"✅ Plan created successfully: {plan['name']}")
    print(f"📝 Generated {len(plan['tasks'])} tasks automatically")
    
    # Show generated tasks
    for i, task in enumerate(plan['tasks'], 1):
        print(f"   {i}. {task['name']} ({task['type']}) - {task.get('estimated_hours', 'N/A')} hours")
        if task.get('dependencies'):
            print(f"      Dependencies: {', '.join(task['dependencies'])}")
    
    print(f"⏳ Plan status: {plan_result['status']}")
    
    # Simulate manager approval
    print("\n👤 Manager reviewing and approving plan...")
    approval_result = integration.approve_plan(
        approval_request_id=approval_request_id,
        approver_email='manager@company.com',
        comments=['Plan looks comprehensive', 'Good task breakdown']
    )
    
    if 'error' in approval_result:
        print(f"❌ Plan approval failed: {approval_result['error']}")
        return None
    
    print(f"✅ Plan approved successfully!")
    print(f"🎯 {len(approval_result['task_assignments'])} tasks assigned to team members")
    
    # Show task assignments
    for assignment in approval_result['task_assignments']:
        print(f"   • {assignment['task_name']} → {assignment['assigned_to']}")
    
    return plan['id']

def test_task_execution():
    """Test task execution workflow"""
    print("\n⚙️ Testing Task Execution Workflow...")
    
    integration = get_enterprise_integration()
    
    # Get tasks for analyst
    analyst_tasks = integration.get_user_tasks('analyst@company.com')
    
    if not analyst_tasks:
        print("❌ No tasks found for analyst")
        return False
    
    print(f"✅ Found {len(analyst_tasks)} tasks assigned to analyst")
    
    # Execute first task
    first_task = analyst_tasks[0]['task']
    task_id = first_task['id']
    
    print(f"🔄 Executing task: {first_task['name']}")
    
    # Create sample data for task execution
    sample_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=365, freq='D'),
        'revenue': 1000 + pd.Series(range(365)) * 2.5 + pd.Series(range(365)).apply(lambda x: 200 * (1 + 0.3 * (x % 90) / 90)),
        'customers': 50 + pd.Series(range(365)) * 0.1,
        'region': ['North', 'South', 'East', 'West'] * 91 + ['North'],
        'product': ['A', 'B', 'C', 'D'] * 91 + ['A']
    })
    
    execution_result = integration.execute_task(
        task_id=task_id,
        user_email='analyst@company.com',
        data=sample_data
    )
    
    if 'error' in execution_result:
        print(f"❌ Task execution failed: {execution_result['error']}")
        return False
    
    print(f"✅ Task executed successfully: {execution_result['status']}")
    
    if execution_result.get('status') == 'submitted_for_review':
        print("👥 Task submitted for peer review (complex analysis)")
    elif execution_result.get('status') == 'completed':
        print("🎉 Task completed without requiring review")
    elif execution_result.get('status') == 'report_generated':
        print("📊 All tasks complete - final report generated!")
        return execution_result.get('report')
    
    return True

def test_approval_queue():
    """Test approval queue functionality"""
    print("\n✅ Testing Approval Queue...")
    
    integration = get_enterprise_integration()
    
    # Get manager's approval queue
    manager_approvals = integration.get_approval_queue(user_role='manager')
    print(f"📥 Manager approval queue: {len(manager_approvals)} items")
    
    for approval in manager_approvals:
        print(f"   • {approval['type']}: {approval['title']}")
        print(f"     From: {approval['submitter']} | Status: {approval['status']}")
    
    # Get senior analyst's approval queue
    senior_approvals = integration.get_approval_queue(user_role='senior_analyst')
    print(f"👨‍💼 Senior analyst approval queue: {len(senior_approvals)} items")
    
    for approval in senior_approvals:
        print(f"   • {approval['type']}: {approval['title']}")
    
    return True

def test_team_dashboard():
    """Test team dashboard metrics"""
    print("\n👥 Testing Team Dashboard...")
    
    integration = get_enterprise_integration()
    
    dashboard_data = integration.get_team_dashboard()
    
    team_stats = dashboard_data['team_stats']
    print(f"✅ Team Statistics:")
    print(f"   • Total Members: {team_stats['total_members']}")
    print(f"   • Total Tasks: {team_stats['total_tasks']}")
    print(f"   • Completed Tasks: {team_stats['completed_tasks']}")
    print(f"   • Completion Rate: {team_stats['completion_rate']:.1f}%")
    print(f"   • Active Plans: {dashboard_data['active_plans']}")
    
    print(f"\n👤 Individual Performance:")
    for member in dashboard_data['member_performance']:
        print(f"   • {member['name']} ({member['role']})")
        print(f"     Active: {member['active_tasks']}, Completed: {member['completed_tasks']}")
    
    return True

def test_complete_workflow():
    """Test complete end-to-end workflow"""
    print("\n🔄 Testing Complete End-to-End Workflow...")
    
    integration = get_enterprise_integration()
    
    # Step 1: Manager creates plan
    print("\n1️⃣ Manager creates comprehensive analysis plan...")
    plan_id = test_plan_creation_and_approval()
    
    if not plan_id:
        print("❌ Workflow failed at plan creation")
        return False
    
    # Step 2: Tasks are assigned and executed
    print("\n2️⃣ Tasks assigned to team members...")
    task_result = test_task_execution()
    
    if not task_result:
        print("❌ Workflow failed at task execution")
        return False
    
    # Step 3: Check plan status
    print("\n3️⃣ Checking overall plan progress...")
    plan_status = integration.get_plan_status(plan_id)
    
    if 'error' in plan_status:
        print(f"❌ Failed to get plan status: {plan_status['error']}")
        return False
    
    print(f"📊 Plan Progress: {plan_status['progress']:.1f}%")
    print(f"📝 Tasks: {plan_status['completed_tasks']}/{plan_status['total_tasks']} complete")
    print(f"⚡ In Progress: {plan_status['in_progress_tasks']} tasks")
    
    # Step 4: Test approval workflows
    print("\n4️⃣ Testing approval workflows...")
    test_approval_queue()
    
    # Step 5: Team performance monitoring
    print("\n5️⃣ Monitoring team performance...")
    test_team_dashboard()
    
    print("\n🎉 Complete workflow test successful!")
    return True

def display_workflow_diagram():
    """Display the complete workflow that was implemented"""
    print("\n" + "="*70)
    print("📈 IMPLEMENTED WORKFLOW DIAGRAM")
    print("="*70)
    print("""
    MANAGER FLOW:
    ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
    │ Create Plan │ -> │ Auto-Generate│ -> │ Review & Approve│
    │   + Objectives│    │   Tasks      │    │     Plan        │
    └─────────────┘    └──────────────┘    └─────────────────┘
                                                    │
                                                    ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐
    │ Intelligent     │ -> │ Generate Marimo │ -> │ Notify Team    │
    │ Task Assignment │    │   Notebooks     │    │   Members      │
    └─────────────────┘    └─────────────────┘    └────────────────┘

    ANALYST/ASSOCIATE FLOW:
    ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐
    │ Receive Task│ -> │ Execute      │ -> │ Submit Results  │
    │ Notification│    │ Marimo       │    │ + Confidence    │
    └─────────────┘    │ Notebook     │    └─────────────────┘
                       └──────────────┘             │
                                                    ▼
    ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐
    │ Quality Check   │ <- │ Peer Review     │ <- │ Review         │
    │ (Automated)     │    │ (if needed)     │    │ Required?      │
    └─────────────────┘    └─────────────────┘    └────────────────┘
                                    │
                                    ▼
    REPORTING FLOW:
    ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐
    │ Aggregate All   │ -> │ Generate Exec   │ -> │ Manager Final  │
    │ Task Results    │    │   Report        │    │   Approval     │
    └─────────────────┘    └─────────────────┘    └────────────────┘
                                                           │
                                                           ▼
                                                  ┌────────────────┐
                                                  │ Distribute to  │
                                                  │ Stakeholders   │
                                                  └────────────────┘

    HUMAN-IN-THE-LOOP APPROVAL POINTS:
    ✓ Plan Creation & Approval
    ✓ Task Assignment Override
    ✓ Quality Gate Reviews
    ✓ Peer Review Process
    ✓ Result Validation
    ✓ Final Report Approval
    ✓ Distribution Authorization
    """)
    print("="*70)

def main():
    """Run comprehensive workflow tests"""
    print("🚀 Starting Enterprise AI Data Analysis Platform Tests")
    print("="*60)
    
    # Test individual components
    tests = [
        ("Authentication System", test_authentication),
        ("Plan Creation & Approval", lambda: test_plan_creation_and_approval() is not None),
        ("Task Execution", lambda: test_task_execution() is not False),
        ("Approval Queue", test_approval_queue),
        ("Team Dashboard", test_team_dashboard),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n❌ ERROR in {test_name}: {e}")
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n" + "="*60)
    print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The enterprise platform is fully operational.")
        
        # Test complete workflow
        print(f"\n" + "="*60)
        print("🔄 RUNNING COMPLETE END-TO-END WORKFLOW TEST")
        print("="*60)
        
        try:
            if test_complete_workflow():
                print("\n🎯 SUCCESS: Complete end-to-end workflow is operational!")
                display_workflow_diagram()
            else:
                print("\n❌ Complete workflow test failed")
        except Exception as e:
            print(f"\n❌ Complete workflow test error: {e}")
    else:
        failed_tests = [name for name, result in results if not result]
        print(f"❌ Failed tests: {', '.join(failed_tests)}")
    
    print(f"\n🏢 Enterprise AI Data Analysis Platform Test Complete")
    print(f"📅 Test run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()