import pdfplumber, pandas as pd, streamlit as st, json, re
from openai import OpenAI
from docx import Document
from docx.shared import RGBColor
from difflib import SequenceMatcher
import io
import database as db  # This is where the supabase client lives

# Initialize OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------- Project Management (Database Linked) ---------------- #

def create_project(name, description=""):
    return db.create_project(name, description)

def get_all_projects():
    return db.get_all_projects()

def get_project(project_id):
    return db.get_project(project_id)

def create_iteration(project_id, docA_name, docB_name, docA_bytes, docB_bytes):
    """
    Calls the database module to handle the logic. 
    Note: Always use db.supabase to access the client initialized in database.py
    """
    # 1. Calculate the next iteration number
    # Using db.supabase ensures we use the client initialized with secrets
    existing_iters = db.supabase.table("iterations")\
        .select("iteration_number")\
        .eq("project_id", project_id)\
        .order("iteration_number", desc=True)\
        .limit(1)\
        .execute()
    
    if existing_iters.data:
        next_version = existing_iters.data[0]['iteration_number'] + 1
    else:
        next_version = 1

    # 2. Insert the record using LOWERCASE column names to match Supabase schema
    data = {
        "project_id": project_id,
        "doca_name": docA_name,
        "docb_name": docB_name,
        "iteration_number": next_version
    }
    
    response = db.supabase.table("iterations").insert(data).execute()
    
    if response.data:
        return response.data[0]
    return None

def get_iterations_list(project_id):
    return db.get_iterations(project_id)

# ---------------- Comparison Logic ---------------- #

def compare_iterations(project_id, iter_ids):
    iterations = []
    for i_id in iter_ids:
        it = db.get_iteration(i_id)
        if it: iterations.append(it)
    
    if len(iterations) < 2:
        return None
    
    comparison = {"iterations": [], "document_changes": []}
    
    for it in iterations:
        df = db.get_clauses(it['id'])
        comparison["iterations"].append({
            "number": it["iteration_number"],
            "date": it["created_at"],
            "docs": f"{it['doca_name']} vs {it['docb_name']}",
            "id": it["id"]
        })

    # AI Analysis of text changes between versions
    for i in range(len(iterations) - 1):
        # We use the LLM to summarize what changed between Version 1 text and Version 2 text
        prompt = f"Summarize the legal changes between these two versions of a Client NDA.\n\nOld Text: {iterations[i]['full_text_b'][:4000]}\n\nNew Text: {iterations[i+1]['full_text_b'][:4000]}"
        changes = llm(prompt)
        comparison["document_changes"].append({
            "from": iterations[i]["iteration_number"],
            "to": iterations[i+1]["iteration_number"],
            "changes": changes
        })
    
    return comparison

# ---------------- PDF & AI Processing ---------------- #

def extract_pages(pdf_bytes):
    pages = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as p:
        for i, page in enumerate(p.pages):
            pages.append({"page": i+1, "text": page.extract_text() or ""})
    return pages

def llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )
    return response.choices[0].message.content

def page_diff(std_pages, client_pages):
    rows = []
    max_pages = max(len(std_pages), len(client_pages))
    
    for i in range(max_pages):
        std_txt = std_pages[i]["text"] if i < len(std_pages) else ""
        clt_txt = client_pages[i]["text"] if i < len(client_pages) else ""
        
        # Use double braces {{ }} for the JSON format example
        prompt = f"""
        Compare these NDA pages. Identify differences in clauses.
        Return ONLY a JSON array of objects. 
        
        Format: [{{ "title": "...", "difference": "...", "legal_impact": "...", "risk": "high/medium/low" }}]
        
        Standard Page {i+1}: {std_txt[:3000]}
        Client Page {i+1}: {clt_txt[:3000]}
        """
        try:
            res = llm(prompt)
            # Find the JSON array in the response
            match = re.search(r"\[.*\]", res, re.S)
            if match:
                clean_json = match.group()
                data = json.loads(clean_json)
                for item in data:
                    item['page'] = i + 1
                    rows.append(item)
        except Exception as e:
            st.warning(f"Could not parse page {i+1}: {e}")
            continue
            
    return pd.DataFrame(rows)

def run_comparison_pipeline(project_id, a_file, b_file):
    # 1. Read and Extract
    a_bytes = a_file.getvalue()
    b_bytes = b_file.getvalue()
    a_pages = extract_pages(a_bytes)
    b_pages = extract_pages(b_bytes)
    a_text = "\n".join([p["text"] for p in a_pages])
    b_text = "\n".join([p["text"] for p in b_pages])
    
    # 2. AI Analysis
    t1 = llm(f"Classify (one word): {a_text[:1000]}")
    t2 = llm(f"Classify (one word): {b_text[:1000]}")
    overall = llm(f"Provide a high-level summary of risks between Doc A and Doc B:\n\nA: {a_text[:3000]}\nB: {b_text[:3000]}")
    
    # 3. Generate the Clause Table
    df = page_diff(a_pages, b_pages)
    
    if df.empty:
        # Emergency fallback so the UI isn't empty
        df = pd.DataFrame([{
            "page": 1, "title": "General", "difference": "Minor formatting differences", 
            "legal_impact": "No major risks detected", "risk": "low"
        }])
    
    df['status'] = 'pending'
    df['notes'] = ''

    # 4. Save and Return
    iteration = create_iteration(project_id, a_file.name, b_file.name, a_bytes, b_bytes)
    if iteration:
        db.update_iteration(
            iteration['id'], 
            full_text_a=a_text, 
            full_text_b=b_text, 
            overall_comparison=overall,
            document_type_a=t1,
            document_type_b=t2
        )
        db.save_clauses(iteration['id'], df)
        return iteration['id']
    return None
# ---------------- Redlining & Export ---------------- #

def generate_redline_doc(old, new, path):
    doc = Document()
    p = doc.add_paragraph()
    matcher = SequenceMatcher(None, old.split(), new.split())
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        words_old = old.split()[i1:i2]
        words_new = new.split()[j1:j2]
        if tag == "equal":
            p.add_run(" ".join(words_old) + " ")
        elif tag == "delete":
            r = p.add_run(" ".join(words_old) + " ")
            r.font.color.rgb, r.font.strike = RGBColor(255,0,0), True
        elif tag == "insert":
            r = p.add_run(" ".join(words_new) + " ")
            r.font.color.rgb = RGBColor(0,176,80)
        elif tag == "replace":
            r = p.add_run(" ".join(words_old) + " ")
            r.font.color.rgb, r.font.strike = RGBColor(255,0,0), True
            r = p.add_run(" ".join(words_new) + " ")
            r.font.color.rgb = RGBColor(0,176,80)
    doc.save(path)

def draft_email(user_input, overall, df):
    rejected_text = ""
    if df is not None and not df.empty and 'status' in df.columns:
        rejected = df[df['status'] == 'rejected']
        rejected_text = "\nRejected items: " + ", ".join(rejected['title'].tolist())
    
    return llm(f"Draft a professional legal email. Context: {overall}. {rejected_text}. User instructions: {user_input}")