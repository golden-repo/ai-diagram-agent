import operator
from typing import Annotated, List, TypedDict
from langgraph.graph import StateGraph, END
from agents import *

class AgentState(TypedDict):
    design_content: str
    output_format: str
    generate_image: bool
    is_valid: bool
    plan: str
    diagram_type: str
    diagram_code: str
    correction_logs: Annotated[List[str], operator.add]
    review_feedback: str
    iteration_count: int
    session_id: str

def create_coordinator():
    workflow = StateGraph(AgentState)

    workflow.add_node("validator", validator_agent)
    workflow.add_node("planner", planning_agent)
    workflow.add_node("mermaid_worker", mermaid_worker)
    workflow.add_node("drawio_worker", drawio_worker)
    workflow.add_node("reviewer", reviewer_agent)
    workflow.add_node("image_gen", image_gen_agent)

    # Routes
    workflow.set_entry_point("validator")
    workflow.add_conditional_edges("validator", lambda x: "planner" if x["is_valid"] else END)
    
    workflow.add_node("worker_selector", lambda x: x)
    workflow.add_edge("planner", "worker_selector")
    workflow.add_conditional_edges("worker_selector", 
        lambda x: "drawio_worker" if x.get("output_format") == "drawio" else "mermaid_worker")
    
    workflow.add_edge("mermaid_worker", "reviewer")
    workflow.add_edge("drawio_worker", "reviewer")
    
    def after_review(x):
        # Max iteration check to prevent infinite loops
        max_iterations = 3
        current_iteration = x.get('iteration_count', 0)
        
        if current_iteration >= max_iterations:
            print(f"⚠️ [Coordinator] Max iterations ({max_iterations}) reached. Ending workflow.")
            return END
        
        if "APPROVED" in x["review_feedback"].upper():
            return "image_gen" if x.get("generate_image") else END
        return "planner" if "REPLAN" in x["review_feedback"] else "worker_selector"

    workflow.add_conditional_edges("reviewer", after_review)
    workflow.add_edge("image_gen", END)

    return workflow.compile()