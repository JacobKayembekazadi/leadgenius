import streamlit as st
import pandas as pd
from lead_generator import generate_leads
from ai_outreach import generate_personalized_outreach_gemini, create_lead_profile, configure_gemini, generate_bulk_outreach, save_outreach_messages
from email_sender import EmailSender, format_email_content
import os
import json
from datetime import datetime
import uuid
import pyperclip

# --- Page Configuration ---
st.set_page_config(
    page_title="LeadGenius CRUD",
    page_icon="🤖",
    layout="wide",
)

# --- Helper functions ---
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def load_leads_from_file():
    """Load leads from JSON file if it exists"""
    try:
        if os.path.exists('leads_database.json'):
            with open('leads_database.json', 'r') as f:
                data = json.load(f)
                return pd.DataFrame(data)
    except:
        pass
    return pd.DataFrame()

def save_leads_to_file(df):
    """Save leads to JSON file"""
    try:
        df.to_json('leads_database.json', orient='records', indent=2)
        return True
    except:
        return False

def initialize_session_state():
    """Initialize session state variables"""
    if 'leads_df' not in st.session_state:
        st.session_state.leads_df = load_leads_from_file()
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'edit_index' not in st.session_state:
        st.session_state.edit_index = None
    if 'show_add_form' not in st.session_state:
        st.session_state.show_add_form = False

# Initialize session state
initialize_session_state()

# --- UI Sections ---
st.title("🤖 LeadGenius: CRUD Lead Management System")
st.markdown("Generate, manage, and organize your business leads with full CRUD functionality.")

# --- Sidebar for CRUD Operations ---
with st.sidebar:
    st.header("🛠️ Lead Management")
    
    # CRUD Operation Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add Lead", use_container_width=True):
            st.session_state.show_add_form = True
            st.session_state.edit_mode = False
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.leads_df = load_leads_from_file()
            st.rerun()
    
    # Lead Statistics
    if not st.session_state.leads_df.empty:
        st.subheader("📊 Lead Statistics")
        total_leads = len(st.session_state.leads_df)
        st.metric("Total Leads", total_leads)
        
        # Show status distribution if exists
        if 'status' in st.session_state.leads_df.columns:
            status_counts = st.session_state.leads_df['status'].value_counts()
            for status, count in status_counts.items():
                st.metric(f"{status} Leads", count)
    
    st.divider()
    
    # API Key Management
    st.subheader("🔑 API Configuration")
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API key configured!")
    except:
        st.warning("⚠️ No API key in secrets")
        api_key = st.text_input("Google Maps API Key:", type="password")

# --- Main Content Area ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Generate Leads", "📋 Manage Leads", "🤖 AI Outreach", "📊 Analytics", "📧 Human-in-the-Loop"])

