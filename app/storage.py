from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.models import GraphDefinition, ExecutionLog


class InMemoryStorage:
    """Simple in-memory storage for graphs and workflow runs."""
    
    def __init__(self):
        self.graphs: Dict[str, GraphDefinition] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
    
    def create_graph(self, graph: GraphDefinition) -> str:
        """Store a graph definition and return its ID."""
        graph_id = str(uuid.uuid4())
        self.graphs[graph_id] = graph
        return graph_id
    
    def get_graph(self, graph_id: str) -> Optional[GraphDefinition]:
        """Retrieve a graph by ID."""
        return self.graphs.get(graph_id)
    
    def create_run(
        self,
        graph_id: str,
        initial_state: Dict[str, Any]
    ) -> str:
        """Create a new workflow run."""
        run_id = str(uuid.uuid4())
        self.runs[run_id] = {
            "run_id": run_id,
            "graph_id": graph_id,
            "initial_state": initial_state,
            "current_state": initial_state.copy(),
            "current_node": None,
            "status": "running",
            "execution_log": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return run_id
    
    def update_run(
        self,
        run_id: str,
        final_state: Dict[str, Any],
        execution_log: list,
        status: str = "completed"
    ):
        """Update a workflow run with results."""
        if run_id in self.runs:
            self.runs[run_id].update({
                "current_state": final_state,
                "status": status,
                "execution_log": execution_log,
                "updated_at": datetime.now().isoformat()
            })
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve run information."""
        return self.runs.get(run_id)
    
    def list_graphs(self) -> list:
        """List all graph IDs."""
        return list(self.graphs.keys())
    
    def list_runs(self, graph_id: Optional[str] = None) -> list:
        """List all runs, optionally filtered by graph_id."""
        if graph_id:
            return [
                run for run in self.runs.values()
                if run["graph_id"] == graph_id
            ]
        return list(self.runs.values())


# Global storage instance
storage = InMemoryStorage()