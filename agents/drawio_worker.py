# agents/drawio_worker.py
import datetime
import os
import re
from langchain_openai import ChatOpenAI

def drawio_worker(state):
    iteration = state.get('iteration_count', 1)
    session_id = state.get('session_id', 'unknown')
    diagram_type = state.get('diagram_type', 'Class')
    print(f"📐 [Draw.io Worker] Generating {diagram_type} XML... (Iteration {iteration})")
    
    llm = ChatOpenAI(model=os.getenv("MODEL_NAME"), temperature=0)
    
    # Route to appropriate generator based on diagram type
    if 'sequence' in diagram_type.lower():
        xml = generate_sequence_diagram(llm, state)
    elif 'class' in diagram_type.lower():
        xml = generate_class_diagram(llm, state)
    elif 'flow' in diagram_type.lower():
        xml = generate_flowchart_diagram(llm, state)
    elif 'state' in diagram_type.lower():
        xml = generate_state_diagram(llm, state)
    else:
        print(f"   ⚠️ Unknown diagram type: {diagram_type}. Defaulting to Class diagram.")
        xml = generate_class_diagram(llm, state)
    
    # Save diagram file
    os.makedirs("output", exist_ok=True)
    diagram_file = f"output/{session_id}_diagram.drawio"
    with open(diagram_file, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"   ✅ Diagram saved to: {diagram_file} ({len(xml)} chars)")
    
    return {
        "diagram_code": xml,
        "diagram_file": diagram_file
    }

def generate_sequence_diagram(llm, state):
    """Generate sequence diagram"""
    prompt = f"""
Extract participants and interactions from this plan:

Plan: {state['plan']}

Output format:
PARTICIPANTS:
- ParticipantName

INTERACTIONS:
- Source -> Target: message
"""
    analysis = llm.invoke(prompt).content
    participants, interactions = parse_sequence_data(analysis)
    return generate_drawio_sequence_xml(participants, interactions)

def generate_class_diagram(llm, state):
    """Generate class diagram"""
    prompt = f"""
Extract entities and relationships from this plan:

Plan: {state['plan']}

Output format:
ENTITIES:
- EntityName: attr1, attr2

RELATIONSHIPS:
- Entity1 -> Entity2: relationship
"""
    analysis = llm.invoke(prompt).content
    entities, relationships = parse_class_data(analysis)
    return generate_drawio_xml(entities, relationships)

def generate_flowchart_diagram(llm, state):
    """Generate flowchart diagram"""
    prompt = f"""
Extract steps and flows from this plan:

Plan: {state['plan']}

Output format:
STEPS:
- StepName: description

FLOWS:
- Step1 -> Step2
"""
    analysis = llm.invoke(prompt).content
    steps, flows = parse_flowchart_data(analysis)
    return generate_drawio_flowchart_xml(steps, flows)

def generate_state_diagram(llm, state):
    """Generate state diagram"""
    prompt = f"""
Extract states and transitions from this plan:

Plan: {state['plan']}

Output format:
STATES:
- StateName

TRANSITIONS:
- State1 -> State2: event
"""
    analysis = llm.invoke(prompt).content
    states, transitions = parse_state_data(analysis)
    return generate_drawio_state_xml(states, transitions)

def parse_sequence_data(analysis):
    participants = []
    interactions = []
    lines = analysis.split('\n')
    in_participants = False
    in_interactions = False
    
    for line in lines:
        line = line.strip()
        if 'PARTICIPANTS:' in line:
            in_participants = True
            in_interactions = False
        elif 'INTERACTIONS:' in line:
            in_participants = False
            in_interactions = True
        elif line.startswith('-') and in_participants:
            participants.append(line[1:].strip())
        elif line.startswith('-') and in_interactions:
            interactions.append(line[1:].strip())
    
    return participants, interactions

def parse_class_data(analysis):
    entities = []
    relationships = []
    lines = analysis.split('\n')
    in_entities = False
    in_relationships = False
    
    for line in lines:
        line = line.strip()
        if 'ENTITIES:' in line:
            in_entities = True
            in_relationships = False
        elif 'RELATIONSHIPS:' in line:
            in_entities = False
            in_relationships = True
        elif line.startswith('-') and in_entities:
            entities.append(line[1:].strip())
        elif line.startswith('-') and in_relationships:
            relationships.append(line[1:].strip())
    
    return entities, relationships

def parse_flowchart_data(analysis):
    steps = []
    flows = []
    lines = analysis.split('\n')
    in_steps = False
    in_flows = False
    
    for line in lines:
        line = line.strip()
        if 'STEPS:' in line:
            in_steps = True
            in_flows = False
        elif 'FLOWS:' in line:
            in_steps = False
            in_flows = True
        elif line.startswith('-') and in_steps:
            steps.append(line[1:].strip())
        elif line.startswith('-') and in_flows:
            flows.append(line[1:].strip())
    
    return steps, flows

