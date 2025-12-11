from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Callable
from enum import Enum


class NodeType(str, Enum):
    STANDARD = "standard"
    CONDITIONAL = "conditional"
    LOOP = "loop"


class Node(BaseModel):
    name: str
    type: NodeType = NodeType.STANDARD
    tool: Optional[str] = None
    condition: Optional[str] = None  # For conditional nodes
    loop_condition: Optional[str] = None  # For loop nodes
    max_iterations: int = 10  # Safety limit for loops


class GraphDefinition(BaseModel):
    nodes: List[str]
    edges: Dict[str, Any]  # Can be str or dict for conditional branching
    start_node: str
    node_configs: Optional[Dict[str, Node]] = None


class GraphCreateRequest(BaseModel):
    nodes: List[str]
    edges: Dict[str, Any]
    start_node: str
    node_configs: Optional[Dict[str, Node]] = None


class GraphCreateResponse(BaseModel):
    graph_id: str
    message: str = "Graph created successfully"


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


class ExecutionLog(BaseModel):
    node: str
    timestamp: str
    state_before: Dict[str, Any]
    state_after: Dict[str, Any]
    output: Optional[Any] = None


class GraphRunResponse(BaseModel):
    run_id: str
    graph_id: str
    final_state: Dict[str, Any]
    execution_log: List[ExecutionLog]
    status: str = "completed"


class StateResponse(BaseModel):
    run_id: str
    graph_id: str
    current_state: Dict[str, Any]
    current_node: Optional[str] = None
    status: str
    execution_log: List[ExecutionLog]


class ToolRegistration(BaseModel):
    name: str
    description: Optional[str] = None