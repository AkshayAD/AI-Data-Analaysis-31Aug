# Agentic Marimo Quick Start Guide

## Overview

This guide will help you get started with the Agentic Marimo system, which seamlessly integrates AI agents with Marimo's reactive notebooks for intelligent data analysis.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.8+ installed
- Node.js 16+ installed (for web UI)
- Git installed
- At least 8GB RAM available
- OpenAI API key (or compatible LLM API)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/ai-data-analysis-team.git
cd ai-data-analysis-team
```

### 2. Clone and Install Marimo

```bash
# Clone marimo repository as a submodule
git submodule add https://github.com/AkshayAD/marimo.git marimo-source
git submodule update --init --recursive

# Install marimo
pip install marimo
```

### 3. Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configurations
nano .env
```

Required environment variables:
```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agentic_marimo

# Security
JWT_SECRET=your_secure_jwt_secret
API_KEY=your_api_key

# Services
REDIS_URL=redis://localhost:6379
MARIMO_SERVER_URL=http://localhost:8080
```

### 4. Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install

# Install development tools
make install
```

### 5. Start the System

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or start individual services
make start-services
```

## Basic Usage

### 1. Natural Language Analysis

```python
from agentic_marimo import Client

# Initialize client
client = Client(api_key="your_api_key")

# Request analysis using natural language
result = client.analyze(
    query="Analyze the sales trends for Q4 2024 and identify top performing products",
    data_source="data/sales_2024.csv"
)

# Get notebook URL for interactive exploration
print(f"Interactive notebook: {result.notebook_url}")
```

### 2. Using the Web Interface

1. Open your browser and navigate to `http://localhost:3000`
2. Login with your credentials
3. Click "New Analysis" and describe your task
4. Upload data or connect to a data source
5. Watch as agents create and execute the analysis
6. Interact with the results in real-time

### 3. CLI Usage

```bash
# Run analysis from command line
agentic-marimo analyze \
  --query "Perform regression analysis on housing prices" \
  --data "housing_data.csv" \
  --output "results.json"

# List available agents
agentic-marimo agents list

# Check task status
agentic-marimo tasks status <task_id>

# Export notebook
agentic-marimo notebooks export <notebook_id> --format html
```

### 4. API Usage

#### Create Analysis Task

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze customer churn patterns",
    "data_source": "customers.csv",
    "agents": ["data_agent", "analysis_agent", "ml_agent"],
    "output_format": "json"
  }'
```

#### Monitor Task Progress

```bash
curl http://localhost:8000/api/v1/tasks/{task_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### WebSocket Real-time Updates

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'subscribe',
    notebook_id: 'nb_123',
    events: ['cell_execution', 'variable_update']
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Notebook update:', data);
};
```

## Example Workflows

### Workflow 1: Exploratory Data Analysis

```python
# Step 1: Initialize orchestrator
from agentic_marimo import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Step 2: Request EDA
task = orchestrator.create_task(
    type="exploratory_analysis",
    data_path="data/raw/dataset.csv",
    requirements={
        "profile_data": True,
        "identify_patterns": True,
        "detect_anomalies": True,
        "create_visualizations": True
    }
)

# Step 3: Execute and monitor
result = await orchestrator.execute(task)

# Step 4: Access results
print(result.summary)
print(f"Notebook: {result.notebook_url}")
print(f"Report: {result.report_path}")
```

### Workflow 2: Machine Learning Pipeline

```python
# Create ML workflow
ml_task = orchestrator.create_ml_workflow(
    data_source="training_data.parquet",
    task_type="classification",
    target_column="churn",
    config={
        "test_size": 0.2,
        "models": ["random_forest", "xgboost", "neural_network"],
        "cross_validation": 5,
        "hyperparameter_tuning": True
    }
)

# Execute with progress tracking
async for progress in orchestrator.execute_with_progress(ml_task):
    print(f"Progress: {progress.percentage}% - {progress.current_step}")

# Get model performance
best_model = result.best_model
print(f"Best model: {best_model.name}")
print(f"Accuracy: {best_model.metrics['accuracy']:.3f}")
```

### Workflow 3: Automated Reporting

```python
# Schedule daily analysis
from agentic_marimo import Scheduler

scheduler = Scheduler()

scheduler.create_job(
    name="daily_sales_report",
    schedule="0 9 * * *",  # 9 AM daily
    task={
        "type": "report_generation",
        "data_query": "SELECT * FROM sales WHERE date = CURRENT_DATE - 1",
        "template": "daily_sales_template",
        "recipients": ["team@company.com"],
        "format": ["pdf", "html", "slack"]
    }
)
```

## Working with Templates

### Using Existing Templates

```python
# List available templates
templates = client.templates.list()

# Use a template
result = client.analyze(
    template="time_series_forecast",
    parameters={
        "data_source": "sales_history.csv",
        "target_column": "revenue",
        "forecast_periods": 12,
        "seasonality": "monthly"
    }
)
```

### Creating Custom Templates

```python
# marimo_notebooks/templates/custom_analysis.py
import marimo as mo

