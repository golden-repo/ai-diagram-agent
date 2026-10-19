# Developer README — AI Diagram Agent

> Detailed technical guide for developers to understand, set up, extend, and contribute to the **AI Diagram Agent** project.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Agent Workflow](#architecture--agent-workflow)
3. [File Dictionary](#file-dictionary)
4. [Prerequisites](#prerequisites)
5. [Environment Setup](#environment-setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [API Reference](#api-reference)
9. [Input File Format](#input-file-format)
10. [Output Files](#output-files)
11. [Agent Internals](#agent-internals)
12. [Self-Correction Loop](#self-correction-loop)
13. [Extending the Project](#extending-the-project)
14. [Troubleshooting](#troubleshooting)

---

## Project Overview

The AI Diagram Agent is a **multi-agent, self-correcting pipeline** that transforms plain-English design descriptions (Markdown files) into production-quality architecture diagrams. It supports **Mermaid.js** (`.mmd`, `.html`, `.png`) and **Draw.io** (`.drawio`) output formats.

Built on:

- **LangGraph** — stateful, graph-based multi-agent orchestration
- **LangChain + OpenAI** — LLM-powered code generation and review
- **FastAPI** — REST API layer
- **Playwright** — headless browser PNG rendering

---

## Architecture & Agent Workflow

```
HTTP POST /generate-diagram
         │
         ▼
  ┌─────────────┐
  │  Validator  │  ← Checks if design content is clear enough
  └──────┬──────┘
         │ is_valid = True
         ▼
  ┌─────────────┐
  │   Planner   │  ← Determines diagram type, creates step-by-step plan
  └──────┬──────┘
         │
         ▼
  ┌──────────────────┐
  │  Worker Selector │  ← Routes based on output_format
  └──┬───────────────┘
     │                │
     ▼                ▼
┌──────────┐   ┌────────────┐
│ Mermaid  │   │  Draw.io   │  ← Generates diagram source code
│  Worker  │   │   Worker   │
└────┬─────┘   └─────┬──────┘
     └────────┬───────┘
              ▼
       ┌────────────┐
       │  Reviewer  │  ← LLM audits the output; APPROVED or REWORK
       └──────┬─────┘
              │ APPROVED
              ▼
       ┌────────────┐
       │ Image Gen  │  ← Playwright renders PNG (if requested)
       └────────────┘
```

### Self-Correction Loop

If the Reviewer returns `REWORK`, the workflow loops back to the **Planner** (if REPLAN) or the **Worker** (for code-level fixes). The loop has a **maximum of 3 iterations** to prevent runaway costs. After 3 iterations, if the code is reasonably complete (>1000 chars), it is **auto-approved**.

---

## File Dictionary

| File / Folder               | Purpose                                                                                                                        |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `main.py`                   | FastAPI application entry point. Defines `/generate-diagram` and `/download/{path}` endpoints.                                 |
| `coordinator.py`            | LangGraph `StateGraph` definition. Wires all agents together and defines conditional routing logic.                            |
| `agents/__init__.py`        | Exports all agent functions for use in the coordinator.                                                                        |
| `agents/validator.py`       | Validates that the design content is clear enough to generate a diagram. Returns `is_valid` flag.                              |
| `agents/planner.py`         | Uses the LLM to determine diagram type (Sequence, Class, Flowchart, State) and produce a detailed plan. Saves plan to `logs/`. |
| `agents/mermaid_worker.py`  | Generates valid Mermaid.js code based on the plan. Saves `.mmd` and `.html` files to `output/`.                                |
| `agents/drawio_worker.py`   | Generates Draw.io XML for multiple diagram types (Sequence, Class, Flowchart, State). Saves `.drawio` to `output/`.            |
| `agents/reviewer.py`        | LLM-based auditor that checks diagram correctness and type alignment. Returns `APPROVED` or `REWORK` with log.                 |
| `agents/image_gen.py`       | Renders Mermaid HTML or Draw.io XML to PNG using Playwright headless Chromium.                                                 |
| `pyproject.toml`            | Python project metadata (uv/pip compatible).                                                                                   |
| `uv.lock`                   | Locked dependency file for reproducible installs via `uv`.                                                                     |
| `setup.bat`                 | Windows setup script — creates venv and installs dependencies.                                                                 |
| `setup.sh`                  | Linux/macOS setup script — creates venv and installs dependencies.                                                             |
| `design.md`                 | **Example** input design file. Use as a template for your own inputs.                                                          |
| `output/`                   | All generated diagram files (`*.mmd`, `*.html`, `*.png`, `*.drawio`) keyed by session ID.                                      |
| `logs/`                     | Per-iteration plan and review logs keyed by session ID (e.g., `{session_id}_plan_iter1.txt`).                                  |
| `*.design.md`               | Various example design specification files included in the repo for testing.                                                   |
| `FILE_NAMING_CONVENTION.md` | Naming conventions used across the project.                                                                                    |

---

## Prerequisites

| Tool                | Version        | Notes                                                                    |
| ------------------- | -------------- | ------------------------------------------------------------------------ |
| Python              | ≥ 3.10         | Required for `match` syntax and type hints                               |
| `uv`                | latest         | Fast Python package manager ([install](https://github.com/astral-sh/uv)) |
| Node.js / npm       | optional       | Only needed if using Mermaid CLI directly                                |
| OpenAI API key      | —              | GPT-4o or GPT-4-turbo recommended                                        |
| Playwright Chromium | auto-installed | Required for PNG image generation                                        |

---

## Environment Setup

### Option 1 — Using `uv` (Recommended)

```bash
# Install uv if not already installed
pip install uv

# Create virtual environment and install all dependencies
uv sync

# Activate the virtual environment
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### Option 2 — Using `setup.bat` / `setup.sh`

**Windows:**

```bat
setup.bat
```

**Linux / macOS:**

```bash
chmod +x setup.sh
./setup.sh
```

### Option 3 — Manual pip

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install fastapi uvicorn langgraph langchain langchain-openai \
            python-multipart python-dotenv playwright

# Install Playwright browser binaries
playwright install chromium
```

---

## Configuration

Create a `.env` file at the project root:

```env
OPENAI_API_KEY=sk-...your-key-here...
MODEL_NAME=gpt-4o
```

| Variable         | Default  | Description                                                     |
| ---------------- | -------- | --------------------------------------------------------------- |
| `OPENAI_API_KEY` | —        | **Required.** Your OpenAI API key.                              |
| `MODEL_NAME`     | `gpt-4o` | The OpenAI model used by all agents. GPT-4o gives best results. |

> **Tip:** Never commit `.env` to version control. Add it to `.gitignore`.

---

## Running the Application

### Start the FastAPI server

```bash
uvicorn main:app --reload
```

The server starts at `http://127.0.0.1:8000`.

### Optional flags

```bash
# Custom port
uvicorn main:app --host 0.0.0.0 --port 8080 --reload

# Production (no reload)
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

### VS Code Debug Configuration

Add to `.vscode/launch.json`:

```json
{
  "configurations": [
    {
      "name": "FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload"],
      "jinja": true
    }
  ]
}
```

---

## API Reference

### `POST /generate-diagram`

Accepts a multipart form with:

| Field         | Type           | Description                                |
| ------------- | -------------- | ------------------------------------------ |
| `design_file` | `file` (`.md`) | Markdown design description                |
| `payload`     | JSON string    | Options: `output_format`, `generate_image` |

**Payload options:**

```json
{
  "output_format": "mermaid", // "mermaid" or "drawio"
  "generate_image": true // true = render PNG via Playwright
}
```

**Example cURL:**

```bash
curl -X POST "http://127.0.0.1:8000/generate-diagram" \
     -F "design_file=@design.md" \
     -F 'payload={"output_format": "mermaid", "generate_image": true}'
```

**Example Response:**

```json
{
  "session_id": "a1b2c3d4",
  "status": "completed",
  "output_format": "mermaid",
  "files": {
    "diagram": "http://localhost:8000/download/output/a1b2c3d4_diagram.mmd",
    "source": "http://localhost:8000/download/output/a1b2c3d4_diagram.mmd",
    "html_viewer": "http://localhost:8000/download/output/a1b2c3d4_diagram.html",
    "image": "http://localhost:8000/download/output/a1b2c3d4_diagram.png"
  },
  "iterations": 1,
  "review_feedback": "APPROVED"
}
```

### `GET /download/{file_path}`

Downloads any file from `output/` or `logs/` by relative path. Enforces path prefix security.

---

## Input File Format

Design files are plain Markdown. Two optional directives control output:

```markdown
# Your Design Title

Describe your system in plain English. Be specific about:

- The components / actors involved
- The interactions / data flow
- Any business rules or decision points

Output: mermaid # or "drawio"
GenerateImage: Yes # or "No"
```

If `Output` or `GenerateImage` are absent, defaults are taken from the API payload.

**Supported diagram types** (auto-detected by the Planner):

| Keyword in plan  | Diagram Generated     |
| ---------------- | --------------------- |
| Sequence         | Sequence diagram      |
| Class            | Class diagram         |
| Flowchart / Flow | Flowchart (TD)        |
| State            | State machine diagram |

---

## Output Files

All output is written to the `output/` folder, namespaced by an 8-character session ID:

| File                  | Format  | Description                                 |
| --------------------- | ------- | ------------------------------------------- |
| `{id}_diagram.mmd`    | Mermaid | Raw Mermaid.js source code                  |
| `{id}_diagram.html`   | HTML    | Self-contained HTML viewer with Mermaid CDN |
| `{id}_diagram.png`    | PNG     | Rendered image via Playwright               |
| `{id}_diagram.drawio` | XML     | Draw.io compatible XML file                 |

Logs are written to `logs/`:

| File                      | Description                                             |
| ------------------------- | ------------------------------------------------------- |
| `{id}_plan_iter{n}.txt`   | LLM-generated plan for iteration N                      |
| `{id}_review_iter{n}.txt` | Reviewer feedback and full diagram code for iteration N |

---

## Agent Internals

### `AgentState` (coordinator.py)

The shared state passed between all agents:

```python
class AgentState(TypedDict):
    design_content: str       # Raw markdown from uploaded file
    output_format: str        # "mermaid" or "drawio"
    generate_image: bool      # Whether to render PNG
    is_valid: bool            # Set by Validator
    plan: str                 # Set by Planner
    diagram_type: str         # "Sequence", "Class", "Flowchart", "State"
    diagram_code: str         # Generated diagram source
    correction_logs: List[str]# Accumulated per-iteration feedback
    review_feedback: str      # Latest Reviewer verdict
    iteration_count: int      # Current loop count (max 3)
    session_id: str           # 8-char UUID prefix for file naming
```

### Conditional Routing Logic

```
validator  → planner         (if is_valid)
validator  → END             (if not is_valid)
planner    → worker_selector
worker_selector → mermaid_worker   (if output_format != "drawio")
worker_selector → drawio_worker    (if output_format == "drawio")
reviewer   → image_gen       (if APPROVED and generate_image)
reviewer   → END             (if APPROVED and not generate_image)
reviewer   → planner         (if REWORK + REPLAN keyword)
reviewer   → worker_selector (if REWORK without REPLAN)
reviewer   → END             (if iteration_count >= 3)
```

---

## Self-Correction Loop

The system implements a **maximum 3-iteration correction loop**:

1. **Iteration 1** — Planner creates initial plan → Worker generates code → Reviewer audits
2. **Iteration 2** — If REWORK, Planner refines plan with feedback → Worker regenerates → Reviewer re-audits
3. **Iteration 3** — Final attempt. If code > 1000 chars, **auto-approved** regardless of LLM verdict to prevent runaway costs

The correction logs accumulate and are injected into every subsequent Planner and Worker prompt, giving the LLM full context of what went wrong in previous iterations.

---

## Extending the Project

### Adding a New Output Format (e.g., PlantUML)

1. Create `agents/plantuml_worker.py` following the pattern of `mermaid_worker.py`
2. Export the function in `agents/__init__.py`
3. In `coordinator.py`, add the node and update the `worker_selector` conditional edge:
   ```python
   workflow.add_node("plantuml_worker", plantuml_worker)
   workflow.add_conditional_edges("worker_selector",
       lambda x: "drawio_worker" if x.get("output_format") == "drawio"
                 else "plantuml_worker" if x.get("output_format") == "plantuml"
                 else "mermaid_worker")
   ```
4. Update `main.py` to collect the new output file path in the response.

### Adding a New Diagram Type

In `mermaid_worker.py`, add to `mermaid_syntax_map`:

```python
mermaid_syntax_map = {
    ...
    'er': 'erDiagram',
    'gantt': 'gantt',
}
```

In `drawio_worker.py`, add a new `generate_*_diagram` function and update the routing `if/elif` chain.

### Swapping the LLM Provider

Replace `ChatOpenAI` imports with your preferred LangChain provider (e.g., `ChatAnthropic`, `ChatGoogleGenerativeAI`) in each agent file. The prompts are provider-agnostic.

---

## Troubleshooting

| Problem                          | Solution                                                                               |
| -------------------------------- | -------------------------------------------------------------------------------------- |
| `uvicorn: command not found`     | Activate your virtual environment first: `.venv\Scripts\activate`                      |
| `OPENAI_API_KEY not set`         | Create `.env` with your key and ensure `load_dotenv()` is called                       |
| `Port 8000 already in use`       | Use `--port 8001` or kill the process holding port 8000                                |
| PNG not generated                | Run `playwright install chromium` to install the browser binary                        |
| Draw.io PNG blank/partial        | Draw.io iframe needs network access. Ensure firewall allows `viewer.diagrams.net`      |
| Validator rejects valid input    | Make design description more specific; mention actors, flows, and decisions explicitly |
| `ModuleNotFoundError: langgraph` | Run `uv sync` or `pip install langgraph langchain langchain-openai`                    |
| Auto-approved at iteration 3     | Acceptable — check `logs/{id}_review_iter3.txt` for details; refine your design prompt |

---

_For project overview and business context, see [README.md](./readme.md)._