def parse_state_data(analysis):
    states = []
    transitions = []
    lines = analysis.split('\n')
    in_states = False
    in_transitions = False
    
    for line in lines:
        line = line.strip()
        if 'STATES:' in line:
            in_states = True
            in_transitions = False
        elif 'TRANSITIONS:' in line:
            in_states = False
            in_transitions = True
        elif line.startswith('-') and in_states:
            states.append(line[1:].strip())
        elif line.startswith('-') and in_transitions:
            transitions.append(line[1:].strip())
    
    return states, transitions

def generate_drawio_flowchart_xml(steps, flows):
    """Generate flowchart XML"""
    xml_parts = []
    xml_parts.append('<mxfile host="app.diagrams.net">')
    xml_parts.append('  <diagram name="Flowchart" id="flowchart">')
    xml_parts.append('    <mxGraphModel dx="1044" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">')
    xml_parts.append('      <root>')
    xml_parts.append('        <mxCell id="0"/>')
    xml_parts.append('        <mxCell id="1" parent="0"/>')
    
    cell_id = 2
    step_ids = {}
    y_pos = 100
    
    for i, step in enumerate(steps):
        if ':' in step:
            name, desc = step.split(':', 1)
            name = name.strip()
        else:
            name = step.strip()
        
        step_ids[name] = cell_id
        xml_parts.append(f'        <mxCell id="{cell_id}" value="{name}" style="rounded=1;whiteSpace=wrap;html=1;" vertex="1" parent="1">')
        xml_parts.append(f'          <mxGeometry x="300" y="{y_pos}" width="120" height="60" as="geometry"/>')
        xml_parts.append('        </mxCell>')
        cell_id += 1
        y_pos += 100
    
    for flow in flows:
        if '->' in flow:
            parts = flow.split('->')
            source = parts[0].strip()
            target = parts[1].strip()
            
            source_id = step_ids.get(source)
            target_id = step_ids.get(target)
            
            if source_id and target_id:
                xml_parts.append(f'        <mxCell id="{cell_id}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="{source_id}" target="{target_id}">')
                xml_parts.append('          <mxGeometry relative="1" as="geometry"/>')
                xml_parts.append('        </mxCell>')
                cell_id += 1
    
    xml_parts.append('      </root>')
    xml_parts.append('    </mxGraphModel>')
    xml_parts.append('  </diagram>')
    xml_parts.append('</mxfile>')
    
    return '\n'.join(xml_parts)

def generate_drawio_state_xml(states, transitions):
    """Generate state diagram XML"""
    xml_parts = []
    xml_parts.append('<mxfile host="app.diagrams.net">')
    xml_parts.append('  <diagram name="State Diagram" id="state-diagram">')
    xml_parts.append('    <mxGraphModel dx="1044" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">')
    xml_parts.append('      <root>')
    xml_parts.append('        <mxCell id="0"/>')
    xml_parts.append('        <mxCell id="1" parent="0"/>')
    
    cell_id = 2
    state_ids = {}
    x_pos = 100
    y_pos = 200
    
    for i, state in enumerate(states):
        state_ids[state] = cell_id
        xml_parts.append(f'        <mxCell id="{cell_id}" value="{state}" style="ellipse;whiteSpace=wrap;html=1;" vertex="1" parent="1">')
        xml_parts.append(f'          <mxGeometry x="{x_pos}" y="{y_pos}" width="120" height="80" as="geometry"/>')
        xml_parts.append('        </mxCell>')
        cell_id += 1
        x_pos += 200
        if (i + 1) % 3 == 0:
            x_pos = 100
            y_pos += 150
    
    for transition in transitions:
        if '->' in transition:
            parts = transition.split('->')
            source = parts[0].strip()
            target_part = parts[1].strip()
            if ':' in target_part:
                target, event = target_part.split(':', 1)
                target = target.strip()
                event = event.strip()
            else:
                target = target_part
                event = ""
            
            source_id = state_ids.get(source)
            target_id = state_ids.get(target)
            
            if source_id and target_id:
                xml_parts.append(f'        <mxCell id="{cell_id}" value="{event}" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="{source_id}" target="{target_id}">')
                xml_parts.append('          <mxGeometry relative="1" as="geometry"/>')
                xml_parts.append('        </mxCell>')
                cell_id += 1
    
    xml_parts.append('      </root>')
    xml_parts.append('    </mxGraphModel>')
    xml_parts.append('  </diagram>')
    xml_parts.append('</mxfile>')
    
    return '\n'.join(xml_parts)

