import streamlit as st
from engine import (
    compare_documents, draft_email, generate_redline_doc,
    init_projects, create_project, get_all_projects, get_project,
    delete_project, set_current_project, get_current_project,
    create_iteration, get_current_iteration, set_current_iteration,
    update_iteration_data, compare_iterations, get_iteration_by_id
)
import pandas as pd
import io

st.set_page_config(page_title="NDA Comparator", layout="wide")

# Initialize projects
init_projects()

# Sidebar for project and iteration management
with st.sidebar:
    st.title("📂 Projects")
    
    # Create new project section
    with st.expander("➕ Create New Project", expanded=False):
        new_project_name = st.text_input("Project Name", key="new_proj_name")
        new_project_desc = st.text_area("Description (optional)", key="new_proj_desc")
        if st.button("Create Project"):
            if new_project_name:
                project_id = create_project(new_project_name, new_project_desc)
                set_current_project(project_id)
                st.success(f"✅ Created: {new_project_name}")
                st.rerun()
            else:
                st.error("Please enter a project name")
    
    st.divider()
    
    # List existing projects
    projects = get_all_projects()
    current_project_id = get_current_project()
    
    if projects:
        st.subheader("Your Projects")
        for proj_id, proj in projects.items():
            is_current = proj_id == current_project_id
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    button_label = f"{'🔵 ' if is_current else ''}{proj['name']}"
                    if st.button(button_label, key=f"select_{proj_id}", use_container_width=True):
                        set_current_project(proj_id)
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{proj_id}"):
                        delete_project(proj_id)
                        st.rerun()
                
                # Show iterations for current project
                if is_current and proj["iterations"]:
                    st.caption(f"📊 {len(proj['iterations'])} iteration(s)")
                    
                    # Show iteration list
                    with st.expander("📑 Iterations", expanded=True):
                        for iteration in proj["iterations"]:
                            iter_label = f"v{iteration['iteration_number']}"
                            is_current_iter = proj["current_iteration"] == iteration["id"]
                            
                            col_a, col_b = st.columns([3, 1])
                            with col_a:
                                if is_current_iter:
                                    st.info(f"📍 {iter_label} - {iteration['created_at']}")
                                else:
                                    if st.button(iter_label, key=f"iter_{iteration['id']}", use_container_width=True):
                                        set_current_iteration(proj_id, iteration["id"])
                                        st.rerun()
                            
                            with col_b:
                                # Show stats badge
                                if iteration["data"]:
                                    df = iteration["data"]["df"]
                                    if not df.empty and 'status' in df.columns:
                                        accepted = len(df[df['status'] == 'accepted'])
                                        rejected = len(df[df['status'] == 'rejected'])
                                        st.caption(f"✅{accepted} ❌{rejected}")
                            
                            if not is_current_iter:
                                st.caption(f"{iteration['docA_name']} vs {iteration['docB_name']}")
                                st.markdown("---")
                elif is_current:
                    st.caption("No iterations yet")
                
                st.divider()
    else:
        st.info("No projects yet. Create one to get started!")

# Main content area
st.title("📄 NDA Review & Negotiation AI")

current_project_id = get_current_project()

if current_project_id is None:
    st.info("👈 Please select or create a project from the sidebar to begin.")
