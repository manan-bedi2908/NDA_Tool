from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import engine
import io
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectCreate(BaseModel):
    name: str
    description: str = ""

@app.get("/")
def read_root():
    return {"status": "ok", "service": "NDA Tool Backend"}

@app.get("/projects")
def get_projects():
    # Helper to serialize projects (convert DataFrames to dicts/lists if needed for listing?)
    # get_all_projects returns huge dict.
    projects = engine.get_all_projects()
    # We might want to clear out heavy data like 'docA_bytes' or 'data' for the list view
    # But for a simple prototype, returning everything is fine if not too big.
    # However, 'docA_bytes' are binary. JSON serialization will fail.
    
    # We must sanitize the output
    sanitized_projects = {}
    for pid, proj in projects.items():
        proj_copy = proj.copy()
        proj_copy['iterations'] = []
        for it in proj['iterations']:
            it_copy = it.copy()
            if 'docA_bytes' in it_copy: del it_copy['docA_bytes']
            if 'docB_bytes' in it_copy: del it_copy['docB_bytes']
            
            # Calculate stats if data exists
            stats = {"accepted": 0, "rejected": 0, "pending": 0}
            if 'data' in it_copy and it_copy['data']:
                try:
                    df = it_copy['data'].get("df")
                    if isinstance(df, pd.DataFrame) and not df.empty and 'status' in df.columns:
                        stats["accepted"] = len(df[df['status'] == 'accepted'])
                        stats["rejected"] = len(df[df['status'] == 'rejected'])
                        stats["pending"] = len(df[df['status'] == 'pending'])
                except Exception as e:
                    print(f"Error calculating stats for {it_copy.get('id')}: {e}")

                # The data contains DataFrame which is not JSON serializable directly
                # We can skip sending full analysis data in the list view
                it_copy['data'] = "Available" 
            
            it_copy['stats'] = stats
            proj_copy['iterations'].append(it_copy)
        sanitized_projects[pid] = proj_copy
    return sanitized_projects

@app.post("/projects")
def create_project(project: ProjectCreate):
    project_id = engine.create_project(project.name, project.description)
    return {"id": project_id, "name": project.name, "message": "Project created"}

@app.post("/create_iteration")
async def create_iteration(
    project_id: str = Form(...),
    fileA: UploadFile = File(...),
    fileB: UploadFile = File(...)
):
    try:
        # Read files
        docA_bytes = await fileA.read()
        docB_bytes = await fileB.read()
        
        # Create iteration
        iteration_id = engine.create_iteration(
            project_id, 
            fileA.filename, 
            fileB.filename, 
            docA_bytes, 
            docB_bytes
        )
        
        # Analyze
        pdfA = io.BytesIO(docA_bytes)
        pdfB = io.BytesIO(docB_bytes)
        
        t1, t2, overall, df, txtA, txtB = engine.compare_documents(pdfA, pdfB)
        
        # Store data in state (keep DataFrame for engine usage)
        data_for_state = {
            "t1": t1,
            "t2": t2,
            "overall": overall,
            "df": df,
            "A": txtA,
            "B": txtB
        }
        engine.update_iteration_data(project_id, iteration_id, data_for_state)
        
        # Prepare response (serialize DataFrame)
        data_response = {
            "t1": t1,
            "t2": t2,
            "overall": overall,
            "df": df.to_dict('records') if not df.empty else [],
            "A": txtA,
            "B": txtB
        }
        
        return {
            "message": "Iteration created and analyzed",
            "iteration_id": iteration_id,
            "analysis": data_response
        }
    except Exception as e:
        print(f"Error processing iteration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{project_id}/analyze")
def analyze_project(project_id: str):
    try:
        summary = engine.generate_project_analysis(project_id)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class EmailDraftRequest(BaseModel):
    user_input: str = ""

@app.post("/projects/{project_id}/draft_email")
def draft_email(project_id: str, request: EmailDraftRequest):
    try:
        email = engine.draft_project_email(project_id, request.user_input)
        return {"email": email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/iteration/latest")
def get_latest_iteration(project_id: str):
    try:
        details = engine.get_latest_iteration_details(project_id)
        if not details:
            return {"clauses": []} # Return empty if no data yet
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/iteration/{iteration_id}")
def get_iteration(project_id: str, iteration_id: str):
    try:
        details = engine.get_iteration_details(project_id, iteration_id)
        if not details:
             # Try to see if it's just missing data
             return {"clauses": [], "overall": "Data not found"}
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ClauseUpdateRequest(BaseModel):
    index: int
    status: str
    notes: str

@app.post("/projects/{project_id}/iteration/clause/update")
def update_clause(project_id: str, request: ClauseUpdateRequest):
    try:
        success = engine.update_latest_iteration_clause(project_id, request.index, request.status, request.notes)
        if not success:
             raise HTTPException(status_code=404, detail="Clause or project not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CompareRequest(BaseModel):
    iteration_ids: list[str]

@app.post("/projects/{project_id}/compare")
def compare_iterations(project_id: str, request: CompareRequest):
    try:
        comparison = engine.compare_iterations(project_id, request.iteration_ids)
        if not comparison:
            raise HTTPException(status_code=400, detail="Could not compare iterations. Ensure at least 2 are selected.")
        return comparison
    except Exception as e:
        print(f"Error comparing iterations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- File Download Endpoints ----------------- #
from fastapi.responses import FileResponse, StreamingResponse
import tempfile
import zipfile
import os

@app.get("/projects/{project_id}/redline")
def get_redline(project_id: str):
    try:
        project = engine.get_project(project_id)
        if not project or not project["iterations"]:
            raise HTTPException(status_code=404, detail="Project or iteration not found")
        
        iteration = project["iterations"][-1]
        data = iteration.get("data")
        if not data or "A" not in data or "B" not in data:
            raise HTTPException(status_code=404, detail="Analysis data not found")
            
        txtA = data["A"]
        txtB = data["B"]
        
        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp_path = tmp.name
            
        engine.generate_redline_doc(txtA, txtB, tmp_path)
        
        return FileResponse(
            path=tmp_path, 
            filename=f"Redline_v{iteration['iteration_number']}.docx",
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}/download_pdfs")
def download_pdfs(project_id: str):
    try:
        project = engine.get_project(project_id)
        if not project or not project["iterations"]:
            raise HTTPException(status_code=404, detail="Project or iteration not found")
        
        iteration = project["iterations"][-1]
        
        # In-memory zip
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            # Doc A
            if "docA_bytes" in iteration:
                zip_file.writestr(iteration.get("docA_name", "Document_A.pdf"), iteration["docA_bytes"])
            # Doc B
            if "docB_bytes" in iteration:
                zip_file.writestr(iteration.get("docB_name", "Document_B.pdf"), iteration["docB_bytes"])
                
        zip_buffer.seek(0)
        
        return StreamingResponse(
            zip_buffer, 
            media_type="application/zip", 
            headers={"Content-Disposition": f"attachment; filename=project_files_v{iteration['iteration_number']}.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
