import streamlit as st
from engine import (
    compare_documents, draft_email, generate_redline_doc,
    init_projects, create_project, get_all_projects, get_project,
    update_project_data, delete_project, set_current_project, get_current_project
)
import pandas as pd

st.set_page_config(page_title="NDA Comparator", layout="wide")

# Initialize projects
init_projects()

# Sidebar for project management
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
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Highlight current project
                is_current = proj_id == current_project_id
                button_label = f"{'🔵 ' if is_current else ''}{proj['name']}"
                
                if st.button(button_label, key=f"select_{proj_id}", use_container_width=True):
                    set_current_project(proj_id)
                    st.rerun()
                
                # Show project info
                st.caption(f"Created: {proj['created_at']}")
                status_badge = "🟢 Analyzed" if proj['status'] == 'analyzed' else "⚪ New"
                st.caption(status_badge)
            
            with col2:
                if st.button("🗑️", key=f"del_{proj_id}"):
                    delete_project(proj_id)
                    st.rerun()
            
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
    
    # Display current project header
    st.header(f"🔵 {current_project['name']}")
    if current_project['description']:
        st.caption(current_project['description'])
    st.divider()
    
    # Document upload section
    c1, c2 = st.columns(2)
    with c1: 
        docA = st.file_uploader("Document A (Standard NDA)", type=["pdf"], key=f"docA_{current_project_id}")
    with c2: 
        docB = st.file_uploader("Document B (Client NDA)", type=["pdf"], key=f"docB_{current_project_id}")
    
    if docA and docB:
        if st.button("🔍 Analyze Documents"):
            with st.spinner("Analyzing documents..."):
                t1, t2, overall, df, txtA, txtB = compare_documents(docA, docB)
                data = {
                    "t1": t1,
                    "t2": t2,
                    "overall": overall,
                    "df": df,
                    "A": txtA,
                    "B": txtB
                }
                update_project_data(current_project_id, data)
            st.success("✅ Analysis complete!")
            st.rerun()
    
    # Display analysis results if available
    if current_project['data'] is not None:
        d = current_project['data']
        
        # Document type info
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Document A:** {d['t1']}")
        with col2:
            st.info(f"**Document B:** {d['t2']}")
        
        # Overall comparison
        with st.expander("📋 Overall Comparison Summary", expanded=True):
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
                
                # Color code by risk level
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
                    
                    col_a, col_b, col_c = st.columns([1, 1, 3])
                    
                    if col_a.button("✅ Accept", key=f"accept_{current_project_id}_{idx}"):
                        df.at[idx, 'status'] = 'accepted'
                        d["df"] = df
                        update_project_data(current_project_id, d)
                        st.rerun()
                    
                    if col_b.button("❌ Reject", key=f"reject_{current_project_id}_{idx}"):
                        df.at[idx, 'status'] = 'rejected'
                        d["df"] = df
                        update_project_data(current_project_id, d)
                        st.rerun()
                    
                    # Notes field
                    note = st.text_input(
                        "Add notes/reason:",
                        value=row.get('notes', ''),
                        key=f"note_{current_project_id}_{idx}"
                    )
                    
                    if note != row.get('notes', ''):
                        df.at[idx, 'notes'] = note
                        d["df"] = df
                        update_project_data(current_project_id, d)
            
            st.divider()
            
            # Display full table
            st.subheader("📊 Complete Review Summary")
            display_cols = ['page', 'title', 'difference', 'legal_impact', 'risk', 'status', 'notes']
            st.dataframe(df[display_cols], use_container_width=True, height=300)
        
        st.divider()
        st.subheader("✉️ Draft Response Email")
        
        note = st.text_area("Additional message/concerns:", key=f"email_note_{current_project_id}")
        if st.button("📧 Draft Email"):
            with st.spinner("Drafting email..."):
                email = draft_email(note, d["overall"], d["df"])
            st.text_area("Email Draft", email, height=250, key=f"email_draft_{current_project_id}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Generate Redlined Word"):
                with st.spinner("Generating redlined document..."):
                    path = f"redlined_{current_project['name'].replace(' ', '_')}.docx"
                    generate_redline_doc(d["A"], d["B"], path)
                st.download_button("📥 Download Redline", open(path, "rb"), path)
        
        with col2:
            if st.button("📊 Export Review Summary"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv,
                    f"{current_project['name']}_review.csv",
                    "text/csv"
                )