def generate_drawio_xml(entities, relationships):
    """Generate complete Draw.io XML from entities and relationships"""
    
    xml_parts = []
    xml_parts.append('<mxfile host="app.diagrams.net">')
    xml_parts.append('  <diagram name="Class Diagram" id="class-diagram">')
    xml_parts.append('    <mxGraphModel dx="1044" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">')
    xml_parts.append('      <root>')
    xml_parts.append('        <mxCell id="0"/>')
    xml_parts.append('        <mxCell id="1" parent="0"/>')
    
    # Generate class boxes
    cell_id = 2
    entity_ids = {}
    y_pos = 100
    
    for i, entity in enumerate(entities):
        if ':' in entity:
            name, attrs = entity.split(':', 1)
            name = name.strip()
            attrs = attrs.strip()
        else:
            name = entity.strip()
            attrs = ""
        
        entity_ids[name] = cell_id
        x_pos = 100 + (i * 250)
        
        # Class box
        label = f"{name}|{attrs}" if attrs else name
        xml_parts.append(f'        <mxCell id="{cell_id}" value="{label}" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=26;horizontalStack=0;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginBottom=0;" vertex="1" parent="1">')
        xml_parts.append(f'          <mxGeometry x="{x_pos}" y="{y_pos}" width="200" height="120" as="geometry"/>')
        xml_parts.append('        </mxCell>')
        cell_id += 1
    
    # Generate relationships with better parsing
    for rel in relationships:
        # Parse various formats: "Author -> Book: 1 to many", "Author writes Books", etc.
        source = None
        target = None
        label = ""
        
        if '->' in rel:
            parts = rel.split('->')
            source = parts[0].strip()
            target_part = parts[1].strip()
            if ':' in target_part:
                target, label = target_part.split(':', 1)
                target = target.strip()
                label = label.strip()
            else:
                target = target_part
        elif ' to ' in rel.lower():
            # Try to extract from natural language
            words = rel.split()
            if len(words) >= 3:
                source = words[0]
                target = words[-1].rstrip('.')
        
        # Find matching entity names (case-insensitive partial match)
        if source and target:
            source_id = None
            target_id = None
            
            for entity_name, eid in entity_ids.items():
                if source.lower() in entity_name.lower() or entity_name.lower() in source.lower():
                    source_id = eid
                if target.lower() in entity_name.lower() or entity_name.lower() in target.lower():
                    target_id = eid
            
            if source_id and target_id:
                xml_parts.append(f'        <mxCell id="{cell_id}" value="{label}" style="endArrow=open;endFill=0;endSize=12;html=1;" edge="1" parent="1" source="{source_id}" target="{target_id}">')
                xml_parts.append('          <mxGeometry relative="1" as="geometry"/>')
                xml_parts.append('        </mxCell>')
                cell_id += 1
    
    xml_parts.append('      </root>')
    xml_parts.append('    </mxGraphModel>')
    xml_parts.append('  </diagram>')
    xml_parts.append('</mxfile>')
    
    return '\n'.join(xml_parts)


def generate_drawio_sequence_xml(participants, interactions):
    """Generate Draw.io XML for sequence diagram"""
    xml_parts = []
    xml_parts.append('<mxfile host="app.diagrams.net">')
    xml_parts.append('  <diagram name="Sequence Diagram" id="sequence-diagram">')
    xml_parts.append('    <mxGraphModel dx="1044" dy="600" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169">')
    xml_parts.append('      <root>')
    xml_parts.append('        <mxCell id="0"/>')
    xml_parts.append('        <mxCell id="1" parent="0"/>')
    
    cell_id = 2
    participant_ids = {}
    x_pos = 100
    y_pos = 50
    
    # Create lifelines for participants
    for participant in participants:
        participant_ids[participant] = cell_id
        xml_parts.append(f'        <mxCell id="{cell_id}" value="{participant}" style="shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;collapsible=0;recursiveResize=0;outlineConnect=0;" vertex="1" parent="1">')
        xml_parts.append(f'          <mxGeometry x="{x_pos}" y="{y_pos}" width="100" height="400" as="geometry"/>')
        xml_parts.append('        </mxCell>')
        cell_id += 1
        x_pos += 150
    
    # Create interactions
    for interaction in interactions:
        if '->' in interaction:
            parts = interaction.split('->')
            if len(parts) == 2:
                source_name = parts[0].strip()
                target_part = parts[1].strip()
                if ':' in target_part:
                    target_name, message = target_part.split(':', 1)
                    target_name = target_name.strip()
                    message = message.strip()
                else:
                    target_name = target_part
                    message = ""
                
                source_id = None
                target_id = None
                for p_name, p_id in participant_ids.items():
                    if source_name.lower() in p_name.lower() or p_name.lower() in source_name.lower():
                        source_id = p_id
                    if target_name.lower() in p_name.lower() or p_name.lower() in target_name.lower():
                        target_id = p_id
                
                if source_id and target_id:
                    xml_parts.append(f'        <mxCell id="{cell_id}" value="{message}" style="html=1;verticalAlign=bottom;endArrow=block;" edge="1" parent="1" source="{source_id}" target="{target_id}">')
                    xml_parts.append('          <mxGeometry relative="1" as="geometry"/>')
                    xml_parts.append('        </mxCell>')
                    cell_id += 1
    
    xml_parts.append('      </root>')
    xml_parts.append('    </mxGraphModel>')
    xml_parts.append('  </diagram>')
    xml_parts.append('</mxfile>')
    
    return '\n'.join(xml_parts)
