# AI Multi-Agent Self-Correcting Diagram System

## Purpose

To orchestrate a highly resilient multi-agent workflow that transforms natural language intent into validated diagrams (Mermaid/Drawio) and high-quality images. The system features an iterative feedback loop where agents analyze failures to improve their subsequent attempts, capped at a hard limit of 3 iterations.
I want you to generate the sequence diagram and very detailed one. It should cover positive and nagative flows.

## Participants / Components

- **User**: Initiator of the request via API or Markdown file.
- **FastAPI_Endpoint**: The gateway for input parsing and response delivery.
- **Coordinator**: The LangGraph state machine maintaining state and loop counters.
- **Validator_Agent**: Scans for semantic clarity and identifies missing requirements.
- **Planner_Agent**: The Architect. Determines diagram type and detailed implementation steps.
- **Worker_Agent**: The Developer. Specialized in Mermaid or Draw.io XML generation.
- **Reviewer_Agent**: The Quality Gate. Audits output against the plan and design logic.
- **ImageGen_Agent**: Headless renderer for final PNG generation.

## Sequence Flow Description

### 1. Initialization & Validation

- **User** submits the design document.
- **Validator_Agent** analyzes for ambiguity.
  - **Positive**: Returns "VALID".
  - **Negative**: Returns clarifying questions. (Loop: Back to User/Input).

### 2. Planning Phase

- **Planner_Agent** extracts entities and logic.
- **Self-Learning Step**: Planner reads `correction_logs` from previous failed iterations (if any) to refine the new strategy.

### 3. Execution Phase

- **Coordinator** routes to the **Worker_Agent** (Mermaid/Drawio) based on the Planner's choice.
- **Worker_Agent** generates the source code for the diagram.

### 4. Review & Iterative Self-Correction (The Feedback Loop)

- **Reviewer_Agent** performs a dual-check:
  1. **Compliance**: Does the diagram match the **Design Requirement**?
  2. **Consistency**: Did the Worker follow the **Planner's Steps**?
- **Decision Logic**:
  - **APPROVED (Positive Flow)**: If the code is perfect, proceed to **ImageGen_Agent**.
  - **REPLAN (Negative Flow - Logic Error)**: If the diagram logic is flawed or the Planner missed a requirement, the Reviewer logs the failure and sends control back to **Planner_Agent**.
  - **REWORK (Negative Flow - Syntax/Style Error)**: If the plan was good but the Worker's code is broken or ugly, the Reviewer logs the failure and sends control back to **Worker_Agent**.
  - Maximum 3 times of iterations possible.

### 5. Termination & Output

- **Max Iterations**: The **Coordinator** tracks `iteration_count`. If a 4th iteration is triggered, the system stops and returns the best-available code along with a "Failure: Max Iterations Reached" log.
- **Final Artifact**: Upon approval, **ImageGen_Agent** produces the PNG. The **User** receives the code, the image path, and a full `correction_logs` history.

## Configuration

Output: Mermaid
GenerateImage: Yes