@mo.cell
def custom_analysis(data):
    # Your custom analysis logic
    pass

# Register template
client.templates.register(
    name="custom_analysis",
    path="marimo_notebooks/templates/custom_analysis.py",
    description="Custom analysis for specific use case"
)
```

## Monitoring & Debugging

### View Logs

```bash
# API logs
docker-compose logs -f api

# Agent worker logs
docker-compose logs -f agent-worker

# Marimo server logs
docker-compose logs -f marimo
```

### Access Monitoring Dashboards

- **Grafana**: http://localhost:3000 (admin/admin)
- **Flower** (Celery): http://localhost:5555
- **Prometheus**: http://localhost:9090
- **MinIO Console**: http://localhost:9001

### Debug Mode

```python
# Enable debug mode for detailed execution logs
client = Client(api_key="your_key", debug=True)

# Or set environment variable
export AGENTIC_MARIMO_DEBUG=true
```

## Best Practices

### 1. Data Management
- Store raw data in `data/raw/`
- Keep processed data in `data/processed/`
- Use version control for data schemas
- Implement data validation before analysis

### 2. Agent Configuration
- Specify appropriate agents for tasks
- Set reasonable timeouts for long-running tasks
- Use agent specialization for better performance
- Monitor agent resource usage

### 3. Notebook Management
- Use templates for repeatable analyses
- Version control notebook templates
- Clean up old notebooks periodically
- Export important results for archival

### 4. Security
- Never commit API keys or secrets
- Use environment variables for sensitive data
- Implement proper authentication
- Regularly update dependencies

### 5. Performance
- Cache frequently used data
- Use async operations where possible
- Limit concurrent notebook executions
- Monitor system resources

## Troubleshooting

### Common Issues

#### 1. Marimo Server Not Responding
```bash
# Check if Marimo is running
docker-compose ps marimo

# Restart Marimo service
docker-compose restart marimo

# Check logs
docker-compose logs marimo
```

#### 2. Agent Task Failures
```python
# Get detailed error information
task_details = client.tasks.get(task_id)
print(task_details.error_message)
print(task_details.stack_trace)

# Retry failed task
client.tasks.retry(task_id)
```

#### 3. Database Connection Issues
```bash
# Test database connection
docker-compose exec api python -c "from src.core.database import test_connection; test_connection()"

# Reset database
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres psql -U postgres -c "CREATE DATABASE agentic_marimo;"
```

#### 4. Memory Issues
```bash
# Increase Docker memory allocation
# Edit docker-compose.yml
services:
  marimo:
    mem_limit: 4g
    
  agent-worker:
    mem_limit: 2g
```

## Advanced Features

### Multi-Agent Collaboration

```python
# Define complex multi-agent workflow
workflow = orchestrator.create_workflow([
    {"agent": "data_agent", "task": "load_and_clean"},
    {"agent": "analysis_agent", "task": "statistical_analysis"},
    {"agent": "ml_agent", "task": "predictive_modeling"},
    {"agent": "visualization_agent", "task": "create_dashboard"},
    {"agent": "report_agent", "task": "generate_report"}
])

# Execute with dependencies
result = await orchestrator.execute_workflow(workflow)
```

### Custom Agent Development

```python
from agentic_marimo.agents import BaseAgent

class CustomAgent(BaseAgent):
    def _define_capabilities(self):
        return {
            "custom_analysis": True,
            "specialized_task": True
        }
    
    async def process_task(self, task):
        # Your custom logic here
        notebook_id = await self.create_notebook("custom_template")
        # Process task
        return result

# Register custom agent
orchestrator.register_agent(CustomAgent())
```

### Reactive Pipeline Creation

```python
# Create reactive data pipeline
pipeline = client.pipelines.create(
    name="real_time_analysis",
    triggers=["data_update", "schedule"],
    steps=[
        {"type": "data_validation"},
        {"type": "transformation"},
        {"type": "analysis"},
        {"type": "alert", "condition": "anomaly_detected"}
    ]
)

# Connect to data stream
pipeline.connect_stream("kafka://localhost:9092/topic")
```

## Getting Help

### Documentation
- Full documentation: [docs/](./docs/)
- API reference: [docs/API.md](./docs/API.md)
- Integration plan: [docs/MARIMO_INTEGRATION_PLAN.md](./docs/MARIMO_INTEGRATION_PLAN.md)

### Community
- GitHub Issues: Report bugs and request features
- Discussions: Ask questions and share experiences
- Slack Channel: Real-time community support

### Support
- Email: support@agenticmarimo.ai
- Documentation: https://docs.agenticmarimo.ai
- Video Tutorials: https://youtube.com/agenticmarimo

## Next Steps

1. **Explore Templates**: Check out the template library in `marimo_notebooks/templates/`
2. **Try Examples**: Run example notebooks in `notebooks/examples/`
3. **Build Custom Agents**: Extend the system with your own agents
4. **Integrate with Your Stack**: Connect to your data sources and tools
5. **Deploy to Production**: Follow the deployment guide for production setup

---

Happy analyzing with Agentic Marimo! 🚀