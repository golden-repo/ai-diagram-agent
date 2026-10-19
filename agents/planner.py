import os, datetime
from langchain_openai import ChatOpenAI

def planning_agent(state):
    print("📋 [Planner] Determining Diagram Type & Strategy...")
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"), temperature=0.3)
    
    # Planner increments iteration at the start of each planning cycle
    current_iteration = state.get("iteration_count", 0) + 1
    
    session_id = state.get("session_id", "unknown")
    correction_logs = state.get("correction_logs", [])
    previous_plan = state.get("plan", "")
    
    # Build feedback context from previous iterations
    feedback_context = ""
    if correction_logs:
        feedback_context = f"""
PREVIOUS ATTEMPTS AND FEEDBACK:
{chr(10).join(correction_logs)}

PREVIOUS PLAN THAT FAILED:
{previous_plan}

IMPORTANT: Learn from the feedback above and adjust your approach.
"""
    
    prompt = f"""
You are an expert diagram planner. Analyze the design and create a detailed plan.

{feedback_context}

DESIGN REQUIREMENTS:
{state['design_content']}

OUTPUT FORMAT: {state.get('output_format', 'mermaid')}

Tasks:
1. Determine the best diagram type (Sequence, Class, Flowchart, etc.)
2. Create a step-by-step plan that addresses ALL requirements
3. If this is a retry, specifically address the previous feedback

Output EXACTLY in this format:
DIAGRAM_TYPE: [Type]
PLAN:
[Detailed step-by-step plan]
"""
    
    response = llm.invoke(prompt).content
    
    # Extract diagram type
    diag_type = "Sequence"
    if "Class" in response: diag_type = "Class"
    elif "Flowchart" in response: diag_type = "Flowchart"

    # Save plan with session ID
    os.makedirs("logs", exist_ok=True)
    plan_file = f"logs/{session_id}_plan_iter{current_iteration}.txt"
    with open(plan_file, "w", encoding="utf-8") as f:
        f.write(f"Session ID: {session_id}\n")
        f.write(f"Iteration: {current_iteration}\n")
        f.write(f"\n{response}")
    
    print(f"   Plan saved to: {plan_file}")
    return {
        "plan": response, 
        "diagram_type": diag_type, 
        "plan_file": plan_file,
        "iteration_count": current_iteration
    }