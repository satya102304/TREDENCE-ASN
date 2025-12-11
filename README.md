# Workflow Engine - AI Engineering Internship Assignment

A minimal but powerful workflow/graph engine built with FastAPI. This system allows you to define sequences of steps (nodes), connect them with edges, maintain shared state, and execute workflows with support for branching and looping.

##  Features

-  **Nodes & Edges**: Define workflow steps and their connections
-  **Shared State**: State dictionary flows through the entire workflow
-  **Conditional Branching**: Route to different nodes based on state conditions
-  **Looping**: Repeat nodes until conditions are met
-  **Tool Registry**: Reusable functions that nodes can call
-  **Async Support**: Non-blocking execution with FastAPI
-  **Execution Logging**: Complete audit trail of workflow execution
-  **In-Memory Storage**: Simple but functional storage layer

##  Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── models.py            # Pydantic models
│   ├── engine.py            # Workflow engine core logic
│   ├── tools.py             # Tool registry & default tools
│   ├── storage.py           # In-memory storage
│   └── workflows/
│       ├── __init__.py
│       └── code_review.py   # Example: Code review workflow
├── requirements.txt
└── README.md
```

##  Installation

1. **Clone or create the project structure** as shown above

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the server**:
```bash
uvicorn app.main:app --reload
```

4. **Access the API**:
- Interactive docs: http://localhost:8000/docs
- API root: http://localhost:8000

##  API Endpoints

### Core Endpoints

#### `POST /graph/create`
Create a new workflow graph.

**Request**:
```json
{
  "nodes": ["extract", "analyze", "improve"],
  "edges": {
    "extract": "analyze",
    "analyze": "improve"
  },
  "start_node": "extract"
}
```

**Response**:
```json
{
  "graph_id": "abc-123-def",
  "message": "Graph created successfully"
}
```

#### `POST /graph/run`
Execute a workflow with initial state.

**Request**:
```json
{
  "graph_id": "abc-123-def",
  "initial_state": {
    "code": "def hello(): return 'world'"
  }
}
```

**Response**:
```json
{
  "run_id": "run-456-xyz",
  "graph_id": "abc-123-def",
  "final_state": { ... },
  "execution_log": [ ... ],
  "status": "completed"
}
```

#### `GET /graph/state/{run_id}`
Get the current state of a workflow run.

**Response**:
```json
{
  "run_id": "run-456-xyz",
  "graph_id": "abc-123-def",
  "current_state": { ... },
  "status": "completed",
  "execution_log": [ ... ]
}
```

### Convenience Endpoints

- `GET /graphs` - List all graphs
- `GET /runs` - List all workflow runs
- `GET /tools` - List registered tools
- `GET /example/code-review` - Get example workflow definition
- `POST /example/run` - Run the example workflow immediately

##  Example Workflow: Code Review Mini-Agent

The project includes a complete code review workflow that demonstrates all features:

### Workflow Steps:
1. **Extract Functions** - Parse code and extract function definitions
2. **Check Complexity** - Analyze complexity metrics
3. **Detect Issues** - Find common code problems
4. **Suggest Improvements** - Generate improvement suggestions
5. **Calculate Quality Score** - Compute overall quality score
6. **Loop** - Repeat improvements until quality_score >= 70

### Quick Test:

```bash
# Run the example workflow
curl -X POST http://localhost:8000/example/run
```

Or use the interactive API docs at http://localhost:8000/docs

## 🔧 How It Works

### 1. Define a Workflow

```python
from app.models import GraphDefinition

workflow = GraphDefinition(
    nodes=["step1", "step2", "step3"],
    edges={
        "step1": "step2",
        "step2": "step3"
    },
    start_node="step1"
)
```

### 2. Add Conditional Branching

```python
edges = {
    "check": {
        "condition": "state.get('value', 0) > 10",
        "true": "handle_high",
        "false": "handle_low"
    }
}
```

### 3. Add Looping

```python
from app.models import Node, NodeType

