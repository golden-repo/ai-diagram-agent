import os
from langchain_openai import ChatOpenAI

def reviewer_agent(state):
    print("🧐 [Reviewer] Auditing output and logging corrections...")
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"), temperature=0)
    
    iteration = state.get('iteration_count', 0)
    session_id = state.get('session_id', 'unknown')
    code_length = len(state['diagram_code'])
    print(f"   Iteration: {iteration}, Code length: {code_length} chars")
    
    # Force approval on iteration 3 if code is reasonably complete
    if iteration >= 3 and code_length > 1000:
        print(f"   ✅ Auto-approving at iteration {iteration} - code appears complete")
        review_file = f"logs/{session_id}_review_iter{iteration}.txt"
        os.makedirs("logs", exist_ok=True)
        with open(review_file, "w", encoding="utf-8") as f:
            f.write(f"Session ID: {session_id}\n")
            f.write(f"Iteration: {iteration}\n")
            f.write(f"Code Length: {code_length} chars\n")
            f.write(f"Status: AUTO-APPROVED (Max iterations reached)\n")
            f.write(f"\nFeedback:\nAuto-approved after {iteration} iterations. Code is reasonably complete.\n")
            f.write(f"\n{'='*60}\n")
            f.write(f"Full Code:\n{state['diagram_code']}\n")
        return {"review_feedback": "APPROVED", "correction_logs": [f"Iter {iteration}: ✅ Auto-approved"]}
    
    # Get previous feedback
    previous_logs = state.get('correction_logs', [])
    previous_feedback = "\n".join(previous_logs[-2:]) if previous_logs else "None"
    
    # Show code preview
    code_preview = state['diagram_code'][:1500]
    if code_length > 2000:
        code_preview += "\n...\n" + state['diagram_code'][-500:]
    
    prompt = f"""
Review the generated diagram code. Be VERY LENIENT.

DESIGN: {state['design_content']}
PLANNED DIAGRAM TYPE: {state.get('diagram_type', 'Unknown')}
FORMAT: {state.get('output_format', 'unknown')}
ITERATION: {iteration}/3

CODE ({code_length} chars):
{code_preview}

For Draw.io XML:
- Sequence diagrams have: shape=umlLifeline elements
- Class diagrams have: swimlane elements with class names
- Check if diagram type matches the planned type

IMPORTANT:
- CRITICAL: Verify the diagram type matches the plan (Sequence vs Class vs Flowchart)
- If plan says "Sequence Diagram" but code has class/swimlane elements, REJECT
- If plan says "Class Diagram" but code has lifeline elements, REJECT
- If iteration >= 2, be VERY LENIENT on other aspects
- If code has proper structure and correct diagram type, APPROVE IT

Respond ONLY:
- "APPROVED" - if code looks reasonable AND diagram type matches
- "STATUS: REWORK\nLOG: [critical issue only]" - only if truly broken or wrong diagram type
"""
    
    response = llm.invoke(prompt).content
    
    # Save review
    os.makedirs("logs", exist_ok=True)
    review_file = f"logs/{session_id}_review_iter{iteration}.txt"
    with open(review_file, "w", encoding="utf-8") as f:
        f.write(f"Session ID: {session_id}\n")
        f.write(f"Iteration: {iteration}\n")
        f.write(f"Code Length: {code_length} chars\n")
        f.write(f"Status: {'APPROVED' if 'APPROVED' in response.upper() else 'REJECTED'}\n")
        f.write(f"\nFeedback:\n{response}\n")
        f.write(f"\n{'='*60}\n")
        f.write(f"Full Code:\n{state['diagram_code']}\n")
    
    if "APPROVED" in response.upper():
        print(f"   ✅ Approved! Review saved to: {review_file}")
        return {"review_feedback": "APPROVED", "correction_logs": [f"Iter {iteration}: ✅ Approved"]}
    
    print(f"   ❌ Issues found. Review saved to: {review_file}")
    return {
        "review_feedback": response,
        "correction_logs": [f"Iter {iteration}: {response[:200]}..."]
    }