else:
    current_project = get_project(current_project_id)
    current_iteration = get_current_iteration(current_project_id)
    
    # Display current project header
    st.header(f"🔵 {current_project['name']}")
    if current_project['description']:
        st.caption(current_project['description'])
    
    # Show iteration info if exists
    if current_iteration:
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            st.info(f"📌 Current: v{current_iteration['iteration_number']}")
        with col2:
            st.info(f"🕒 {current_iteration['created_at']}")
        with col3:
            if len(current_project["iterations"]) > 1:
                if st.button("🔄 Compare"):
                    st.session_state["show_comparison"] = True
    
    st.divider()
    
    # Comparison view
    if st.session_state.get("show_comparison", False) and len(current_project["iterations"]) > 1:
        st.subheader("📊 Compare Iterations - Document Changes")
        
        st.info("💡 Select multiple iterations to see what the client changed in their NDA versions")
        
        # Multi-select for iterations
        iter_options = {f"v{it['iteration_number']} - {it['created_at']}": it['id'] 
                       for it in current_project["iterations"]}
        
        selected_iters = st.multiselect(
            "Select iterations to compare (in order)",
            list(iter_options.keys()),
            default=list(iter_options.keys())[:2] if len(iter_options) >= 2 else list(iter_options.keys()),
            help="Select 2 or more iterations. Comparison will show changes from earliest to latest."
        )
        
        if len(selected_iters) >= 2:
            if st.button("🔍 Compare Selected Iterations", type="primary"):
                # Get iteration IDs in order
                selected_ids = [iter_options[name] for name in selected_iters]
                
                with st.spinner("Analyzing document changes across iterations..."):
                    comparison = compare_iterations(current_project_id, selected_ids)
                
                if comparison:
                    # Show iteration overview
                    st.write("### 📋 Selected Iterations")
                    cols = st.columns(len(comparison["iterations"]))
                    
                    for i, iter_info in enumerate(comparison["iterations"]):
                        with cols[i]:
                            st.markdown(f"**v{iter_info['number']}**")
                            st.caption(f"📅 {iter_info['date']}")
                            st.caption(f"📄 {iter_info['docs']}")
                    
                    st.divider()
                    
                    # Show document changes between versions
                    if "document_changes" in comparison and comparison["document_changes"]:
                        st.write("### 🔄 What Changed in Client's NDA")
                        
                        for change in comparison["document_changes"]:
                            with st.expander(f"📝 Changes from v{change['from']} → v{change['to']}", expanded=True):
                                st.markdown(change['changes'])
                    else:
                        st.info("ℹ️ No significant changes detected between selected iterations")
        else:
            st.warning("⚠️ Please select at least 2 iterations to compare")
        
        if st.button("← Back to Current Iteration"):
            st.session_state["show_comparison"] = False
            st.rerun()
        
        st.divider()
    
    # New iteration section
    st.subheader("📤 Create New Iteration")
    
    with st.expander("➕ Add New Iteration", expanded=not current_iteration):
        st.write("Upload documents to create a new iteration for this project")
        
        c1, c2 = st.columns(2)
        with c1: 
            docA = st.file_uploader("Document A (Standard NDA)", type=["pdf"], key=f"docA_{current_project_id}")
        with c2: 
            docB = st.file_uploader("Document B (Client NDA)", type=["pdf"], key=f"docB_{current_project_id}")
        
        if docA and docB:
            if st.button("🔍 Create Iteration & Analyze", type="primary", use_container_width=True):
                with st.spinner("Creating iteration and analyzing documents..."):
                    # Read file bytes for storage
                    docA_bytes = docA.read()
                    docB_bytes = docB.read()
                    
                    # Reset file pointers
                    docA.seek(0)
                    docB.seek(0)
                    
                    # Create iteration
                    iteration_id = create_iteration(
                        current_project_id,
                        docA.name,
                        docB.name,
                        docA_bytes,
                        docB_bytes
                    )
                    
                    # Analyze documents
                    t1, t2, overall, df, txtA, txtB = compare_documents(docA, docB)
                    data = {
                        "t1": t1,
                        "t2": t2,
                        "overall": overall,
                        "df": df,
                        "A": txtA,
                        "B": txtB
                    }
                    update_iteration_data(current_project_id, iteration_id, data)
                    
                st.success(f"✅ Iteration v{len(current_project['iterations'])} created and analyzed!")
                st.rerun()
        elif not docA or not docB:
            st.info("📄 Upload both documents to create a new iteration")
    st.divider()
    
    # Display current iteration analysis
    if current_iteration and current_iteration['data'] is not None:
        d = current_iteration['data']
        
        # Document type info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Document A:** {d['t1']}")
        with col2:
            st.info(f"**Document B:** {d['t2']}")
        
        # Overall comparison
        with st.expander("📋 Overall Comparison Summary", expanded=False):
            st.write(d["overall"])
        
        st.divider()
        st.subheader("📋 Clause-by-Clause Review")
        
        df = d["df"]
        
        if not df.empty and 'status' in df.columns:
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            total = len(df)
            accepted = len(df[df['status'] == 'accepted'])
            rejected = len(df[df['status'] == 'rejected'])
            pending = len(df[df['status'] == 'pending'])
            
            col1.metric("Total Clauses", total)
            col2.metric("✅ Accepted", accepted)
            col3.metric("❌ Rejected", rejected)
            col4.metric("⏳ Pending", pending)
            
            st.divider()
            
            # Filter options
            filter_opt = st.selectbox("Filter by status:", ["All", "Pending", "Accepted", "Rejected"])
            
            if filter_opt == "Pending":
                display_df = df[df['status'] == 'pending']
            elif filter_opt == "Accepted":
                display_df = df[df['status'] == 'accepted']
            elif filter_opt == "Rejected":
                display_df = df[df['status'] == 'rejected']
            else:
                display_df = df
            
            # Review each clause
            for idx in display_df.index:
                row = df.loc[idx]
                
                risk_color = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(row.get('risk', 'medium'), "⚪")
                
                status_emoji = {
                    "accepted": "✅",
                    "rejected": "❌",
                    "pending": "⏳"
                }.get(row['status'], "⏳")
                
                with st.expander(f"{status_emoji} {risk_color} Page {row['page']} - {row.get('title', 'Clause')}"):
                    st.markdown(f"**Difference:** {row.get('difference', 'N/A')}")
                    st.markdown(f"**Legal Impact:** {row.get('legal_impact', 'N/A')}")
                    st.markdown(f"**Risk Level:** {row.get('risk', 'N/A').upper()}")
                    
                    col_a, col_b = st.columns(2)
                    
                    if col_a.button("✅ Accept", key=f"accept_{current_iteration['id']}_{idx}"):
                        df.at[idx, 'status'] = 'accepted'
                        d["df"] = df
                        update_iteration_data(current_project_id, current_iteration['id'], d)
                        st.rerun()
                    
                    if col_b.button("❌ Reject", key=f"reject_{current_iteration['id']}_{idx}"):
                        df.at[idx, 'status'] = 'rejected'
                        d["df"] = df
                        update_iteration_data(current_project_id, current_iteration['id'], d)
                        st.rerun()
                    
                    note = st.text_input(
                        "Add notes/reason:",
                        value=row.get('notes', ''),
                        key=f"note_{current_iteration['id']}_{idx}"
                    )
                    
                    if note != row.get('notes', ''):
                        df.at[idx, 'notes'] = note
                        d["df"] = df
                        update_iteration_data(current_project_id, current_iteration['id'], d)
            
            st.divider()
            
            # Display full table
            st.subheader("📊 Complete Review Summary")
            display_cols = ['page', 'title', 'difference', 'legal_impact', 'risk', 'status', 'notes']
            st.dataframe(df[display_cols], use_container_width=True, height=300)
        
        st.divider()
        st.subheader("✉️ Draft Response Email")
        
        note = st.text_area("Additional message/concerns:", key=f"email_note_{current_iteration['id']}")
        if st.button("📧 Draft Email"):
            with st.spinner("Drafting email..."):
                email = draft_email(note, d["overall"], d["df"])
            st.text_area("Email Draft", email, height=250, key=f"email_draft_{current_iteration['id']}")
        
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📄 Generate Redlined Word"):
                with st.spinner("Generating redlined document..."):
                    path = f"redlined_v{current_iteration['iteration_number']}_{current_project['name'].replace(' ', '_')}.docx"
                    generate_redline_doc(d["A"], d["B"], path)
                st.download_button("📥 Download Redline", open(path, "rb"), path)
        
        with col2:
            if st.button("📊 Export Review Summary"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"v{current_iteration['iteration_number']}_{current_project['name']}_review.csv",
                    "text/csv"
                )
        
        with col3:
            if st.button("💾 Download PDFs"):
                # Create info about the PDFs
                info = f"Iteration v{current_iteration['iteration_number']}\n"
                info += f"Project: {current_project['name']}\n"
                info += f"Document A: {current_iteration['docA_name']}\n"
                info += f"Document B: {current_iteration['docB_name']}\n"
                info += f"Created: {current_iteration['created_at']}\n"
                st.download_button(
                    "📥 Download Info",
                    info,
                    f"v{current_iteration['iteration_number']}_documents_info.txt",
                    "text/plain"
                )