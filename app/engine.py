from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import copy

from app.models import (
    GraphDefinition, Node, NodeType, ExecutionLog
)
from app.tools import tool_registry


class WorkflowEngine:
    """Core workflow engine that executes graphs with nodes, edges, branching, and loops."""
    
    def __init__(self):
        self.tool_registry = tool_registry
    
    async def execute_graph(
        self,
        graph: GraphDefinition,
        initial_state: Dict[str, Any],
        run_id: str
    ) -> tuple[Dict[str, Any], List[ExecutionLog]]:
        """
        Execute a workflow graph from start to finish.
        
        Args:
            graph: The graph definition with nodes and edges
            initial_state: Starting state dictionary
            run_id: Unique identifier for this run
            
        Returns:
            Tuple of (final_state, execution_log)
        """
        state = copy.deepcopy(initial_state)
        execution_log: List[ExecutionLog] = []
        
        current_node = graph.start_node
        visited_nodes = []
        
        while current_node:
            # Safety check for infinite loops
            if len(visited_nodes) > 100:
                state["_error"] = "Maximum iteration limit reached"
                break
            
            visited_nodes.append(current_node)
            
            # Get node configuration
            node_config = self._get_node_config(graph, current_node)
            
            # Execute the node
            state_before = copy.deepcopy(state)
            state, output = await self._execute_node(current_node, node_config, state)
            
            # Log execution
            log_entry = ExecutionLog(
                node=current_node,
                timestamp=datetime.now().isoformat(),
                state_before=state_before,
                state_after=copy.deepcopy(state),
                output=output
            )
            execution_log.append(log_entry)
            
            # Determine next node
            current_node = self._get_next_node(
                graph, current_node, node_config, state
            )
        
        return state, execution_log
    
    def _get_node_config(self, graph: GraphDefinition, node_name: str) -> Node:
        """Get configuration for a specific node."""
        if graph.node_configs and node_name in graph.node_configs:
            return graph.node_configs[node_name]
        
        # Default configuration
        return Node(
            name=node_name,
            type=NodeType.STANDARD,
            tool=node_name
        )
    
    async def _execute_node(
        self,
        node_name: str,
        node_config: Node,
        state: Dict[str, Any]
    ) -> tuple[Dict[str, Any], Optional[Any]]:
        """
        Execute a single node.
        
        Args:
            node_name: Name of the node
            node_config: Node configuration
            state: Current state
            
        Returns:
            Tuple of (updated_state, output)
        """
        try:
            # Get the tool/function for this node
            tool_name = node_config.tool or node_name
            tool_func = self.tool_registry.get(tool_name)
            
            # Execute the tool
            # Support both sync and async functions
            if asyncio.iscoroutinefunction(tool_func):
                result = await tool_func(state)
            else:
                result = tool_func(state)
            
            # If tool returns a dict, merge it into state
            if isinstance(result, dict):
                state.update(result)
                return state, None
            else:
                # Otherwise, store the output
                return state, result
                
        except Exception as e:
            state["_error"] = f"Error in node '{node_name}': {str(e)}"
            return state, None
    
    def _get_next_node(
        self,
        graph: GraphDefinition,
        current_node: str,
        node_config: Node,
        state: Dict[str, Any]
    ) -> Optional[str]:
        """
        Determine the next node to execute based on edges and conditions.
        
        Supports:
        - Simple edges: {"A": "B"}
        - Conditional branches: {"A": {"condition": "state['x'] > 5", "true": "B", "false": "C"}}
        - Loops: Node with loop_condition will repeat until condition is false
        """
        # Check for loop condition
        if node_config.type == NodeType.LOOP or node_config.loop_condition:
            iteration = state.get("iteration", 0)
            
            # Safety check
            if iteration >= node_config.max_iterations:
                # Exit loop, continue to next node
                pass
            elif node_config.loop_condition:
                # Evaluate loop condition
                if self._evaluate_condition(node_config.loop_condition, state):
                    # Continue looping - stay on current node
                    return current_node
        
        # Get edge from current node
        if current_node not in graph.edges:
            return None  # No more nodes
        
        edge = graph.edges[current_node]
        
        # Simple edge (string)
        if isinstance(edge, str):
            return edge
        
        # Conditional edge (dict)
        if isinstance(edge, dict):
            if "condition" in edge:
                condition = edge["condition"]
                if self._evaluate_condition(condition, state):
                    return edge.get("true")
                else:
                    return edge.get("false")
            
            # Multiple conditions
            for key, next_node in edge.items():
                if self._evaluate_condition(key, state):
                    return next_node
        
        return None
    
    def _evaluate_condition(self, condition: str, state: Dict[str, Any]) -> bool:
        """
        Safely evaluate a condition string.
        
        Examples:
            "state['quality_score'] >= 70"
            "state.get('num_issues', 0) < 3"
        """
        try:
            # Create a safe evaluation context
            context = {
                'state': state,
                '__builtins__': {}  # Restrict built-ins for safety
            }
            
            # Allow safe operations
            safe_builtins = {
                'len': len,
                'int': int,
                'float': float,
                'str': str,
                'bool': bool,
                'True': True,
                'False': False,
                'None': None
            }
            context.update(safe_builtins)
            
            return bool(eval(condition, context))
        except Exception as e:
            print(f"Condition evaluation error: {e}")
            return False


# Global engine instance
workflow_engine = WorkflowEngine()