import pdfplumber, pandas as pd, streamlit as st, json, re
from openai import OpenAI
from docx import Document
from docx.shared import RGBColor
from difflib import SequenceMatcher
from datetime import datetime
import io

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- Project Management ---------------- #
def init_projects():
    if "projects" not in st.session_state:
        st.session_state["projects"] = {}
    if "current_project" not in st.session_state:
        st.session_state["current_project"] = None

def create_project(name, description=""):
    init_projects()
    project_id = f"proj_{len(st.session_state['projects']) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    st.session_state["projects"][project_id] = {
        "id": project_id,
        "name": name,
        "description": description,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "iterations": [],  # List of iterations
        "current_iteration": None,
        "status": "new"
    }
    return project_id

def get_all_projects():
    init_projects()
    return st.session_state["projects"]

def get_project(project_id):
    init_projects()
    return st.session_state["projects"].get(project_id)

def create_iteration(project_id, docA_name, docB_name, docA_bytes, docB_bytes):
    """Create a new iteration within a project"""
    init_projects()
    if project_id in st.session_state["projects"]:
        project = st.session_state["projects"][project_id]
        iteration_num = len(project["iterations"]) + 1
        iteration_id = f"iter_{iteration_num}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        iteration = {
            "id": iteration_id,
            "iteration_number": iteration_num,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "docA_name": docA_name,
            "docB_name": docB_name,
            "docA_bytes": docA_bytes,
            "docB_bytes": docB_bytes,
            "data": None,
        }
        
        project["iterations"].append(iteration)
        project["current_iteration"] = iteration_id
        project["status"] = "active"
        
        return iteration_id

def get_current_iteration(project_id):
    """Get the current iteration for a project"""
    project = get_project(project_id)
    if project and project["current_iteration"]:
        for iteration in project["iterations"]:
            if iteration["id"] == project["current_iteration"]:
                return iteration
    return None

def get_iteration_by_id(project_id, iteration_id):
    """Get a specific iteration by ID"""
    project = get_project(project_id)
    if project:
        for iteration in project["iterations"]:
            if iteration["id"] == iteration_id:
                return iteration
    return None

def set_current_iteration(project_id, iteration_id):
    """Set the current iteration for a project"""
    init_projects()
    if project_id in st.session_state["projects"]:
        st.session_state["projects"][project_id]["current_iteration"] = iteration_id

def update_iteration_data(project_id, iteration_id, data):
    """Update analysis data for an iteration"""
    init_projects()
    if project_id in st.session_state["projects"]:
        project = st.session_state["projects"][project_id]
        for iteration in project["iterations"]:
            if iteration["id"] == iteration_id:
                iteration["data"] = data
                break

def delete_project(project_id):
    init_projects()
    if project_id in st.session_state["projects"]:
        del st.session_state["projects"][project_id]
        if st.session_state["current_project"] == project_id:
            st.session_state["current_project"] = None

def set_current_project(project_id):
    st.session_state["current_project"] = project_id

def get_current_project():
    return st.session_state.get("current_project")

def compare_iterations(project_id, iter_ids):
    """Compare multiple iterations to show what changed in documents"""
    project = get_project(project_id)
    iterations = []
    
    for iter_id in iter_ids:
        iteration = get_iteration_by_id(project_id, iter_id)
        if iteration:
            iterations.append(iteration)
    
    if len(iterations) < 2:
        return None
    
    comparison = {
        "iterations": []
    }
    
    # Get basic info for each iteration
    for iteration in iterations:
        iter_info = {
            "number": iteration["iteration_number"],
            "date": iteration["created_at"],
            "docs": f"{iteration['docA_name']} vs {iteration['docB_name']}",
            "id": iteration["id"]
        }
        
        if iteration["data"]:
            df = iteration["data"]["df"]
            if not df.empty and 'status' in df.columns:
                iter_info["stats"] = {
                    "total": len(df),
                    "accepted": len(df[df['status'] == 'accepted']),
                    "rejected": len(df[df['status'] == 'rejected']),
                    "pending": len(df[df['status'] == 'pending'])
                }
        
        comparison["iterations"].append(iter_info)
    
    # Generate AI comparison of document changes
    comparison["document_changes"] = []
    
    for i in range(len(iterations) - 1):
        iter1 = iterations[i]
        iter2 = iterations[i + 1]
        
        if iter1["data"] and iter2["data"]:
            # Get the full text from both iterations
            text1 = iter1["data"]["B"][:5000]  # Client NDA from iteration 1
            text2 = iter2["data"]["B"][:5000]  # Client NDA from iteration 2
            
            # Ask AI to explain what changed
            changes = llm(f"""
Compare these two versions of a client NDA and explain what changed.
Focus on CONTENT changes made by the client, not status changes.

VERSION {iter1['iteration_number']} (Client NDA):
{text1}

VERSION {iter2['iteration_number']} (Client NDA):
{text2}

List the key differences in a clear, concise way. Focus on:
1. New clauses added
2. Clauses removed
3. Significant modifications to existing clauses
4. Changes in terms, dates, amounts, or conditions

Format as bullet points. Be specific about what changed.
""")
            
            comparison["document_changes"].append({
                "from": iter1["iteration_number"],
                "to": iter2["iteration_number"],
                "changes": changes
            })
    
    return comparison

