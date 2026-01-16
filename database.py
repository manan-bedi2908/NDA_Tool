import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import datetime
import uuid

# Initialize Supabase client
@st.cache_resource
def get_supabase() -> Client:
    """Get Supabase client (cached)"""
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ============================================
# AUTHENTICATION FUNCTIONS
# ============================================

def sign_up(email: str, password: str, full_name: str = "", company_name: str = ""):
    """Create new user account"""
    try:
        # Sign up with Supabase Auth
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Create profile
            supabase.table('profiles').insert({
                'id': response.user.id,
                'email': email,
                'full_name': full_name,
                'company_name': company_name
            }).execute()
            
            return True, "Account created! Please check your email to verify."
        return False, "Sign up failed"
    except Exception as e:
        return False, str(e)

def sign_in(email: str, password: str):
    """Sign in existing user"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if response.user:
            # Store session in Streamlit
            st.session_state['user'] = response.user
            st.session_state['session'] = response.session
            return True, "Logged in successfully!"
        return False, "Login failed"
    except Exception as e:
        return False, str(e)

def sign_out():
    """Sign out current user"""
    try:
        supabase.auth.sign_out()
        st.session_state.clear()
        return True
    except:
        return False

def get_current_user():
    """Get current logged-in user"""
    return st.session_state.get('user')

def is_authenticated():
    """Check if user is logged in"""
    return 'user' in st.session_state

# ============================================
# PROJECT FUNCTIONS
# ============================================

def create_project(name: str, description: str = ""):
    """Create a new project"""
    user = get_current_user()
    if not user:
        return None
    
    try:
        response = supabase.table('projects').insert({
            'name': name,
            'description': description,
            'created_by': user.id,
            'status': 'new'
        }).execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error creating project: {e}")
        return None

def get_all_projects():
    """Get all projects for current user"""
    user = get_current_user()
    if not user:
        return []
    
    try:
        response = supabase.table('projects')\
            .select('*')\
            .eq('created_by', user.id)\
            .order('created_at', desc=True)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching projects: {e}")
        return []

def get_project(project_id: str):
    """Get single project by ID"""
    try:
        response = supabase.table('projects')\
            .select('*')\
            .eq('id', project_id)\
            .single()\
            .execute()
        
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error fetching project: {e}")
        return None

def update_project(project_id: str, **kwargs):
    """Update project fields"""
    try:
        response = supabase.table('projects')\
            .update(kwargs)\
            .eq('id', project_id)\
            .execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error updating project: {e}")
        return None

def delete_project(project_id: str):
    """Delete a project (cascades to iterations and clauses)"""
    try:
        supabase.table('projects').delete().eq('id', project_id).execute()
        return True
    except Exception as e:
        st.error(f"Error deleting project: {e}")
        return False

# ============================================
# ITERATION FUNCTIONS
# ============================================

def create_iteration(project_id: str, docA_name: str, docB_name: str, 
                    docA_bytes: bytes, docB_bytes: bytes):
    """Create a new iteration"""
    user = get_current_user()
    if not user:
        return None
    
    try:
        # Get current iteration count for this project
        existing = supabase.table('iterations')\
            .select('iteration_number')\
            .eq('project_id', project_id)\
            .execute()
        
        iteration_num = len(existing.data) + 1 if existing.data else 1
        
        # Upload PDFs to storage
        user_folder = str(user.id)
        iteration_folder = f"{user_folder}/project_{project_id}/iteration_{iteration_num}"
        
        docA_path = f"{iteration_folder}/{docA_name}"
        docB_path = f"{iteration_folder}/{docB_name}"
        
        # Upload files
        supabase.storage.from_('documents').upload(docA_path, docA_bytes)
        supabase.storage.from_('documents').upload(docB_path, docB_bytes)
        
        # Create iteration record
        response = supabase.table('iterations').insert({
            'project_id': project_id,
            'iteration_number': iteration_num,
            'docA_name': docA_name,
            'docB_name': docB_name,
            'docA_path': docA_path,
            'docB_path': docB_path
        }).execute()
        
        iteration = response.data[0] if response.data else None
        
        # Update project's current_iteration
        if iteration:
            update_project(project_id, current_iteration_id=iteration['id'])
        
        return iteration
    except Exception as e:
        st.error(f"Error creating iteration: {e}")
        return None

def get_iterations(project_id: str):
    """Get all iterations for a project"""
    try:
        response = supabase.table('iterations')\
            .select('*')\
            .eq('project_id', project_id)\
            .order('iteration_number', desc=False)\
            .execute()
        
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error fetching iterations: {e}")
        return []

def get_iteration(iteration_id: str):
    """Get single iteration"""
    try:
        response = supabase.table('iterations')\
            .select('*')\
            .eq('id', iteration_id)\
            .single()\
            .execute()
        
        return response.data if response.data else None
    except Exception as e:
        st.error(f"Error fetching iteration: {e}")
        return None

def update_iteration(iteration_id: str, **kwargs):
    """Update iteration fields"""
    try:
        response = supabase.table('iterations')\
            .update(kwargs)\
            .eq('id', iteration_id)\
            .execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error updating iteration: {e}")
        return None

def download_pdf(file_path: str):
    """Download PDF from storage"""
    try:
        response = supabase.storage.from_('documents').download(file_path)
        return response
    except Exception as e:
        st.error(f"Error downloading PDF: {e}")
        return None

# ============================================
# CLAUSE FUNCTIONS
# ============================================

def save_clauses(iteration_id: str, clauses_df: pd.DataFrame):
    """Save all clauses for an iteration"""
    try:
        # Delete existing clauses
        supabase.table('clauses').delete().eq('iteration_id', iteration_id).execute()
        
        # Insert new clauses
        clauses_data = []
        for _, row in clauses_df.iterrows():
            clauses_data.append({
                'iteration_id': iteration_id,
                'page': int(row['page']) if pd.notna(row['page']) else None,
                'title': str(row['title']),
                'difference': str(row['difference']),
                'legal_impact': str(row['legal_impact']),
                'risk_level': str(row['risk']),
                'status': str(row['status']),
                'notes': str(row['notes']) if pd.notna(row['notes']) else ''
            })
        
        if clauses_data:
            supabase.table('clauses').insert(clauses_data).execute()
        
        return True
    except Exception as e:
        st.error(f"Error saving clauses: {e}")
        return False

def get_clauses(iteration_id):
    import pandas as pd
    # We MUST include 'id' here to identify the row during the save process
    columns = "id, page, title, difference, legal_impact, risk_level, status, notes"
    res = supabase.table("clauses").select(columns).eq("iteration_id", iteration_id).execute()
    return pd.DataFrame(res.data)

def update_clause(clause_id: str, **kwargs):
    """Update a single clause"""
    try:
        response = supabase.table('clauses')\
            .update(kwargs)\
            .eq('id', clause_id)\
            .execute()
        
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error updating clause: {e}")
        return None