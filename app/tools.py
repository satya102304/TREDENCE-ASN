from typing import Dict, Any, Callable
import ast
import re


class ToolRegistry:
    """Simple registry for tools (Python functions) that nodes can call."""
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def register(self, name: str, func: Callable):
        """Register a tool with a given name."""
        self._tools[name] = func
    
    def get(self, name: str) -> Callable:
        """Retrieve a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def list_tools(self) -> list:
        """List all registered tool names."""
        return list(self._tools.keys())
    
    def _register_default_tools(self):
        """Register default tools for the code review workflow."""
        # Code review tools
        self.register("extract_functions", extract_functions)
        self.register("check_complexity", check_complexity)
        self.register("detect_issues", detect_issues)
        self.register("suggest_improvements", suggest_improvements)
        self.register("calculate_quality_score", calculate_quality_score)


# Default tool implementations for Code Review workflow

def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract functions from code."""
    code = state.get("code", "")
    
    functions = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "num_args": len(node.args.args)
                })
    except SyntaxError:
        functions = [{"name": "parse_error", "line_start": 0, "num_args": 0}]
    
    state["functions"] = functions
    state["num_functions"] = len(functions)
    return state


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Check code complexity (simplified)."""
    code = state.get("code", "")
    functions = state.get("functions", [])
    
    # Simple complexity metrics
    complexity_scores = []
    for func in functions:
        # Count lines, loops, conditions as a simple metric
        lines = len(code.split('\n'))
        loops = code.count('for ') + code.count('while ')
        conditions = code.count('if ') + code.count('elif ')
        
        score = (lines * 0.1) + (loops * 2) + (conditions * 1.5)
        complexity_scores.append({
            "function": func.get("name", "unknown"),
            "score": round(score, 2)
        })
    
    state["complexity"] = complexity_scores
    state["avg_complexity"] = round(sum(s["score"] for s in complexity_scores) / len(complexity_scores), 2) if complexity_scores else 0
    return state


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """Detect basic code issues."""
    code = state.get("code", "")
    
    issues = []
    
    # Check for common issues
    if "print(" in code:
        issues.append({"type": "debug_code", "message": "Found print statements"})
    
    if len(code.split('\n')) > 100:
        issues.append({"type": "long_file", "message": "File is too long"})
    
    # Check for missing docstrings
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node):
                    issues.append({
                        "type": "missing_docstring",
                        "message": f"Function '{node.name}' missing docstring"
                    })
    except:
        pass
    
    state["issues"] = issues
    state["num_issues"] = len(issues)
    return state


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """Suggest improvements based on detected issues."""
    issues = state.get("issues", [])
    complexity = state.get("avg_complexity", 0)
    
    suggestions = []
    
    for issue in issues:
        if issue["type"] == "debug_code":
            suggestions.append("Remove debug print statements before production")
        elif issue["type"] == "missing_docstring":
            suggestions.append(f"Add docstring: {issue['message']}")
        elif issue["type"] == "long_file":
            suggestions.append("Consider splitting file into smaller modules")
    
    if complexity > 10:
        suggestions.append("Consider refactoring complex functions")
    
    state["suggestions"] = suggestions
    state["num_suggestions"] = len(suggestions)
    return state


def calculate_quality_score(state: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall quality score."""
    num_issues = state.get("num_issues", 0)
    avg_complexity = state.get("avg_complexity", 0)
    num_functions = state.get("num_functions", 1)
    
    # Simple scoring formula (0-100)
    base_score = 100
    issue_penalty = num_issues * 10
    complexity_penalty = min(avg_complexity * 2, 30)
    
    quality_score = max(0, base_score - issue_penalty - complexity_penalty)
    
    state["quality_score"] = round(quality_score, 2)
    state["iteration"] = state.get("iteration", 0) + 1
    
    return state


# Global tool registry instance
tool_registry = ToolRegistry()