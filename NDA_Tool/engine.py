import pdfplumber, pandas as pd, json, re, os
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

from openai import OpenAI
from docx import Document
from docx.shared import RGBColor
from difflib import SequenceMatcher
from datetime import datetime
import io

# State Management for Hybrid (Streamlit/API) usage
class StateManager:
    def __init__(self):
        self._local_state = {}

    def __getitem__(self, key):
        if HAS_STREAMLIT and hasattr(st, "session_state"):
             return st.session_state[key]
        return self._local_state[key]

    def __setitem__(self, key, value):
        if HAS_STREAMLIT and hasattr(st, "session_state"):
            st.session_state[key] = value
        else:
            self._local_state[key] = value
            
    def get(self, key, default=None):
        if HAS_STREAMLIT and hasattr(st, "session_state"):
            return st.session_state.get(key, default)
        return self._local_state.get(key, default)

    def __contains__(self, key):
        if HAS_STREAMLIT and hasattr(st, "session_state"):
            return key in st.session_state
        return key in self._local_state

    def __delitem__(self, key):
        if HAS_STREAMLIT and hasattr(st, "session_state"):
            del st.session_state[key]
        else:
            del self._local_state[key]

state = StateManager()

def get_openai_key():
    if HAS_STREAMLIT and hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=get_openai_key())

# ---------------- Project Management ---------------- #
def init_projects():
    if "projects" not in state:
        state["projects"] = {}
    if "current_project" not in state:
        state["current_project"] = None

def create_project(name, description=""):
    init_projects()
    project_id = f"proj_{len(state['projects']) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    state["projects"][project_id] = {
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
    return state["projects"]

def get_project(project_id):
    init_projects()
    return state["projects"].get(project_id)

def create_iteration(project_id, docA_name, docB_name, docA_bytes, docB_bytes):
    """Create a new iteration within a project"""
    init_projects()
    if project_id in state["projects"]:
        project = state["projects"][project_id]
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
    if project_id in state["projects"]:
        state["projects"][project_id]["current_iteration"] = iteration_id

def update_iteration_data(project_id, iteration_id, data):
    """Update analysis data for an iteration"""
    init_projects()
    if project_id in state["projects"]:
        project = state["projects"][project_id]
        for iteration in project["iterations"]:
            if iteration["id"] == iteration_id:
                iteration["data"] = data
                break

def delete_project(project_id):
    init_projects()
    if project_id in state["projects"]:
        del state["projects"][project_id]
        if state["current_project"] == project_id:
            state["current_project"] = None

def set_current_project(project_id):
    state["current_project"] = project_id

def get_current_project():
    return state.get("current_project")

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
            text1 = iter1["data"]["B"]  # Client NDA from iteration 1
            text2 = iter2["data"]["B"]  # Client NDA from iteration 2
            
            # Ask AI to explain what changed
            changes = llm(f"""
Compare these two versions of a client NDA and explain what changed.
Focus ONLY on content changes made by the client.

VERSION {iter1['iteration_number']} (Client NDA):
{text1}

VERSION {iter2['iteration_number']} (Client NDA):
{text2}

List the key differences clearly:
1. New clauses added
2. Clauses removed
3. Significant modifications to existing clauses
4. Changes in terms, dates, amounts, or obligations

Format the response as clear bullet points.
Be specific and lawyer-friendly.
""")
            
            comparison["document_changes"].append({
                "from": iter1["iteration_number"],
                "to": iter2["iteration_number"],
                "changes": changes
            })
    
    return comparison

def generate_project_analysis(project_id):
    """Generates an executive summary comparing the latest iteration's documents"""
    project = get_project(project_id)
    if not project or not project["iterations"]:
        return "Not enough data to analyze."
    
    # Get the latest iteration
    latest_iteration = project["iterations"][-1]
    
    if not latest_iteration.get("data"):
         return "No analysis data available for the latest iteration."

    # Extract text from the latest iteration
    # Assuming 'A' and 'B' keys store the full text in the data dict
    text_a = latest_iteration["data"].get("A", "")
    text_b = latest_iteration["data"].get("B", "")

    if not text_a or not text_b:
        return "Document text not found in the latest iteration."

    # Construct the prompt based on the user's specific request
    prompt = f"""
You are a legal document analysis assistant.

Task:
Compare two documents referred to as Document A and Document B.

Context:
Both documents are Mutual Non-Disclosure Agreements (NDAs).

Document A Content:
{text_a[:15000]}

Document B Content:
{text_b[:15000]}

Instructions:
- Begin with a brief opening sentence stating that both documents are NDAs and broadly similar in structure and purpose.
- Then provide a clear, section-wise comparison highlighting key differences and similarities.
- Use short headings for each comparison aspect.
- Maintain a neutral, professional, explanatory tone.
- Do NOT speculate beyond the provided text.
- Do NOT rewrite clauses.
- Focus on factual comparison only.

Comparison Sections to Include (in this order):

1. Disclosing Party Name  
   - Clearly state the disclosing party named in Document A.
   - Clearly state the disclosing party named in Document B.

2. Content Consistency  
   - Explain whether the core clauses and obligations are largely the same.
   - Mention examples such as definitions, confidentiality obligations, term, exclusions, non-solicitation, and return of information.

3. Formatting and Structure  
   - Compare layout, numbering, and structure.
   - Explicitly note if one document appears incomplete or truncated.

4. Legal and Regulatory References  
   - State whether both documents include similar legal or regulatory clauses.
   - Mention that wording may vary slightly due to party context, if applicable.

5. Overall Purpose  
   - Explain that both documents serve the same legal purpose of establishing confidentiality.
   - Note differences only in parties or identifiers, not intent.

6. Date of Agreement  
   - State the date(s) mentioned in both documents and whether they match.

Ending Requirement:
- Conclude with a short summary paragraph clearly stating:
  - the primary difference between the documents
  - whether one document appears incomplete
  - that the remaining content is largely consistent

Formatting Rules:
- Use bullet points
- Clear headings (H2/H3 in markdown)
- No emojis
- No conversational language
"""
    return llm(prompt)

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
Compare these two NDA pages and generate a structured review of ALL clauses.

