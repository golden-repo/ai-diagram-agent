from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from coordinator import create_coordinator
import json, re, uuid, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
coordinator = create_coordinator()

@app.post("/generate-diagram")
async def run_workflow(design_file: UploadFile = File(...), payload: str = Form(...)):
    content = (await design_file.read()).decode("utf-8")
    data = json.loads(payload)
    
    # Generate session ID for tracking all related files
    session_id = str(uuid.uuid4())[:8]
    
    # Logic to detect format and image req from MD or Payload
    fmt = data.get("output_format", "mermaid")
    gen_img = data.get("generate_image", "GenerateImage: Yes" in content)

    initial_state = {
        "design_content": content,
        "output_format": fmt,
        "generate_image": gen_img,
        "correction_logs": [],
        "iteration_count": 0,
        "session_id": session_id
    }
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting new workflow - Session ID: {session_id}")
    print(f"{'='*60}\n")
    
    result = coordinator.invoke(initial_state)
    
    # Build response with downloadable file paths
    base_url = "http://localhost:8000/download/"
    response = {
        "session_id": session_id,
        "status": "completed" if result.get("review_feedback") == "APPROVED" else "completed_with_issues",
        "output_format": fmt,
        "files": {}
    }
    
    # Add source code file (always generated)
    if fmt == "mermaid":
        mmd_file = f"output/{session_id}_diagram.mmd"
        if os.path.exists(mmd_file):
            response["files"]["diagram"] = base_url + mmd_file
            response["files"]["source"] = base_url + mmd_file
        
        # Add HTML viewer for mermaid
        html_file = f"output/{session_id}_diagram.html"
        if os.path.exists(html_file):
            response["files"]["html_viewer"] = base_url + html_file
        
        # Add PNG image if generated
        png_file = f"output/{session_id}_diagram.png"
        if os.path.exists(png_file):
            response["files"]["image"] = base_url + png_file
    
    elif fmt == "drawio":
        drawio_file = f"output/{session_id}_diagram.drawio"
        if os.path.exists(drawio_file):
            response["files"]["diagram"] = base_url + drawio_file
            response["files"]["source"] = base_url + drawio_file
    
    # Add iteration info
    response["iterations"] = result.get("iteration_count", 0)
    response["review_feedback"] = result.get("review_feedback", "")
    
    return response

@app.get("/download/{file_path:path}")
async def download_file(file_path: str):
    """Download any output file by relative path"""
    # Security: only allow downloads from output and logs folders
    if not (file_path.startswith("output/") or file_path.startswith("logs/")):
        return {"error": "Invalid file path"}
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    # Determine media type based on extension
    if file_path.endswith(".png"):
        media_type = "image/png"
    elif file_path.endswith(".html"):
        media_type = "text/html"
    elif file_path.endswith(".mmd"):
        media_type = "text/plain"
    elif file_path.endswith(".drawio"):
        media_type = "application/xml"
    elif file_path.endswith(".txt"):
        media_type = "text/plain"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(file_path, media_type=media_type, filename=os.path.basename(file_path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)