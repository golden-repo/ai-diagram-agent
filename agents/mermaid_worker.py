# agents/mermaid_worker.py
import datetime
import os
import re
from langchain_openai import ChatOpenAI

def mermaid_worker(state):
    iteration = state.get('iteration_count', 1)
    session_id = state.get('session_id', 'unknown')
    diagram_type = state.get('diagram_type', 'Sequence')
    print(f"🎨 [Mermaid Worker] Generating {diagram_type} code... (Iteration {iteration})")
    
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"))
    
    correction_logs = state.get('correction_logs', [])
    feedback = "\n".join(correction_logs[-2:]) if correction_logs else "None"
    
    # Map diagram type to Mermaid syntax
    mermaid_syntax_map = {
        'sequence': 'sequenceDiagram',
        'class': 'classDiagram',
        'flowchart': 'flowchart TD',
        'flow': 'flowchart TD',
        'state': 'stateDiagram-v2'
    }
    
    # Find matching syntax
    mermaid_syntax = 'sequenceDiagram'
    for key, syntax in mermaid_syntax_map.items():
        if key in diagram_type.lower():
            mermaid_syntax = syntax
            break
    
    prompt = f"""
Generate Mermaid.js code for a {diagram_type}.

Diagram Type: {diagram_type}
Mermaid Syntax: Start with "{mermaid_syntax}"

Plan:
{state['plan']}

Previous Feedback: {feedback}

CRITICAL REQUIREMENTS:
1. Start with EXACTLY: {mermaid_syntax}
2. For Sequence diagrams:
   - Use: participant Name
   - Use: Name->>OtherName: message
3. For Class diagrams:
   - Use: class ClassName
   - Use: ClassName : +attribute
   - Use: ClassName --> OtherClass
4. For Flowcharts:
   - Use: A[Node] --> B[Node]
5. For State diagrams:
   - Use: [*] --> State1
   - Use: State1 --> State2

Return ONLY valid Mermaid code. No markdown fences. No explanations.
"""
    
    code = llm.invoke(prompt).content
    
    # Clean up
    code = re.sub(r'^```mermaid\n?|^```\n?|```$', '', code, flags=re.MULTILINE).strip()
    code = code.replace('\\n', '\n')
    
    # Validate it starts with correct syntax
    if not any(code.startswith(syntax) for syntax in mermaid_syntax_map.values()):
        print(f"   ⚠️ Warning: Code doesn't start with expected Mermaid syntax. Adding {mermaid_syntax}...")
        code = f"{mermaid_syntax}\n{code}"
    
    # Save diagram file with session ID (overwrite on each iteration)
    os.makedirs("output", exist_ok=True)
    diagram_file = f"output/{session_id}_diagram.mmd"
    with open(diagram_file, "w", encoding="utf-8") as f:
        f.write(code)
    
    # Also create an HTML viewer for easy viewing
    html_file = f"output/{session_id}_diagram.html"
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mermaid Diagram - {session_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>mermaid.initialize({{startOnLoad:true}});</script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; }}
        .mermaid {{ text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Mermaid Diagram</h1>
        <p>Session ID: {session_id}</p>
        <div class="mermaid">
{code}
        </div>
    </div>
</body>
</html>
    """
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"   ✅ Diagram saved to: {diagram_file} ({len(code)} chars)")
    print(f"   🌐 HTML viewer: {html_file} (open in browser)")
    
    return {
        "diagram_code": code,
        "diagram_file": diagram_file
    }