with tab1:
    st.subheader("🔍 Generate New Leads")
    
    # --- Search Form ---
    with st.form("search_form"):
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            business_type = st.text_input("Business Type", "e.g., restaurants, plumbers, law firms")
        with col2:
            location = st.text_input("Location", "e.g., San Francisco, CA")
        with col3:
            max_results = st.number_input("Max Results", min_value=5, max_value=100, value=20, step=5)
        
        submitted = st.form_submit_button("✨ Generate Leads")

    # --- Lead Generation Results ---
    if submitted:
        if not api_key:
            st.error("Please provide a Google Maps API key to proceed.")
        elif not business_type or not location:
            st.error("Please enter both a business type and location.")
        else:
            query = f"{business_type} in {location}"
            st.write(f"Searching for: **{query}**")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                leads_generator = generate_leads(api_key, query, max_results)
                
                all_leads = []
                for i, (status, current_leads) in enumerate(leads_generator):
                    all_leads = current_leads
                    status_text.text(status)
                    progress_bar.progress((i + 1) / max_results)
                
                # Add generated leads to existing database
                new_leads_df = pd.DataFrame(all_leads)
                if not new_leads_df.empty:
                    # Add unique IDs and timestamps
                    new_leads_df['id'] = [str(uuid.uuid4()) for _ in range(len(new_leads_df))]
                    new_leads_df['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    new_leads_df['status'] = 'New'
                    
                    # Merge with existing leads
                    if st.session_state.leads_df.empty:
                        st.session_state.leads_df = new_leads_df
                    else:
                        st.session_state.leads_df = pd.concat([st.session_state.leads_df, new_leads_df], ignore_index=True)
                    
                    # Save to file
                    save_leads_to_file(st.session_state.leads_df)
                    status_text.success(f"✅ Generated {len(new_leads_df)} new leads!")
                    
                    # Show preview
                    st.subheader("🎯 New Leads Generated")
                    st.dataframe(new_leads_df[['Business Name', 'Address', 'Phone', 'Website', 'Found Emails']], use_container_width=True)

            except Exception as e:
                st.error(f"❌ An error occurred: {e}")

with tab2:
    st.subheader("📋 Lead Database Management")
    
    if st.session_state.leads_df.empty:
        st.info("No leads in database. Generate some leads first!")
    else:
        # Search and filter
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_term = st.text_input("🔍 Search leads", placeholder="Search by business name, phone, email...")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All"] + list(st.session_state.leads_df['status'].unique()) if 'status' in st.session_state.leads_df.columns else ["All"])
        with col3:
            sort_by = st.selectbox("Sort by", ["Business Name", "created_at", "status"] if 'created_at' in st.session_state.leads_df.columns else ["Business Name"])
        
        # Apply filters
        filtered_df = st.session_state.leads_df.copy()
        
        if search_term:
            mask = filtered_df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            filtered_df = filtered_df[mask]
        
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]
        
        # Display leads with CRUD operations
        if not filtered_df.empty:
            st.write(f"Showing {len(filtered_df)} of {len(st.session_state.leads_df)} leads")
            
            for idx, row in filtered_df.iterrows():
                with st.expander(f"🏢 {row.get('Business Name', 'Unknown Business')} - {row.get('status', 'Unknown')}"):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**Address:** {row.get('Address', 'N/A')}")
                        st.write(f"**Phone:** {row.get('Phone', 'N/A')}")
                        st.write(f"**Website:** {row.get('Website', 'N/A')}")
                        st.write(f"**Emails:** {row.get('Found Emails', 'N/A')}")
                        if 'created_at' in row:
                            st.write(f"**Created:** {row['created_at']}")
                    
                    with col2:
                        if st.button(f"✏️ Edit", key=f"edit_{idx}"):
                            st.session_state.edit_mode = True
                            st.session_state.edit_index = idx
                            st.session_state.show_add_form = False
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                            st.session_state.leads_df = st.session_state.leads_df.drop(idx).reset_index(drop=True)
                            save_leads_to_file(st.session_state.leads_df)
                            st.success("Lead deleted!")
                            st.rerun()
        
        # Bulk operations
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📥 Export All to CSV"):
                csv = convert_df_to_csv(st.session_state.leads_df)
                st.download_button(
                    label="📄 Download CSV",
                    data=csv,
                    file_name=f'leads_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                )
        
        with col2:
            if st.button("🗑️ Clear All Leads"):
                if st.session_state.get('confirm_clear'):
                    st.session_state.leads_df = pd.DataFrame()
                    save_leads_to_file(st.session_state.leads_df)
                    st.session_state.confirm_clear = False
                    st.success("All leads cleared!")
                    st.rerun()
                else:
                    st.session_state.confirm_clear = True
                    st.warning("Click again to confirm deletion of ALL leads!")

# --- Add/Edit Lead Form ---
if st.session_state.show_add_form or st.session_state.edit_mode:
    st.divider()
    
    if st.session_state.edit_mode:
        st.subheader("✏️ Edit Lead")
        lead_data = st.session_state.leads_df.iloc[st.session_state.edit_index]
    else:
        st.subheader("➕ Add New Lead")
        lead_data = {}
    
    with st.form("lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("Business Name", value=lead_data.get('Business Name', ''))
            address = st.text_input("Address", value=lead_data.get('Address', ''))
            phone = st.text_input("Phone", value=lead_data.get('Phone', ''))
        
        with col2:
            website = st.text_input("Website", value=lead_data.get('Website', ''))
            emails = st.text_input("Emails", value=lead_data.get('Found Emails', ''))
            status = st.selectbox("Status", ["New", "Contacted", "Qualified", "Converted", "Rejected"], 
                                index=["New", "Contacted", "Qualified", "Converted", "Rejected"].index(lead_data.get('status', 'New')) if lead_data.get('status') in ["New", "Contacted", "Qualified", "Converted", "Rejected"] else 0)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submitted = st.form_submit_button("💾 Save Lead")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state.show_add_form = False
            st.session_state.edit_mode = False
            st.session_state.edit_index = None
            st.rerun()
        
        if submitted:
            new_lead = {
                'id': lead_data.get('id', str(uuid.uuid4())),
                'Business Name': business_name,
                'Address': address,
                'Phone': phone,
                'Website': website,
                'Found Emails': emails,
                'status': status,
                'created_at': lead_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if st.session_state.edit_mode:
                # Update existing lead
                for key, value in new_lead.items():
                    st.session_state.leads_df.at[st.session_state.edit_index, key] = value
                st.success("Lead updated successfully!")
            else:
                # Add new lead
                if st.session_state.leads_df.empty:
                    st.session_state.leads_df = pd.DataFrame([new_lead])
                else:
                    st.session_state.leads_df = pd.concat([st.session_state.leads_df, pd.DataFrame([new_lead])], ignore_index=True)
                st.success("New lead added successfully!")
            
            # Save to file
            save_leads_to_file(st.session_state.leads_df)
            
            # Reset form state
            st.session_state.show_add_form = False
            st.session_state.edit_mode = False
            st.session_state.edit_index = None
            st.rerun()

with tab3:
    st.subheader("🤖 AI-Powered Outreach Generation")
    
    # Gemini API Key Configuration
    col1, col2 = st.columns([2, 1])
    with col1:
        try:
            gemini_api_key = st.secrets["GEMINI_API_KEY"]
            st.success("✅ Gemini AI key configured!")
        except:
            st.warning("⚠️ No Gemini API key in secrets")
            gemini_api_key = st.text_input("Google Gemini API Key:", type="password", help="Get your API key from Google AI Studio")
    
    with col2:
        if st.button("🧠 Test AI Connection"):
            if gemini_api_key:
                if configure_gemini(gemini_api_key):
                    st.success("✅ AI connection successful!")
                else:
                    st.error("❌ AI connection failed")
            else:
                st.error("Please provide an API key")
    
    if st.session_state.leads_df.empty:
        st.info("No leads available. Generate some leads first to create AI outreach messages!")
    else:
        # Lead selection for outreach
        st.subheader("📋 Select Leads for AI Outreach")
        
        # Filter leads that don't have outreach generated yet
        available_leads = st.session_state.leads_df.copy()
        
        # Show lead selection
        if not available_leads.empty:
            # Option to select individual leads or all
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.checkbox("🎯 Generate outreach for all leads", key="select_all_leads"):
                    selected_leads = available_leads
                    st.info(f"Selected all {len(selected_leads)} leads for AI outreach")
                else:
                    # Multi-select for individual leads
                    lead_options = [f"{row['Business Name']} - {row.get('status', 'New')}" for _, row in available_leads.iterrows()]
                    selected_indices = st.multiselect(
                        "Select leads for outreach:",
                        options=range(len(lead_options)),
                        format_func=lambda x: lead_options[x],
                        default=[]
                    )
                    selected_leads = available_leads.iloc[selected_indices] if selected_indices else pd.DataFrame()
            
            with col2:
                if st.button("🚀 Generate AI Outreach", disabled=selected_leads.empty or not gemini_api_key):
                    if not gemini_api_key:
                        st.error("Please provide a Gemini API key")
                    else:
                        with st.spinner("🧠 AI is generating personalized outreach messages..."):
                            try:
                                # Generate outreach for selected leads
                                outreach_results = generate_bulk_outreach(selected_leads, gemini_api_key)
                                
                                if outreach_results is not None and not outreach_results.empty:
                                    # Display generation analytics
                                    analytics = getattr(outreach_results, 'attrs', {}).get('analytics', {})
                                    
                                    col1, col2, col3, col4 = st.columns(4)
                                    with col1:
                                        st.metric("Success Rate", f"{analytics.get('success_rate', 0)}%")
                                    with col2:
                                        st.metric("Avg Confidence", f"{analytics.get('avg_confidence_score', 0)}/10")
                                    with col3:
                                        st.metric("High Quality", f"{analytics.get('high_confidence_count', 0)}")
                                    with col4:
                                        st.metric("Generated", f"{len(outreach_results)}")
                                    
                                    # Show personalization angles
                                    if analytics.get('personalization_angles'):
                                        st.subheader("🎯 Personalization Strategies Used")
                                        angles_data = analytics['personalization_angles']
                                        cols = st.columns(min(len(angles_data), 3))
                                        for i, (angle, count) in enumerate(angles_data.items()):
                                            with cols[i % 3]:
                                                st.info(f"**{angle}**: {count} leads")
                                    
                                    st.success(f"✅ Generated personalized outreach for {len(outreach_results)} leads!")
                                    
                                    # Save results to session state for display
                                    if 'outreach_messages' not in st.session_state:
                                        st.session_state.outreach_messages = pd.DataFrame()
                                    
                                    # Merge new messages with existing ones
                                    if st.session_state.outreach_messages.empty:
                                        st.session_state.outreach_messages = outreach_results
                                    else:
                                        st.session_state.outreach_messages = pd.concat([st.session_state.outreach_messages, outreach_results], ignore_index=True)
                                    
                                    # Save to file
                                    save_outreach_messages(st.session_state.outreach_messages)
                                    
                                    # Update lead status to "Contacted"
                                    for idx in selected_leads.index:
                                        st.session_state.leads_df.at[idx, 'status'] = 'Contacted'
                                        st.session_state.leads_df.at[idx, 'updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    
                                    # Save updated leads
                                    save_leads_to_file(st.session_state.leads_df)
                                    
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to generate outreach messages")
                                    
                            except Exception as e:
                                st.error(f"Error generating outreach: {e}")
            
            # Display generated outreach messages
            if 'outreach_messages' in st.session_state and not st.session_state.outreach_messages.empty:
                st.divider()
                st.subheader("📧 Generated Outreach Messages")
                
                # Analytics overview
                messages_df = st.session_state.outreach_messages
                if 'confidence_score' in messages_df.columns:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        avg_confidence = messages_df['confidence_score'].mean()
                        st.metric("Overall Confidence", f"{avg_confidence:.1f}/10")
                    with col2:
                        high_quality = len(messages_df[messages_df['confidence_score'] >= 8])
                        st.metric("High Quality Messages", f"{high_quality}/{len(messages_df)}")
                    with col3:
                        avg_email_words = messages_df.get('word_count_email', pd.Series([0])).mean()
                        st.metric("Avg Email Length", f"{avg_email_words:.0f} words")
                    with col4:
                        if 'personalization_angle' in messages_df.columns:
                            unique_strategies = messages_df['personalization_angle'].nunique()
                            st.metric("Strategy Variety", f"{unique_strategies} types")
                
                # Search and filter outreach messages
                col1, col2 = st.columns([2, 1])
                with col1:
                    search_outreach = st.text_input("🔍 Search outreach messages", placeholder="Search by business name...")
                with col2:
                    sort_options = ["generated_at", "business_name", "confidence_score"]
                    sort_outreach = st.selectbox("Sort by", sort_options, key="sort_outreach")
                
                # Apply filters
                filtered_outreach = st.session_state.outreach_messages.copy()
                if search_outreach:
                    mask = filtered_outreach['business_name'].str.contains(search_outreach, case=False, na=False)
                    filtered_outreach = filtered_outreach[mask]
                
                # Sort messages
                filtered_outreach = filtered_outreach.sort_values(sort_outreach, ascending=False)
                
                # Display messages
                for idx, message in filtered_outreach.iterrows():
                    # Create title with confidence indicator
                    confidence = message.get('confidence_score', 5)
                    confidence_emoji = "🎯" if confidence >= 8 else "⚡" if confidence >= 6 else "📝"
                    title = f"{confidence_emoji} {message['business_name']} - Confidence: {confidence}/10"
                    
                    with st.expander(title):
                        # Analytics row
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Confidence", f"{confidence}/10")
                        with col2:
                            st.metric("Email Words", message.get('word_count_email', 0))
                        with col3:
                            st.metric("LinkedIn Words", message.get('word_count_linkedin', 0))
                        with col4:
                            st.write("**Strategy:**")
                            st.write(message.get('personalization_angle', 'Unknown'))
                        
                        st.divider()
                        
                        # Messages
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📧 Email Message")
                            if 'email_subject' in message and message['email_subject']:
                                st.text_input(
                                    "Subject Line:",
                                    value=message['email_subject'],
                                    key=f"subject_{idx}",
                                    help="Email subject line"
                                )
                            st.text_area(
                                "Email Body:",
                                value=message['email_body'],
                                height=120,
                                key=f"email_{idx}",
                                help="Copy this message for your email outreach"
                            )
                        
                        with col2:
                            st.subheader("💼 LinkedIn Message")
                            st.text_area(
                                "LinkedIn DM:",
                                value=message['linkedin_dm'],
                                height=150,
                                key=f"linkedin_{idx}",
                                help="Copy this message for LinkedIn outreach"
                            )
                        
                        # Copy buttons and quality indicator
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button(f"📋 Copy Email", key=f"copy_email_{idx}"):
                                st.write("Email copied to display above ↑")
                        with col2:
                            if st.button(f"📋 Copy LinkedIn", key=f"copy_linkedin_{idx}"):
                                st.write("LinkedIn message copied to display above ↑")
                        with col3:
                            quality_color = "green" if confidence >= 8 else "orange" if confidence >= 6 else "red"
                            quality_text = "High Quality" if confidence >= 8 else "Good Quality" if confidence >= 6 else "Basic Quality"
                            st.markdown(f":{quality_color}[{quality_text}]")
                
                # Bulk operations for outreach
                st.divider()
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📥 Export Outreach Messages"):
                        csv_outreach = st.session_state.outreach_messages.to_csv(index=False)
                        st.download_button(
                            label="📄 Download Outreach CSV",
                            data=csv_outreach,
                            file_name=f'outreach_messages_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                            mime='text/csv',
                        )
                
                with col2:
                    if st.button("🗑️ Clear All Messages"):
                        if st.session_state.get('confirm_clear_outreach'):
                            st.session_state.outreach_messages = pd.DataFrame()
                            st.session_state.confirm_clear_outreach = False
                            st.success("All outreach messages cleared!")
                            st.rerun()
                        else:
                            st.session_state.confirm_clear_outreach = True
                            st.warning("Click again to confirm deletion!")

with tab4:
    st.subheader("📊 Lead Analytics")
    
    if st.session_state.leads_df.empty:
        st.info("No data available for analytics. Generate some leads first!")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Leads", len(st.session_state.leads_df))
        
        with col2:
            if 'status' in st.session_state.leads_df.columns:
                conversion_rate = len(st.session_state.leads_df[st.session_state.leads_df['status'] == 'Converted']) / len(st.session_state.leads_df) * 100
                st.metric("Conversion Rate", f"{conversion_rate:.1f}%")
        
        with col3:
            if 'created_at' in st.session_state.leads_df.columns:
                today_leads = len(st.session_state.leads_df[st.session_state.leads_df['created_at'].str.contains(datetime.now().strftime('%Y-%m-%d'))])
                st.metric("Today's Leads", today_leads)
        
        # Status distribution chart
        if 'status' in st.session_state.leads_df.columns:
            st.subheader("Lead Status Distribution")
            status_counts = st.session_state.leads_df['status'].value_counts()
            st.bar_chart(status_counts)
        
        # Recent activity
        if 'created_at' in st.session_state.leads_df.columns:
            st.subheader("Recent Leads")
            recent_leads = st.session_state.leads_df.sort_values('created_at', ascending=False).head(5)
            st.dataframe(recent_leads[['Business Name', 'status', 'created_at']], use_container_width=True)

with tab5:
    st.subheader("📧 Human-in-the-Loop Email & LinkedIn Management")
    st.markdown("Review and send AI-generated messages manually for complete control over your outreach.")
    
    # SendGrid API Key Configuration
    col1, col2 = st.columns([2, 1])
    with col1:
        try:
            sendgrid_api_key = st.secrets.get("SENDGRID_API_KEY", "")
            if sendgrid_api_key:
                st.success("✅ SendGrid API key configured!")
            else:
                st.warning("⚠️ No SendGrid API key in secrets")
                sendgrid_api_key = st.text_input("SendGrid API Key:", type="password", help="Get your API key from SendGrid dashboard")
        except:
            st.warning("⚠️ No SendGrid API key in secrets")
            sendgrid_api_key = st.text_input("SendGrid API Key:", type="password", help="Get your API key from SendGrid dashboard")
    
    with col2:
        from_email = st.text_input("From Email Address:", value="noreply@leadgenius.com", help="Email address to send from")
    
    # Check if we have outreach messages
    if 'outreach_messages' not in st.session_state or st.session_state.outreach_messages.empty:
        st.info("📝 No outreach messages available. Please generate AI outreach messages first in the 'AI Outreach' tab.")
    else:
        # Filter leads that have outreach messages and are ready for human review
        outreach_df = st.session_state.outreach_messages.copy()
        
        # Add a column to track email sent status if it doesn't exist
        if 'email_sent' not in outreach_df.columns:
            outreach_df['email_sent'] = False
            st.session_state.outreach_messages['email_sent'] = False
        
        # Filter options
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search_hitl = st.text_input("🔍 Search leads", placeholder="Search by business name...")
        with col2:
            status_filter_hitl = st.selectbox("Filter by Status", ["All", "Email Not Sent", "Email Sent"], key="hitl_status_filter")
        with col3:
            sort_hitl = st.selectbox("Sort by", ["generated_at", "business_name"], key="hitl_sort")
        
        # Apply filters
        filtered_hitl = outreach_df.copy()
        
        if search_hitl:
            mask = filtered_hitl['business_name'].str.contains(search_hitl, case=False, na=False)
            filtered_hitl = filtered_hitl[mask]
        
        if status_filter_hitl == "Email Not Sent":
            filtered_hitl = filtered_hitl[filtered_hitl['email_sent'] == False]
        elif status_filter_hitl == "Email Sent":
            filtered_hitl = filtered_hitl[filtered_hitl['email_sent'] == True]
        
        # Sort
        filtered_hitl = filtered_hitl.sort_values(sort_hitl, ascending=False)
        
        if filtered_hitl.empty:
            st.info("No leads match your current filters.")
        else:
            st.write(f"Showing {len(filtered_hitl)} leads with draft messages")
            
            # Initialize email sender
            email_sender = EmailSender(sendgrid_api_key) if sendgrid_api_key else None
            
            # Display each lead with action buttons
            for idx, lead in filtered_hitl.iterrows():
                # Find corresponding lead data for email
                lead_data = None
                if not st.session_state.leads_df.empty:
                    matching_leads = st.session_state.leads_df[st.session_state.leads_df['Business Name'] == lead['business_name']]
                    if not matching_leads.empty:
                        lead_data = matching_leads.iloc[0]
                
                # Create expander for each lead
                status_icon = "✅" if lead.get('email_sent', False) else "📧"
                with st.expander(f"{status_icon} {lead['business_name']} - Generated {lead['generated_at']}"):
                    
                    # Display lead information
                    if lead_data is not None:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Address:** {lead_data.get('Address', 'N/A')}")
                            st.write(f"**Phone:** {lead_data.get('Phone', 'N/A')}")
                        with col2:
                            st.write(f"**Website:** {lead_data.get('Website', 'N/A')}")
                            st.write(f"**Email:** {lead_data.get('Found Emails', 'N/A')}")
                    
                    # Display draft messages
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("📧 Draft Email")
                        email_content = st.text_area(
                            "Email Body:",
                            value=lead['email_body'],
                            height=200,
                            key=f"hitl_email_{idx}",
                            help="Edit this message before sending"
                        )
                        
                        # Email subject
                        email_subject = st.text_input(
                            "Email Subject:",
                            value=f"Business Growth Opportunity for {lead['business_name']}",
                            key=f"subject_{idx}"
                        )
                    
                    with col2:
                        st.subheader("💼 LinkedIn Message")
                        linkedin_content = st.text_area(
                            "LinkedIn DM:",
                            value=lead['linkedin_dm'],
                            height=200,
                            key=f"hitl_linkedin_{idx}",
                            help="Copy this message for LinkedIn outreach"
                        )
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                    
                    # Send Email Button
                    with col1:
                        email_disabled = not sendgrid_api_key or lead_data is None or not lead_data.get('Found Emails')
                        send_button_text = "📧 Send Email"
                        if lead.get('email_sent', False):
                            send_button_text = "✅ Email Sent"
                            email_disabled = True
                        
                        if st.button(send_button_text, key=f"send_{idx}", disabled=email_disabled):
                            if email_sender and lead_data is not None and lead_data.get('Found Emails'):
                                recipient_email = lead_data['Found Emails'].split(',')[0].strip()  # Use first email if multiple
                                
                                # Format email content
                                html_content = format_email_content(lead_data, email_content)
                                
                                # Send email
                                result = email_sender.send_email(
                                    to_email=recipient_email,
                                    subject=email_subject,
                                    html_content=html_content,
                                    from_email=from_email
                                )
                                
                                # Log activity
                                email_sender.log_email_activity(
                                    lead_id=lead_data.get('id', 'unknown'),
                                    to_email=recipient_email,
                                    subject=email_subject,
                                    status="success" if result['success'] else "failed",
                                    message=result['message']
                                )
                                
                                if result['success']:
                                    st.success(f"✅ Email sent successfully to {recipient_email}")
                                    # Mark as sent in the dataframe
                                    st.session_state.outreach_messages.at[idx, 'email_sent'] = True
                                    
                                    # Update lead status
                                    lead_idx = st.session_state.leads_df[st.session_state.leads_df['Business Name'] == lead['business_name']].index
                                    if not lead_idx.empty:
                                        st.session_state.leads_df.at[lead_idx[0], 'status'] = 'Contacted'
                                        st.session_state.leads_df.at[lead_idx[0], 'updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        save_leads_to_file(st.session_state.leads_df)
                                    
                                    st.rerun()
                                else:
                                    st.error(f"❌ Failed to send email: {result['message']}")
                    
                    # Copy LinkedIn Message Button
                    with col2:
                        if st.button("📋 Copy LinkedIn", key=f"copy_linkedin_hitl_{idx}"):
                            try:
                                # Use JavaScript to copy to clipboard
                                st.write("Copy this LinkedIn message:")
                                st.code(linkedin_content, language="text")
                                st.info("💡 Tip: Select the text above and copy it manually, then paste into LinkedIn")
                            except Exception as e:
                                st.error(f"Copy failed: {e}")
                    
                    # Reject Button
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{idx}"):
                            # Update lead status to rejected
                            lead_idx = st.session_state.leads_df[st.session_state.leads_df['Business Name'] == lead['business_name']].index
                            if not lead_idx.empty:
                                st.session_state.leads_df.at[lead_idx[0], 'status'] = 'Rejected'
                                st.session_state.leads_df.at[lead_idx[0], 'updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                save_leads_to_file(st.session_state.leads_df)
                                st.success(f"Lead {lead['business_name']} marked as rejected")
                                st.rerun()
                    
                    # Preview Email Button
                    with col4:
                        if st.button("👁️ Preview", key=f"preview_{idx}"):
                            if lead_data is not None:
                                html_preview = format_email_content(lead_data, email_content)
                                st.components.v1.html(html_preview, height=400, scrolling=True)
        
        # Statistics
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_messages = len(outreach_df)
            st.metric("Total Messages", total_messages)
        
        with col2:
            sent_emails = len(outreach_df[outreach_df.get('email_sent', False) == True])
            st.metric("Emails Sent", sent_emails)
        
        with col3:
            pending_emails = total_messages - sent_emails
            st.metric("Pending Emails", pending_emails)
        
        with col4:
            if total_messages > 0:
                sent_rate = (sent_emails / total_messages) * 100
                st.metric("Sent Rate", f"{sent_rate:.1f}%") 