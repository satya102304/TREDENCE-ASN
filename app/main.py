from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any

from app.models import (
    GraphCreateRequest, GraphCreateResponse,
    GraphRunRequest, GraphRunResponse,
    StateResponse, ToolRegistration,
    GraphDefinition
)
from app.storage import storage
from app.engine import workflow_engine
from app.tools import tool_registry
from app.workflows.code_review import get_code_review_workflow, EXAMPLE_INITIAL_STATE


app = FastAPI(
    title="Workflow Engine API",
    description="A minimal workflow/graph engine with nodes, edges, branching, and loops",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Workflow Engine API",
        "version": "1.0.0",
        "endpoints": {
            "create_graph": "POST /graph/create",
            "run_graph": "POST /graph/run",
            "get_state": "GET /graph/state/{run_id}",
            "list_graphs": "GET /graphs",
            "register_tool": "POST /tools/register",
            "list_tools": "GET /tools",
            "example_workflow": "GET /example/code-review"
        }
    }


@app.post("/graph/create", response_model=GraphCreateResponse)
async def create_graph(request: GraphCreateRequest):
    """
    Create a new workflow graph.
    
    Example:
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
    """
    try:
        graph = GraphDefinition(
            nodes=request.nodes,
            edges=request.edges,
            start_node=request.start_node,
            node_configs=request.node_configs
        )
        
        graph_id = storage.create_graph(graph)
        
        return GraphCreateResponse(
            graph_id=graph_id,
            message="Graph created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/graph/run", response_model=GraphRunResponse)
async def run_graph(request: GraphRunRequest):
    """
    Execute a workflow graph with an initial state.
    
    Example:
    ```json
    {
        "graph_id": "abc-123",
        "initial_state": {
            "code": "def hello(): return 'world'"
        }
    }
    ```
    """
    try:
        # Get the graph
        graph = storage.get_graph(request.graph_id)
        if not graph:
            raise HTTPException(status_code=404, detail="Graph not found")
        
        # Create a run
        run_id = storage.create_run(request.graph_id, request.initial_state)
        
        # Execute the workflow
        final_state, execution_log = await workflow_engine.execute_graph(
            graph, request.initial_state, run_id
        )
        
        # Update storage
        status = "completed" if "_error" not in final_state else "failed"
        storage.update_run(run_id, final_state, execution_log, status)
        
        return GraphRunResponse(
            run_id=run_id,
            graph_id=request.graph_id,
            final_state=final_state,
            execution_log=execution_log,
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=StateResponse)
async def get_run_state(run_id: str):
    """
    Get the current state of a workflow run.
    """
    run = storage.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return StateResponse(
        run_id=run["run_id"],
        graph_id=run["graph_id"],
        current_state=run["current_state"],
        current_node=run.get("current_node"),
        status=run["status"],
        execution_log=run["execution_log"]
    )


@app.get("/graphs")
async def list_graphs():
    """List all created graphs."""
    graph_ids = storage.list_graphs()
    return {
        "graphs": graph_ids,
        "count": len(graph_ids)
    }


@app.get("/runs")
async def list_runs(graph_id: str = None):
    """List all workflow runs, optionally filtered by graph_id."""
    runs = storage.list_runs(graph_id)
    return {
        "runs": runs,
        "count": len(runs)
    }


@app.post("/tools/register")
async def register_tool(registration: ToolRegistration):
    """
    Register a new tool (placeholder endpoint).
    In a real implementation, this would allow dynamic tool registration.
    """
    return {
        "message": f"Tool registration endpoint (not fully implemented)",
        "tool_name": registration.name,
        "note": "Use tool_registry.register() in code to add tools"
    }


@app.get("/tools")
async def list_tools():
    """List all registered tools."""
    tools = tool_registry.list_tools()
    return {
        "tools": tools,
        "count": len(tools)
    }


@app.get("/example/code-review")
async def get_example_workflow():
    """
    Get the example code review workflow definition.
    This is a complete, ready-to-use workflow.
    """
    workflow = get_code_review_workflow()
    return {
        "workflow": workflow.model_dump(),
        "example_initial_state": EXAMPLE_INITIAL_STATE,
        "usage": "Use POST /graph/create with this workflow definition, then POST /graph/run with the example_initial_state"
    }


@app.post("/example/run")
async def run_example_workflow():
    """
    Run the example code review workflow with sample code.
    This is a convenience endpoint to test the system quickly.
    """
    # Create the workflow
    workflow = get_code_review_workflow()
    graph_id = storage.create_graph(workflow)
    
    # Run it
    run_id = storage.create_run(graph_id, EXAMPLE_INITIAL_STATE)
    final_state, execution_log = await workflow_engine.execute_graph(
        workflow, EXAMPLE_INITIAL_STATE, run_id
    )
    
    # Update storage
    status = "completed" if "_error" not in final_state else "failed"
    storage.update_run(run_id, final_state, execution_log, status)
    
    return {
        "run_id": run_id,
        "graph_id": graph_id,
        "final_state": final_state,
        "execution_summary": {
            "total_steps": len(execution_log),
            "quality_score": final_state.get("quality_score"),
            "num_issues": final_state.get("num_issues"),
            "num_suggestions": final_state.get("num_suggestions"),
            "iterations": final_state.get("iteration")
        },
        "status": status
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)