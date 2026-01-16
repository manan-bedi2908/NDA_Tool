import streamlit as st

# 1. THIS MUST BE THE ABSOLUTE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Artiaz | NDA AI", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 2. NOW import your other libraries and local modules
import pandas as pd
import io
import database as db  # Handles Supabase connection and secrets
import engine         # Handles PDF processing and AI logic

# --- AUTHENTICATION CHECK (REVISED FOR PERSISTENCE) ---
def check_auth():
    """Ensures user stays logged in across refreshes"""
    # Initialize the session flag if it doesn't exist
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    # Check if the Supabase client already has an active session
    if not st.session_state["authenticated"]:
        if db.is_authenticated():
            st.session_state["authenticated"] = True
            return True
        
        # Show Login/Signup UI if no session is found
        st.title("⚖️ Artiaz Legal AI")
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            with st.form("login"):
                e = st.text_input("Email")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    success, msg = db.sign_in(e, p)
                    if success: 
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else: st.error(msg)
        
        with tab2:
            with st.form("signup"):
                new_e = st.text_input("Email")
                new_p = st.text_input("Password", type="password")
                name = st.text_input("Full Name")
                if st.form_submit_button("Sign Up"):
                    success, msg = db.sign_up(new_e, new_p, name)
                    if success: st.success("Account created! Please login.")
                    else: st.error(msg)
        return False
    return True

# --- MAIN APP ---
def main():
    if not check_auth(): return

    user = db.get_current_user()

    # --- SIDEBAR: PROJECT NAVIGATION ---
    with st.sidebar:
        st.title("📂 Artiaz Projects")
        st.write(f"User: **{user.email}**")
        
        if st.button("Logout"):
            db.sign_out()
            # Clear authentication and project state on logout
            st.session_state["authenticated"] = False
            if 'current_project_id' in st.session_state:
                del st.session_state['current_project_id']
            st.rerun()
        
        st.divider()
        
        # New Project Creation
        with st.expander("➕ New Project"):
            p_name = st.text_input("Project Name")
            p_desc = st.text_area("Description")
            if st.button("Create"):
                if p_name:
                    db.create_project(p_name, p_desc)
                    st.rerun()

        st.divider()

        # Project Selection and Deletion
        projects = db.get_all_projects()
        if not projects:
            st.info("No projects yet.")
        else:
            project_names = [p['name'] for p in projects]
            selected_name = st.selectbox("Select Project", project_names)
            curr_project = next(p for p in projects if p['name'] == selected_name)
            st.session_state['current_project_id'] = curr_project['id']

            # Project Settings (Delete Feature)
            with st.expander("🗑️ Project Settings"):
                st.warning(f"Delete project: {selected_name}?")
                confirm_delete = st.checkbox("Confirm permanent deletion of all versions.")
                if st.button("Delete Project", type="secondary", disabled=not confirm_delete):
                    db.delete_project(curr_project['id'])
                    # Clean up session state after deletion
                    if 'current_project_id' in st.session_state:
                        del st.session_state['current_project_id']
                    st.success("Project deleted.")
                    st.rerun()

    # --- MAIN CONTENT ---
    if 'current_project_id' in st.session_state:
        pid = st.session_state['current_project_id']
        project = db.get_project(pid)
        
        st.header(f"Project: {project['name']}")
        
        tab_new, tab_history, tab_compare = st.tabs(["🚀 New Analysis", "📜 Iteration History", "🔄 Version Comparison"])

        # TAB 1: NEW ANALYSIS
        with tab_new:
            st.subheader("Upload Documents")
            c1, c2 = st.columns(2)
            with c1: doc_a = st.file_uploader("Standard NDA (PDF)", type="pdf")
            with c2: doc_b = st.file_uploader("Client NDA (PDF)", type="pdf")
            
            if st.button("Analyze Documents", type="primary") and doc_a and doc_b:
                with st.spinner("AI is analyzing legal risks..."):
                    iter_id = engine.run_comparison_pipeline(pid, doc_a, doc_b)
                    if iter_id:
                        st.success("Analysis Complete!")
                        st.session_state['active_iter_id'] = iter_id
                        st.rerun()

        # TAB 2: HISTORY & REVIEW
        with tab_history:
            iterations = db.get_iterations(pid)
            if not iterations:
                st.info("No iterations yet.")
            else:
                it_options = {f"v{it['iteration_number']} - {it['created_at'][:16]}": it['id'] for it in iterations}
                
                # Default selection to the most recent analysis
                default_idx = 0
                if 'active_iter_id' in st.session_state:
                    for i, (label, it_id) in enumerate(it_options.items()):
                        if it_id == st.session_state['active_iter_id']:
                            default_idx = i

                selected_it_label = st.selectbox("Select Iteration to View", list(it_options.keys()), index=default_idx)
                active_it_id = it_options[selected_it_label]
                
                it_data = db.get_iteration(active_it_id)
                clauses_df = db.get_clauses(active_it_id)

                st.divider()
                st.subheader("Executive Summary")
                st.info(it_data['overall_comparison'])

                # --- INTERACTIVE CLAUSE TABLE ---
                st.subheader("Clause-by-Clause Review")
                if not clauses_df.empty:
                    # 'id' is hidden but kept in the dataframe to avoid KeyError on save
                    edited_df = st.data_editor(
                        clauses_df,
                        column_config={
                            "id": None, # Hides primary key from user
                            "status": st.column_config.SelectboxColumn(
                                "Status",
                                options=["pending", "accepted", "rejected"],
                                required=True,
                            ),
                            "notes": st.column_config.TextColumn("Legal Notes", width="large"),
                        },
                        disabled=["page", "title", "difference", "legal_impact", "risk_level"],
                        use_container_width=True,
                        hide_index=True,
                        key=f"editor_{active_it_id}"
                    )
                    
                    if st.button("💾 Save All Review Changes"):
                        with st.spinner("Saving..."):
                            for _, row in edited_df.iterrows():
                                # Uses the hidden 'id' to update the specific row
                                db.update_clause(row['id'], status=row['status'], notes=row['notes'])
                            st.success("Changes saved!")
                            st.rerun()

                    # Exports
                    st.divider()
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        st.subheader("📧 Draft Response")
                        u_input = st.text_area("Instructions for AI email draft?")
                        if st.button("Generate Email"):
                            email = engine.draft_email(u_input, it_data['overall_comparison'], edited_df)
                            st.text_area("AI Draft", value=email, height=300)
                    
                    with ec2:
                        st.subheader("📝 Export Redline")
                        if st.button("Generate Word Redline"):
                            path = f"Redline_v{it_data['iteration_number']}.docx"
                            engine.generate_redline_doc(it_data['full_text_a'], it_data['full_text_b'], path)
                            with open(path, "rb") as f:
                                st.download_button("Download .docx", f, file_name=path)

        # TAB 3: VERSION COMPARISON
        with tab_compare:
            st.subheader("Analyze Changes Between Client Versions")
            if len(iterations) < 2:
                st.warning("Need at least two iterations.")
            else:
                selected_ids = st.multiselect(
                    "Select versions to compare",
                    options=[it['id'] for it in iterations],
                    format_func=lambda x: next(f"v{i['iteration_number']}" for i in iterations if i['id'] == x)
                )
                if len(selected_ids) >= 2:
                    if st.button("Run Comparison"):
                        comparison = engine.compare_iterations(pid, selected_ids)
                        for change in comparison['document_changes']:
                            with st.expander(f"Changes: v{change['from']} ➡️ v{change['to']}"):
                                st.markdown(change['changes'])

if __name__ == "__main__":
    main()