# ---------------- PDF ---------------- #
def extract_pages(pdf):
    pages = []
    with pdfplumber.open(pdf) as p:
        for i, page in enumerate(p.pages):
            pages.append({"page": i+1, "text": page.extract_text() or ""})
    return pages

def full_text(pages):
    return "\n".join([p["text"] for p in pages])

# ---------------- LLM ---------------- #
def llm(prompt):
    # Using gpt-4o-mini - the cheapest model for testing
    return client.chat.completions.create(
        model="gpt-4o-mini",  # Cheapest model: ~$0.15 per 1M input tokens
        messages=[{"role":"user","content":prompt}],
        temperature=0
    ).choices[0].message.content

# ---------------- Classification ---------------- #
def classify(text):
    return llm(f"""
Classify this document as:
NDA, Resume, Invoice, Contract, Legal Agreement, Other.
Text:
{text[:6000]}
Return one word.
""").strip()

# ---------------- Overall diff ---------------- #
def overall_diff(a, b):
    return llm(f"""
Compare these two documents and explain their differences.
Document A:
{a[:8000]}
Document B:
{b[:8000]}
""")

# ---------------- Page-level NDA diff ---------------- #
def page_diff(std_pages, client_pages):
    rows = []
    max_pages = max(len(std_pages), len(client_pages))
    for i in range(max_pages):
        std = std_pages[i]["text"] if i < len(std_pages) else ""
        client_txt = client_pages[i]["text"] if i < len(client_pages) else ""
        prompt = f"""
You are a senior contract lawyer.
Compare these two NDA pages.
STANDARD NDA – Page {i+1}
{std}
CLIENT NDA – Page {i+1}
{client_txt}
You MUST list all legal differences.
Return VALID JSON only.
Each field must be a SINGLE LINE of text.
Do NOT use newlines, bullet points, or lists.
Format:
[
  {{
    "page": {i+1},
    "title": "short clause name",
    "difference": "one sentence describing what is different",
    "legal_impact": "one sentence explaining the legal meaning of that difference",
    "risk": "low | medium | high"
  }}
]
"""
        try:
            res = llm(prompt)
            json_str = re.search(r"\[.*\]", res, re.S).group()
            rows.extend(json.loads(json_str))
        except:
            pass
    df = pd.DataFrame(rows)
    if not df.empty:
        df['status'] = 'pending'
        df['notes'] = ''
    return df

# ---------------- Redline Word ---------------- #
def generate_redline_doc(old, new, path):
    doc = Document()
    p = doc.add_paragraph()
    matcher = SequenceMatcher(None, old.split(), new.split())
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            p.add_run(" ".join(old.split()[i1:i2]) + " ")
        elif tag == "delete":
            r = p.add_run(" ".join(old.split()[i1:i2]) + " ")
            r.font.color.rgb = RGBColor(255,0,0)
            r.font.strike = True
        elif tag == "insert":
            r = p.add_run(" ".join(new.split()[j1:j2]) + " ")
            r.font.color.rgb = RGBColor(0,176,80)
        elif tag == "replace":
            r = p.add_run(" ".join(old.split()[i1:i2]) + " ")
            r.font.color.rgb = RGBColor(255,0,0)
            r.font.strike = True
            r = p.add_run(" ".join(new.split()[j1:j2]) + " ")
            r.font.color.rgb = RGBColor(0,176,80)
    doc.save(path)

# ---------------- Email drafting ---------------- #
def draft_email(user_input, overall, df=None):
    review_summary = ""
    if df is not None and not df.empty and 'status' in df.columns:
        accepted = df[df['status'] == 'accepted']
        rejected = df[df['status'] == 'rejected']
        
        if not accepted.empty:
            review_summary += "\n\nACCEPTED CLAUSES:\n"
            for _, row in accepted.iterrows():
                review_summary += f"- {row['title']}: {row['difference']}\n"
        
        if not rejected.empty:
            review_summary += "\n\nREJECTED CLAUSES:\n"
            for _, row in rejected.iterrows():
                review_summary += f"- {row['title']}: {row['difference']}\n"
                if row['notes']:
                    review_summary += f"  Reason: {row['notes']}\n"
    
    return llm(f"""
You are a senior legal counsel.
Differences:
{overall}
{review_summary}
User message:
{user_input}
Draft a professional email to the counterparty.
Sign as:
Artiaz
""")

# ---------------- Main pipeline ---------------- #
def compare_documents(a_pdf, b_pdf):
    a_pages = extract_pages(a_pdf)
    b_pages = extract_pages(b_pdf)
    a_text = full_text(a_pages)
    b_text = full_text(b_pages)
    t1 = classify(a_text)
    t2 = classify(b_text)
    overall = overall_diff(a_text, b_text)
    if t1 == "NDA" and t2 == "NDA":
        df = page_diff(a_pages, b_pages)
    else:
        df = pd.DataFrame([{
            "page":"N/A",
            "difference":f"{t1} vs {t2}",
            "legal_impact":"Not comparable",
            "risk":"high",
            "status":"pending",
            "notes":""
        }])
    return t1, t2, overall, df, a_text, b_text