STANDARD NDA – Page {i+1}
{std}

CLIENT NDA – Page {i+1}
{client_txt}

Instructions:
- Identify EVERY clause present in the text (e.g. Confidentiality, Term, Governing Law, etc.).
- Compare the content of each clause between Standard and Client versions.
- Include **all clauses**, even if identical.
- Focus only on **content differences**, not formatting.
- If identical, set "difference" to "Identical".
- Keep entries clear and concise; one clause per entry.
- Return valid **JSON array** only; no extra text or explanations.

Field Requirements:
- page: {i+1}
- title: Short clause name
- difference: Description of the difference (or 'Identical')
- legal_impact: Explanation of legal implications (or 'None' if identical)
- risk: low | medium | high (based on potential legal/financial impact)
- status: "pending" (always set this value)
- notes: "" (always set empty string)

Format:
[
  {{
    "page": {i+1},
    "title": "Clause Title",
    "difference": "Description...",
    "legal_impact": "Impact...",
    "risk": "medium",
    "status": "pending",
    "notes": ""
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
    # Ensure columns exist even if LLM missed them or rows is empty
    if not df.empty:
        if 'status' not in df.columns: df['status'] = 'pending'
        if 'notes' not in df.columns: df['notes'] = ''
        if 'risk' not in df.columns: df['risk'] = 'low'
        
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

def draft_project_email(project_id, user_input):
    """Drafts an email for the project's latest iteration"""
    project = get_project(project_id)
    if not project or not project["iterations"]:
        return "No project data found."
    
    iteration = project["iterations"][-1]
    if not iteration.get("data"):
        return "No analysis data found for the latest iteration."
        
    data = iteration["data"]
    overall = data.get("overall", "")
    df = data.get("df")
    
    return draft_email(user_input, overall, df)

def get_latest_iteration_details(project_id):
    """Returns the clause dataframe and text for the latest iteration"""
    project = get_project(project_id)
    if not project or not project["iterations"]:
        return None
    
    iteration = project["iterations"][-1]
    if not iteration.get("data"):
        return None
        
    data = iteration["data"]
    df = data.get("df")
    
    result = {
        "iteration_id": iteration.get("id"),
        "created_at": iteration.get("created_at"),
        "clauses": df.to_dict('records') if isinstance(df, pd.DataFrame) and not df.empty else [],
        "overall": data.get("overall", ""),
        "docA_name": iteration.get("docA_name", "Document A"), # Ensure these form part of iteration data if stored
        "docB_name": iteration.get("docB_name", "Document B")
    }
    return result

def get_iteration_details(project_id, iteration_id):
    """Returns the clause dataframe and text for a specific iteration"""
    iteration = get_iteration_by_id(project_id, iteration_id)
    if not iteration or not iteration.get("data"):
        return None
        
    data = iteration["data"]
    df = data.get("df")
    
    # Check if df is a DataFrame
    clauses = []
    if isinstance(df, pd.DataFrame) and not df.empty:
         clauses = df.to_dict('records')
    elif isinstance(df, list):
         clauses = df
    
    result = {
        "iteration_id": iteration.get("id"),
        "iteration_number": iteration.get("iteration_number"),
        "created_at": iteration.get("created_at"),
        "clauses": clauses,
        "overall": data.get("overall", ""),
        "docA_name": iteration.get("docA_name", "Document A"),
        "docB_name": iteration.get("docB_name", "Document B")
    }
    return result

def update_latest_iteration_clause(project_id, clause_index, status, notes):
    """Updates status and notes for a specific clause in the latest iteration"""
    project = get_project(project_id)
    if not project or not project["iterations"]:
        return False
    
    iteration = project["iterations"][-1]
    if not iteration.get("data") or "df" not in iteration["data"]:
        return False
        
    df = iteration["data"]["df"]
    
    if 0 <= clause_index < len(df):
        # Update the specific row
        df.at[clause_index, 'status'] = status
        df.at[clause_index, 'notes'] = notes
        
        # Save back to persistence (in-memory or file)
        # Since 'df' is a reference to the dict object in memory (if get_project returns ref)
        # But we need to make sure. engine.projects is global. 
        # get_project returns engine.projects.get(project_id) which is a reference.
        # So modifying df here modifies the global state.
        
        return True
    return False

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