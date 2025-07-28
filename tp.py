import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import re
import pandas as pd
import docx
from fpdf import FPDF

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Career Toolkit",
    page_icon="🏆",
    layout="wide"
)

# --- Initialize Session State ---
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = ""
if 'ats_result' not in st.session_state:
    st.session_state.ats_result = ""
if 'roadmap_result' not in st.session_state:
    st.session_state.roadmap_result = ""
if 'opportunity_result' not in st.session_state:
    st.session_state.opportunity_result = ""
if 'enhanced_resume' not in st.session_state:
    st.session_state.enhanced_resume = ""
if 'cover_letter_result' not in st.session_state:
    st.session_state.cover_letter_result = ""
if 'trends_result' not in st.session_state:
    st.session_state.trends_result = None
if 'app_started' not in st.session_state:
    st.session_state.app_started = False

# --- AI Model Configuration ---
try:
    # This is the hardcoded version for your local computer to work.
    # IMPORTANT: Remember to remove this and use st.secrets before your final push to GitHub.
    MY_API_KEY = "PASTE_YOUR_REAL_KEY_HERE"
    genai.configure(api_key=MY_API_KEY)
    
    generation_config = genai.types.GenerationConfig(temperature=0.2)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error configuring the AI model: {e}")
    st.stop()

# --- Helper Functions ---
def extract_text_from_file(file):
    try:
        if file.name.endswith('.pdf'):
            doc = fitz.open(stream=file.read(), filetype="pdf")
            text = "".join(page.get_text() for page in doc)
        elif file.name.endswith('.docx'):
            doc = docx.Document(file)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            st.error("Unsupported file type.")
            return None
        
        if not text.strip():
            st.error("Error: This file contains no text.")
            return None
        return text
    except Exception as e:
        st.error("An error occurred while reading the file.")
        st.exception(e)
        return None

def text_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    encoded_text = text.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 5, encoded_text)
    return pdf.output(dest='S').encode('latin-1')

# --- Main Application UI ---
st.title("AI-Powered Career Toolkit 🏆")
st.write("Your all-in-one assistant for resume feedback, career planning, and job applications.")

uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

if uploaded_file is not None:
    st.session_state.app_started = True

if not st.session_state.app_started:
    st.info("💡 Upload your resume to unlock your personalized AI career toolkit!")
    st.subheader("Features:")
    st.markdown("""
    - **📄 Resume Feedback:** Get a general score or a specific ATS score against a job description.
    - **✨ Resume Enhancement:** Rewrite your resume for maximum impact with one click.
    - **🗺️ Learning Roadmap:** Receive a personalized plan to bridge your skill gaps for a target role.
    - **🎯 Career Insights:** Discover unique job roles and future market trends for your desired career.
    - **✍️ Cover Letter Generator:** Create a tailored cover letter for any job description.
    """)

