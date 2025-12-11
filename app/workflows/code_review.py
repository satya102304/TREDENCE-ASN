from app.models import GraphDefinition, Node, NodeType


def get_code_review_workflow() -> GraphDefinition:
    """
    Code Review Mini-Agent Workflow
    
    Steps:
    1. Extract functions from code
    2. Check complexity metrics
    3. Detect basic issues
    4. Suggest improvements
    5. Calculate quality score
    6. Loop back to improve if quality_score < threshold
    """
    
    # Define nodes with configurations
    node_configs = {
        "extract": Node(
            name="extract",
            type=NodeType.STANDARD,
            tool="extract_functions"
        ),
        "analyze": Node(
            name="analyze",
            type=NodeType.STANDARD,
            tool="check_complexity"
        ),
        "detect": Node(
            name="detect",
            type=NodeType.STANDARD,
            tool="detect_issues"
        ),
        "improve": Node(
            name="improve",
            type=NodeType.STANDARD,
            tool="suggest_improvements"
        ),
        "score": Node(
            name="score",
            type=NodeType.LOOP,
            tool="calculate_quality_score",
            loop_condition="state.get('quality_score', 0) < 70 and state.get('iteration', 0) < 3",
            max_iterations=3
        )
    }
    
    # Define edges with conditional branching
    edges = {
        "extract": "analyze",
        "analyze": "detect",
        "detect": "improve",
        "improve": "score",
        "score": {
            "condition": "state.get('quality_score', 0) < 70 and state.get('iteration', 0) < 3",
            "true": "improve",  # Loop back to improve
            "false": None  # Exit workflow
        }
    }
    
    return GraphDefinition(
        nodes=["extract", "analyze", "detect", "improve", "score"],
        edges=edges,
        start_node="extract",
        node_configs=node_configs
    )


# Example initial state for testing
EXAMPLE_CODE = '''
def calculate_total(items):
    total = 0
    for item in items:
        if item > 0:
            total += item
    print(f"Total: {total}")
    return total

def process_data(data):
    result = []
    for i in range(len(data)):
        if data[i] % 2 == 0:
            result.append(data[i] * 2)
        else:
            result.append(data[i])
    return result
'''

EXAMPLE_INITIAL_STATE = {
    "code": EXAMPLE_CODE,
    "quality_threshold": 70,
    "iteration": 0
}