node_configs = {
    "process": Node(
        name="process",
        type=NodeType.LOOP,
        tool="process_data",
        loop_condition="state.get('count', 0) < 5",
        max_iterations=10
    )
}
```

### 4. Register Custom Tools

```python
from app.tools import tool_registry

def my_custom_tool(state):
    # Your logic here
    state["result"] = "processed"
    return state

tool_registry.register("my_tool", my_custom_tool)
```

##  Testing

### Manual Testing with curl:

```bash
# 1. Create a simple graph
curl -X POST http://localhost:8000/graph/create \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": ["start", "end"],
    "edges": {"start": "end"},
    "start_node": "start"
  }'

# 2. Run the graph
curl -X POST http://localhost:8000/graph/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "<graph_id_from_step_1>",
    "initial_state": {"data": "test"}
  }'
```

### Using Python requests:

```python
import requests

# Create graph
response = requests.post(
    "http://localhost:8000/graph/create",
    json={
        "nodes": ["extract", "analyze"],
        "edges": {"extract": "analyze"},
        "start_node": "extract"
    }
)
graph_id = response.json()["graph_id"]

# Run workflow
response = requests.post(
    "http://localhost:8000/graph/run",
    json={
        "graph_id": graph_id,
        "initial_state": {"code": "def test(): pass"}
    }
)
print(response.json())
```

##  What This Engine Supports

### ✅ Implemented Features:
- **Nodes**: Python functions that transform state
- **Edges**: Simple string or conditional dict connections
- **State Management**: Dictionary that flows through workflow
- **Conditional Branching**: Route based on state values
- **Looping**: Repeat nodes with max iteration safety
- **Tool Registry**: Pre-register or dynamically add tools
- **Async Execution**: All endpoints and engine support async
- **Execution Logging**: Complete audit trail with before/after states
- **Multiple Workflows**: Create and store multiple graphs
- **Error Handling**: Graceful error capture in state

###  What Could Be Improved With More Time:

1. **Persistence Layer**: 
   - SQLite or PostgreSQL for production use
   - Persistent storage of graphs and runs

2. **Advanced Features**:
   - WebSocket streaming for real-time execution updates
   - Parallel node execution for independent branches
   - Sub-graphs and workflow composition
   - Workflow versioning

3. **Monitoring & Observability**:
   - Structured logging with levels
   - Metrics (execution time, success rate)
   - Distributed tracing

4. **Security**:
   - Authentication & authorization
   - Rate limiting
   - Input validation hardening
   - Sandboxed tool execution

5. **Developer Experience**:
   - Visual workflow editor
   - Workflow templates library
   - Better error messages
   - Workflow simulation/dry-run mode

6. **Testing**:
   - Comprehensive unit tests
   - Integration tests
   - Performance benchmarks
   - Chaos testing for edge cases

7. **Scale & Performance**:
   - Queue-based execution (Celery/RQ)
   - Distributed execution
   - Caching layer
   - State compression

##  Architecture Decisions

### Why FastAPI?
- Modern async support
- Automatic API documentation
- Type validation with Pydantic
- Great developer experience

### Why In-Memory Storage?
- Simplicity for the assignment
- No external dependencies
- Easy to test
- Can be swapped for DB easily

### Why Simple Condition Evaluation?
- Safe eval with restricted context
- Easy to understand and debug
- Sufficient for most use cases
- Can be extended to full expression language

### Code Structure
- **Separation of Concerns**: Engine, storage, tools, API are separate
- **Type Safety**: Pydantic models throughout
- **Extensibility**: Easy to add new tools and workflows
- **Clean APIs**: RESTful design with clear semantics


Created as part of the AI Engineering Internship coding assignment.

---

**Note**: This is a minimal but functional implementation focusing on clean code, clear structure, and core workflow engine capabilities. It demonstrates understanding of Python, async programming, API design, and system architecture.