if st.session_state.app_started and uploaded_file is not None:
    resume_text = extract_text_from_file(uploaded_file)
    if resume_text:
        st.header("Interactive Resume Editor & Toolkit")
        
        target_job = st.text_input("Enter a Target Job Title for Analysis (used across all tabs)")

        left_column, right_column = st.columns(2)

        with left_column:
            st.subheader("Edit Your Resume Text")
            edited_text = st.text_area(
                "Resume Content",
                resume_text,
                height=700,
                label_visibility="collapsed"
            )

        with right_column:
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Resume Feedback", "🗺️ Learning Roadmap", "🎯 Career Insights", "✍️ Cover Letter"])

            with tab1:
                st.subheader("Resume Analysis")
                st.markdown("##### Get General Feedback")
                st.info("Get an overall score and general feedback from our AI recruiter.")
                if st.button("Run General Analysis"):
                    with st.spinner("Running general analysis..."):
                        live_editor_prompt = f"""
                        You are a top-tier executive recruiter...
                        ---
                        {edited_text}
                        ---
                        """
                        try:
                            response = model.generate_content(live_editor_prompt, generation_config=generation_config)
                            st.session_state.general_result = response.text
                        except Exception as e:
                            st.error(f"An error occurred during analysis: {e}")
                
                if st.session_state.general_result:
                    response_text = st.session_state.general_result
                    score = 0
                    match = re.search(r'(\d+)\s*/\s*100', response_text)
                    if match:
                        score = int(match.group(1))
                        st.metric(label="General Score", value=f"{score} / 100")
                    with st.expander("See Detailed General Feedback"):
                        st.markdown(response_text)

                st.divider()

                st.markdown("##### Get ATS Compatibility Score")
                st.info("Paste a job description to get a specific ATS score and keyword analysis.")
                job_desc_for_ats = st.text_area("Paste the Job Description here for ATS Analysis")
                if st.button("Run ATS Analysis"):
                    if job_desc_for_ats:
                        with st.spinner("Running ATS simulation..."):
                            ats_prompt = f"""
                            You are an advanced Applicant Tracking System (ATS)...
                            ---
                            **USER'S RESUME:**
                            {edited_text}
                            ---
                            **TARGET JOB DESCRIPTION:**
                            {job_desc_for_ats}
                            ---
                            """
                            try:
                                response = model.generate_content(ats_prompt, generation_config=generation_config)
                                st.session_state.ats_result = response.text
                            except Exception as e:
                                st.error(f"An error occurred during analysis: {e}")
                    else:
                        st.warning("Please paste a job description to run the ATS analysis.")
                
                if st.session_state.ats_result:
                    response_text = st.session_state.ats_result
                    score = 0
                    match = re.search(r'(\d+)\s*/\s*100', response_text)
                    if match:
                        score = int(match.group(1))
                        st.metric(label="ATS Score", value=f"{score} / 100")
                    with st.expander("See Detailed ATS Feedback"):
                        st.markdown(response_text)

                st.divider()

                if st.button("✨ Generate Enhanced Version"):
                    with st.spinner("Rewriting your resume for maximum impact..."):
                        enhancement_prompt = f"""
                        You are a world-class resume writer...
                        ---
                        {edited_text}
                        ---
                        """
                        try:
                            response = model.generate_content(enhancement_prompt, generation_config=generation_config)
                            st.session_state.enhanced_resume = response.text
                        except Exception as e:
                            st.error(f"An error occurred during enhancement: {e}")

                if st.session_state.enhanced_resume:
                    with st.expander("View AI-Enhanced Resume Version", expanded=True):
                        st.code(st.session_state.enhanced_resume)
                        pdf_data = text_to_pdf(st.session_state.enhanced_resume)
                        st.download_button(
                            label="Download Enhanced Resume as PDF",
                            data=pdf_data,
                            file_name="enhanced_resume.pdf",
                            mime="application/pdf"
                        )

            with tab2:
                st.subheader("Your Personalized Learning Roadmap")
                roadmap_personalization = st.text_area("Add any personalizations (e.g., 'create a 60-day plan', 'focus on free courses')")
                if st.button("Generate My Roadmap"):
                    if target_job:
                        with st.spinner(f"Building your roadmap for {target_job}..."):
                            roadmap_prompt = f"""
                            You are a world-class academic advisor...
                            ---
                            {edited_text}
                            ---
                            """
                            try:
                                roadmap_response = model.generate_content(roadmap_prompt, generation_config=generation_config)
                                st.session_state.roadmap_result = roadmap_response.text
                            except Exception as e:
                                st.error(f"An error occurred during roadmap generation: {e}")
                    else:
                        st.warning("Please enter a Target Job Title above.")

                if st.session_state.roadmap_result:
                    st.markdown(st.session_state.roadmap_result)

            with tab3:
                st.subheader("Career Opportunity & Market Insights")
                if st.button("Find My Opportunities"):
                    if target_job:
                        with st.spinner("Scanning for career paths..."):
                            opportunity_prompt = f"""
                            You are a seasoned career strategist...
                            ---
                            {edited_text}
                            ---
                            """
                            try:
                                response = model.generate_content(opportunity_prompt, generation_config=generation_config)
                                st.session_state.opportunity_result = response.text
                            except Exception as e:
                                st.error(f"An error occurred during analysis: {e}")
                    else:
                        st.warning("Please enter a Target Job Title above.")

                if st.session_state.opportunity_result:
                    st.markdown(st.session_state.opportunity_result)

                st.divider()
                st.subheader("Job Market Future Trends")
                if st.button("Analyze Market Trends"):
                    if target_job:
                        with st.spinner(f"Analyzing future trends for a {target_job}..."):
                            trends_prompt = f"""
                            Act as a senior market analyst from Gartner providing a direct report.
                            Your task is to generate a job market trend analysis for the role of "{target_job}".

                            **Output Requirements:**
                            1.  **Executive Summary:** A concise, one-paragraph summary of the future outlook for this role.
                            2.  **Data Table:** A Markdown table with columns 'Year' and 'Demand Growth (%)', showing data for the last 3 years and a forecast for the next 3.

                            **CRITICAL RULE:** For a high-growth role like AI Engineer or Data Scientist, the numbers in the 'Demand Growth (%)' column MUST show a generally increasing trend for future years. Do not show a declining trend. All numbers must be positive.

                            **Constraint:**
                            - Do not include any conversational introductions.
                            - Your entire output must consist of only the Executive Summary and the Markdown Data Table.

                            Generate the report now.
                            """
                            try:
                                response = model.generate_content(trends_prompt, generation_config=generation_config)
                                st.session_state.trends_result = response.text
                            except Exception as e:
                                st.error(f"An error occurred during trend analysis: {e}")
                    else:
                        st.warning("Please enter a Target Job Title above.")

                if st.session_state.trends_result:
                    trends_text = st.session_state.trends_result
                    st.markdown(trends_text)
                    try:
                        table_rows = re.findall(r'\|\s*(\d{4})\s*\|\s*([\d.-]+)\s*\|', trends_text)
                        if table_rows:
                            df = pd.DataFrame(table_rows, columns=['Year', 'Demand Growth (%)'])
                            df['Demand Growth (%)'] = pd.to_numeric(df['Demand Growth (%)'])
                            df = df.set_index('Year')
                            st.line_chart(df)
                        else:
                            st.info("Could not find table data in the response to generate a graph.")
                    except Exception as e:
                        st.info("Could not generate a graph from the analysis.")
            
            with tab4:
                st.subheader("AI Cover Letter Generator")
                job_description = st.text_area("Paste the job description here")
                if st.button("Generate Cover Letter"):
                    if job_description:
                        with st.spinner("Writing a tailored cover letter..."):
                            cover_letter_prompt = f"""
                            You are a professional career writer...
                            ---
                            **User's Resume:**
                            {edited_text}
                            ---
                            **Target Job Description:**
                            {job_description}
                            ---
                            """
                            try:
                                response = model.generate_content(cover_letter_prompt, generation_config=generation_config)
                                st.session_state.cover_letter_result = response.text
                            except Exception as e:
                                st.error(f"An error occurred during cover letter generation: {e}")
                    else:
                        st.warning("Please paste a job description.")

                if st.session_state.cover_letter_result:
                    st.code(st.session_state.cover_letter_result)
                    st.download_button(
                        label="Download Cover Letter as PDF",
                        data=text_to_pdf(st.session_state.cover_letter_result),
                        file_name="cover_letter.pdf",
                        mime="application/pdf"
                    )