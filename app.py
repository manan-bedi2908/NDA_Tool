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
import database as db  # This calls st.secrets/st.session_state during import
import engine         # This calls st.secrets during import

# --- AUTHENTICATION CHECK ---
def check_auth():
    """Checks if user is logged in via Supabase Auth"""
    if not db.is_authenticated():
        st.title("⚖️ Artiaz Legal AI")
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            with st.form("login"):
                e = st.text_input("Email")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    success, msg = db.sign_in(e, p)
                    if success: st.rerun()
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

        # Project Selection List
        projects = db.get_all_projects()
        if not projects:
            st.info("No projects yet.")
        else:
            project_names = [p['name'] for p in projects]
            selected_name = st.selectbox("Select Project", project_names)
            curr_project = next(p for p in projects if p['name'] == selected_name)
            st.session_state['current_project_id'] = curr_project['id']

    # --- MAIN CONTENT ---
    if 'current_project_id' in st.session_state:
        pid = st.session_state['current_project_id']
        project = db.get_project(pid)
        
        st.header(f"Project: {project['name']}")
        
        # UI Organization via Tabs
        tab_new, tab_history, tab_compare = st.tabs(["🚀 New Analysis", "📜 Iteration History", "🔄 Version Comparison"])

        # TAB 1: NEW ANALYSIS
        with tab_new:
            st.subheader("Upload Documents")
            c1, c2 = st.columns(2)
            with c1: doc_a = st.file_uploader("Standard NDA (PDF)", type="pdf")
            with c2: doc_b = st.file_uploader("Client NDA (PDF)", type="pdf")
            
            if st.button("Analyze Documents", type="primary") and doc_a and doc_b:
                with st.spinner("AI is analyzing legal risks..."):
                    # Pipeline handles extraction, AI classification, and Supabase insertion
                    iter_id = engine.run_comparison_pipeline(pid, doc_a, doc_b)
                    if iter_id:
                        st.success("Analysis Complete!")
                        # Store in session state so History tab can focus on it immediately
                        st.session_state['active_iter_id'] = iter_id
                        st.rerun()

        # TAB 2: HISTORY & REVIEW (FIXES KeyErrors and UnboundLocalErrors)
        with tab_history:
            iterations = db.get_iterations(pid)
            if not iterations:
                st.info("No iterations yet. Run a new analysis in the first tab.")
            else:
                it_options = {f"v{it['iteration_number']} - {it['created_at'][:16]}": it['id'] for it in iterations}
                
                # Automatically select the iteration just created, or the first one available
                default_idx = 0
                if 'active_iter_id' in st.session_state:
                    for i, (label, it_id) in enumerate(it_options.items()):
                        if it_id == st.session_state['active_iter_id']:
                            default_idx = i

                selected_it_label = st.selectbox("Select Iteration to View", list(it_options.keys()), index=default_idx)
                active_it_id = it_options[selected_it_label]
                
                # Fetch fresh data from DB using the ID retrieved from selectbox
                it_data = db.get_iteration(active_it_id)
                clauses_df = db.get_clauses(active_it_id)

                # Show AI Summary
                st.divider()
                st.subheader("Executive Summary")
                st.info(it_data['overall_comparison'])

                # --- INTERACTIVE CLAUSE TABLE (FIXED) ---
                st.subheader("Clause-by-Clause Review")
                if not clauses_df.empty:
                    # Fix KeyError: 'id' by keeping 'id' in the df but hiding it in the config
                    # Fix Clutter by hiding technical columns
                    edited_df = st.data_editor(
                        clauses_df,
                        column_config={
                            "id": None,  # Hides from UI but keeps it in data for row updates
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
                        with st.spinner("Saving changes to database..."):
                            # This loop relies on 'id' being present in the edited_df
                            for _, row in edited_df.iterrows():
                                db.update_clause(row['id'], status=row['status'], notes=row['notes'])
                            st.success("Changes saved successfully!")
                            st.rerun()

                    # Email & Redline Exports
                    st.divider()
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        st.subheader("📧 Draft Response")
                        u_input = st.text_area("Specific instructions for AI Draft?")
                        if st.button("Generate Email"):
                            # Passes edited_df to include human-made notes in the email prompt
                            email = engine.draft_email(u_input, it_data['overall_comparison'], edited_df)
                            st.text_area("AI Drafted Email", value=email, height=300)
                    
                    with ec2:
                        st.subheader("📝 Export Redline")
                        if st.button("Generate Word Document"):
                            path = f"Redline_v{it_data['iteration_number']}.docx"
                            engine.generate_redline_doc(it_data['full_text_a'], it_data['full_text_b'], path)
                            with open(path, "rb") as f:
                                st.download_button("Download Redlined .docx", f, file_name=path)
                else:
                    st.warning("No clauses detected for this analysis.")

        # TAB 3: COMPARISON
        with tab_compare:
            st.subheader("Analyze Changes Between Iterations")
            if len(iterations) < 2:
                st.warning("You need at least two iterations to compare versions.")
            else:
                selected_ids = st.multiselect(
                    "Select versions to compare",
                    options=[it['id'] for it in iterations],
                    format_func=lambda x: next(f"v{i['iteration_number']}" for i in iterations if i['id'] == x)
                )
                if len(selected_ids) >= 2:
                    if st.button("Run Version-over-Version Analysis"):
                        comparison = engine.compare_iterations(pid, selected_ids)
                        for change in comparison['document_changes']:
                            with st.expander(f"Changes: v{change['from']} ➡️ v{change['to']}"):
                                st.markdown(change['changes'])

if __name__ == "__main__":
    main()