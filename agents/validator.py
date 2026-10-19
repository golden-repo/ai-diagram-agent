import os
from langchain_openai import ChatOpenAI

def validator_agent(state):
    print("🔍 [Validator] Analyzing intent and requirements...")
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"))
    
    prompt = f"""
    Analyze the following design document:
    {state['design_content']}

    Check if the technical flow or purpose is clear enough to build a diagram.
    If clear, respond ONLY with "VALID". 
    If vague, respond with specific questions to clarify the intent.
    """
    
    response = llm.invoke(prompt).content
    is_valid = "VALID" in response.upper()
    
    if not is_valid:
        print(f"❌ [Validator] Issue: {response}")
    
    return {
        "is_valid": is_valid, 
        "review_feedback": "" if is_valid else response,
        "iteration_count": 0  # Keep at 0, planner will increment to 1
    }