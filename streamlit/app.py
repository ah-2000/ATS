import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
import json
import time
import pandas as pd
from dotenv import load_dotenv
from typing import Optional, Dict, List, Any
from io import BytesIO
import requests
from openai import OpenAI
from anthropic import Anthropic
import cv_enhancer

load_dotenv()  # Load environment variables

# ============================================
# MULTI-MODEL CONFIGURATION
# ============================================

# Load API keys and configurations
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://192.168.18.8:11434")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Initialize clients
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Model availability status
MODEL_STATUS = {
    "Ollama (Llama)": {"available": False, "models": []},
    "Google Gemini": {"available": bool(GOOGLE_API_KEY), "models": ["gemini-2.0-flash", "gemini-1.5-pro"]},
    "OpenAI GPT": {"available": bool(OPENAI_API_KEY), "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]},
    "Anthropic Claude": {"available": bool(ANTHROPIC_API_KEY), "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"]}
}

# Check Ollama availability
try:
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
    if response.status_code == 200:
        ollama_models = [model["name"] for model in response.json().get("models", [])]
        if ollama_models:
            MODEL_STATUS["Ollama (Llama)"]["available"] = True
            MODEL_STATUS["Ollama (Llama)"]["models"] = ollama_models
except:
    pass  # Ollama not available

# ============================================
# HELPER FUNCTIONS (with Type Hints)
# ============================================

def get_ollama_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from Ollama API."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"Ollama API call failed after {max_retries} attempts: {str(e)}")


def get_gemini_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from Gemini API with retry mechanism."""
    gemini_model = genai.GenerativeModel(model)
    
    for attempt in range(max_retries):
        try:
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"Gemini API call failed after {max_retries} attempts: {str(e)}")


def get_openai_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from OpenAI API."""
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"OpenAI API call failed after {max_retries} attempts: {str(e)}")


def get_claude_response(prompt: str, model: str, max_retries: int = 3) -> str:
    """Get response from Anthropic Claude API."""
    client = Anthropic(api_key=ANTHROPIC_API_KEY)
    
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            else:
                raise Exception(f"Claude API call failed after {max_retries} attempts: {str(e)}")


def get_ai_response(prompt: str, provider: str, model: str, max_retries: int = 3) -> str:
    """
    Unified function to get AI response from any provider.
    
    Args:
        prompt: The input prompt for the model
        provider: AI provider name (e.g., "Ollama (Llama)", "Google Gemini")
        model: Specific model to use
        max_retries: Maximum number of retry attempts
    
    Returns:
        The model's response text
    """
    if provider == "Ollama (Llama)":
        return get_ollama_response(prompt, model, max_retries)
    elif provider == "Google Gemini":
        return get_gemini_response(prompt, model, max_retries)
    elif provider == "OpenAI GPT":
        return get_openai_response(prompt, model, max_retries)
    elif provider == "Anthropic Claude":
        return get_claude_response(prompt, model, max_retries)
    else:
        raise Exception(f"Unknown provider: {provider}")


def input_pdf_text(uploaded_file) -> str:
    """Extract text from uploaded PDF file."""
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")
        return ""
    return text


def input_docx_text(uploaded_file) -> str:
    """Extract text from uploaded DOCX file."""
    try:
        from docx import Document
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text
    except Exception as e:
        st.error(f"❌ Error reading DOCX: {str(e)}")
        return ""


def get_file_text(uploaded_file) -> str:
    """Extract text from uploaded file (PDF or DOCX)."""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    if file_extension == 'pdf':
        return input_pdf_text(uploaded_file)
    elif file_extension == 'docx':
        return input_docx_text(uploaded_file)
    else:
        st.error(f"❌ Unsupported file type: {file_extension}")
        return ""


def clean_json_response(response: str) -> Optional[Dict[str, Any]]:
    """Parse and clean AI response to extract JSON."""
    try:
        # Remove markdown code blocks if present
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        return json.loads(response)
    except json.JSONDecodeError:
        return None


def extract_match_percentage(match_str: str) -> int:
    """Extract numeric percentage from JD Match string."""
    try:
        return int(''.join(filter(str.isdigit, match_str)))
    except:
        return 0


def get_match_color(percentage: int) -> str:
    """Return color based on match percentage."""
    if percentage >= 80:
        return "🟢"
    elif percentage >= 60:
        return "🟡"
    elif percentage >= 40:
        return "🟠"
    else:
        return "🔴"


def results_to_dataframe(results: List[Dict]) -> pd.DataFrame:
    """Convert analysis results to a pandas DataFrame for export."""
    rows = []
    for result in results:
        row = {
            "File Name": result.get("filename", "N/A"),
            "JD Match": result.get("JD Match", "N/A"),
            "Missing Keywords": ", ".join(result.get("MissingKeywords", [])),
            "Key Strength": result.get("KeyStrength", "N/A"),
            "Recommendations": result.get("Recommendations", "N/A"),
            "Profile Summary": result.get("Profile Summary", "N/A"),
            "Experience Match": result.get("ExperienceMatch", "N/A"),
            "Skills Match": result.get("SkillsMatch", "N/A"),
            "Education Match": result.get("EducationMatch", "N/A"),
        }
        rows.append(row)
    return pd.DataFrame(rows)


# ============================================
# ENHANCED PROMPT TEMPLATE
# ============================================
input_prompt = """
Hey, act like a skilled and experienced ATS (Application Tracking System) with deep understanding of both technical and non-technical fields.
Your task is to evaluate the resume based on the given job description for the job position "{job_position}".
You must consider the job market is very competitive and provide the best assistance for improving resumes.
Assign the percentage matching based on the job description and list the missing keywords with high accuracy.
Evaluate the resume while ignoring name, gender, and age.

**Requirements:**
- Assign a JD match percentage (accurate score).
- Highlight missing skills (only relevant ones).
- Extract Key Strengths and provide Recommendations.
- Ensure the response **always contains** a "Profile Summary".
- Provide weighted scoring breakdown.

**Input:**
Job Position: {job_position}
Resume: {text}
Job Description: {jd}

**Return Response in Strict JSON Format:**
{{
    "JD Match": "XX%",
    "MissingKeywords": ["Skill1", "Skill2", "Skill3"],
    "KeyStrength": "Brief summary of key strengths",
    "Recommendations": "Brief recommendations for improvement",
    "Profile Summary": "Concise evaluation of strengths and gaps.",
    "ExperienceMatch": "XX%",
    "SkillsMatch": "XX%",
    "EducationMatch": "XX%"
}}
"""

# ============================================
# STREAMLIT APP INTERFACE
# ============================================
st.set_page_config(page_title="Smart ATS System", page_icon="💼", layout="wide")

# ============================================
# MODEL SELECTION SIDEBAR
# ============================================
st.sidebar.title("🤖 AI Model Selection")

# Check if any models are available
available_providers = [provider for provider, status in MODEL_STATUS.items() if status["available"]]

if not available_providers:
    st.sidebar.error("❌ No AI models available!")
    st.sidebar.info("Please configure at least one API key in your `.env` file or ensure Ollama is running.")
    st.error("❌ **No AI models available!** Please configure API keys or start Ollama server.")
    st.stop()

# Provider selection
selected_provider = st.sidebar.selectbox(
    "Select AI Provider:",
    options=available_providers,
    help="Choose your preferred AI model provider"
)

# Model selection based on provider
available_models = MODEL_STATUS[selected_provider]["models"]
selected_model = st.sidebar.selectbox(
    "Select Model:",
    options=available_models,
    help=f"Choose a specific {selected_provider} model"
)

# Show provider status
st.sidebar.divider()
st.sidebar.markdown("### 📊 Provider Status")
for provider, status in MODEL_STATUS.items():
    if status["available"]:
        st.sidebar.success(f"✅ {provider}")
    else:
        st.sidebar.error(f"❌ {provider}")

st.sidebar.divider()
st.sidebar.markdown(f"**Current Selection:**\n- Provider: `{selected_provider}`\n- Model: `{selected_model}`")

st.title("💼 Smart ATS System")
st.markdown("*Analyze your resume against job descriptions with AI-powered insights*")

st.divider()

# ============================================
# JOB POSITION SELECTION (with Custom Option)
# ============================================
job_positions = [
    "Software Engineer",
    "Data Analyst",
    "Data Engineer",
    "Machine Learning Engineer",
    "Full Stack Developer (MERN)",
    "Full Stack Developer (MEAN)",
    "Frontend Developer",
    "Backend Developer",
    "DevOps Engineer",
    "Cloud Solutions Architect",
    "Artificial Intelligence Engineer",
    "Deep Learning Engineer",
    "Computer Vision Engineer",
    "Big Data Engineer",
    "Network Engineer",
    "Cybersecurity Engineer",
    "IT Support Specialist",
    "Technical Support Specialist",
    "Cybersecurity Analyst",
    "Ethical Hacker/Penetration Tester",
    "Mobile App Developer",
    "Blockchain Developer",
    "Data Scientist",
    "UI/UX Designer",
    "Customer Support",
    "Business Development Manager",
    "Marketing Specialist",
    "Sales Representative",
    "Graphic Designer",
    "Product Manager",
    "Project Manager",
    "Content Writer",
    "Financial Analyst",
    "Human Resources Manager",
    "Other (Custom)",  # Quick Fix #4
]

col_job, col_custom = st.columns([2, 1])

with col_job:
    selected_position = st.selectbox("🎯 Select Job Position:", job_positions)

with col_custom:
    if selected_position == "Other (Custom)":
        custom_position = st.text_input("✏️ Enter Custom Position:", placeholder="e.g., QA Engineer")
        job_position = custom_position if custom_position else "Not Specified"
    else:
        job_position = selected_position
        st.markdown("")  # Spacer

# Job description input
jd = st.text_area("📌 Job Description:", height=150, placeholder="Paste the job description here...")

# ============================================
# MULTI-FILE RESUME UPLOAD (High Priority #1)
# ============================================
st.markdown("### 📂 Upload Resume(s)")
uploaded_files = st.file_uploader(
    "Upload one or more PDF or DOCX resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    help="You can upload multiple resumes (PDF or DOCX) for batch analysis"
)

if uploaded_files:
    st.info(f"📄 **{len(uploaded_files)}** resume(s) uploaded and ready for analysis")

submit = st.button("🔍 Analyze Resume(s)", type="primary", use_container_width=True)

# ============================================
# INPUT VALIDATION (Quick Fix #1)
# ============================================
if submit:
    # Validation checks
    has_error = False
    
    if not jd.strip():
        st.warning("⚠️ Please enter a job description!")
        has_error = True
    
    if not uploaded_files:
        st.warning("⚠️ Please upload at least one resume!")
        has_error = True
    
    if selected_position == "Other (Custom)" and not custom_position.strip():
        st.warning("⚠️ Please enter a custom job position!")
        has_error = True
    
    if not has_error:
        # Initialize session state for storing results
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = []
        if 'uploaded_file_data' not in st.session_state:
            st.session_state.uploaded_file_data = {}
        
        # Store all results for export
        all_results = []
        
        # ============================================
        # LOADING SPINNER (Quick Fix #3)
        # ============================================
        with st.spinner(f"🔄 Analyzing {len(uploaded_files)} resume(s)... This may take a moment."):
            
            for idx, uploaded_file in enumerate(uploaded_files):
                st.markdown(f"---")
                st.subheader(f"📄 Results for: `{uploaded_file.name}`")
                
                # Extract text from PDF or DOCX
                text = get_file_text(uploaded_file)
                
                if not text.strip():
                    st.error(f"❌ Could not extract text from {uploaded_file.name}. Please check if it's a valid file.")
                    continue
                
                # Store file data for enhancement later
                uploaded_file.seek(0)
                file_bytes = BytesIO(uploaded_file.read())
                file_extension = uploaded_file.name.split('.')[-1].lower()
                st.session_state.uploaded_file_data[uploaded_file.name] = {
                    'bytes': file_bytes,
                    'type': file_extension
                }
                
                # Format prompt and get response
                formatted_prompt = input_prompt.format(text=text, jd=jd, job_position=job_position)
                
                try:
                    response = get_ai_response(formatted_prompt, selected_provider, selected_model)
                    parsed_response = clean_json_response(response)
                    
                    if parsed_response:
                        # Add filename for export
                        parsed_response["filename"] = uploaded_file.name
                        all_results.append(parsed_response)
                        
                        # ============================================
                        # SKILL GAP VISUALIZATION (High Priority #3)
                        # ============================================
                        jd_match = parsed_response.get('JD Match', '0%')
                        match_percentage = extract_match_percentage(jd_match)
                        match_color = get_match_color(match_percentage)
                        
                        # Main match score with progress bar
                        st.markdown(f"### {match_color} Overall JD Match: **{jd_match}**")
                        st.progress(match_percentage / 100)
                        
                        # Weighted scoring breakdown
                        score_cols = st.columns(3)
                        
                        with score_cols[0]:
                            exp_match = parsed_response.get("ExperienceMatch", "N/A")
                            exp_pct = extract_match_percentage(exp_match)
                            st.metric("📊 Experience", exp_match)
                            if exp_pct > 0:
                                st.progress(exp_pct / 100)
                        
                        with score_cols[1]:
                            skills_match = parsed_response.get("SkillsMatch", "N/A")
                            skills_pct = extract_match_percentage(skills_match)
                            st.metric("🛠️ Skills", skills_match)
                            if skills_pct > 0:
                                st.progress(skills_pct / 100)
                        
                        with score_cols[2]:
                            edu_match = parsed_response.get("EducationMatch", "N/A")
                            edu_pct = extract_match_percentage(edu_match)
                            st.metric("🎓 Education", edu_match)
                            if edu_pct > 0:
                                st.progress(edu_pct / 100)
                        
                        st.markdown("")
                        
                        # Details in columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 🔴 Missing Keywords")
                            missing_keywords = parsed_response.get("MissingKeywords", [])
                            if missing_keywords:
                                for kw in missing_keywords:
                                    st.markdown(f"- `{kw}`")
                            else:
                                st.success("✅ No critical keywords missing!")
                        
                        with col2:
                            st.markdown("#### 💪 Key Strength")
                            st.write(parsed_response.get("KeyStrength", "N/A"))
                            
                            st.markdown("#### 💡 Recommendations")
                            st.write(parsed_response.get("Recommendations", "N/A"))
                        
                        # Profile Summary
                        st.markdown("#### 📝 Profile Summary")
                        st.info(parsed_response.get("Profile Summary", "No summary available."))
                        
                    else:
                        st.error(f"⚠️ AI Response Formatting Error for {uploaded_file.name}!")
                        st.write("🔍 **Possible Issue:** AI is not returning JSON correctly.")
                        st.write("📌 **Suggestion:** Try modifying the job description and rerun.")
                        
                except Exception as e:
                    st.error(f"❌ Error analyzing {uploaded_file.name}: {str(e)}")
        
        # ============================================
        # EXPORT FUNCTIONALITY (High Priority #2)
        # ============================================
        if all_results:
            st.divider()
            st.subheader("📥 Export Results")
            
            df = results_to_dataframe(all_results)
            
            # CSV Export
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                st.download_button(
                    label="📊 Download as CSV",
                    data=csv_data,
                    file_name="ats_analysis_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_export2:
                # JSON Export
                json_data = json.dumps(all_results, indent=2)
                st.download_button(
                    label="📋 Download as JSON",
                    data=json_data,
                    file_name="ats_analysis_results.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # ============================================
            # CV ENHANCEMENT FEATURE
            # ============================================
            st.divider()
            st.subheader("✨ CV Enhancement")
            st.info("💡 **Auto-enhance your CV** - Apply AI-recommended improvements while preserving your original formatting!")
            
            # Store results in session state for enhancement
            st.session_state.analysis_results = all_results
            st.session_state.job_description = jd
            st.session_state.job_position = job_position
            st.session_state.selected_provider = selected_provider
            st.session_state.selected_model = selected_model
            
            # Show summary table
            st.markdown("### 📊 Summary Table")
            st.dataframe(df[["File Name", "JD Match", "Experience Match", "Skills Match", "Education Match"]], use_container_width=True)

# ============================================
# CV ENHANCEMENT SECTION (OUTSIDE SUBMIT BLOCK)
# ============================================
# This section persists after analysis is complete
if 'analysis_results' in st.session_state and st.session_state.analysis_results:
    all_results = st.session_state.analysis_results
    
    st.divider()
    st.subheader("✨ Enhance Your CV")
    
    # Select which CV to enhance
    if len(all_results) == 1:
        selected_cv_name = all_results[0]["filename"]
        st.write(f"📄 Ready to enhance: **{selected_cv_name}**")
    else:
        cv_names = [result["filename"] for result in all_results]
        selected_cv_name = st.selectbox("Select CV to enhance:", cv_names, key="cv_select")
    
    # Check if file data is available
    if 'uploaded_file_data' in st.session_state and selected_cv_name in st.session_state.uploaded_file_data:
        # Enhancement button
        enhance_button = st.button("✨ Enhance Selected CV", type="primary", use_container_width=True)
        
        if enhance_button:
            file_data = st.session_state.uploaded_file_data[selected_cv_name]
            
            # Find the analysis result for this CV
            cv_analysis = next((r for r in all_results if r["filename"] == selected_cv_name), None)
            
            if cv_analysis:
                with st.spinner(f"✨ Enhancing {selected_cv_name}... This may take a moment."):
                    # Reset file pointer
                    file_data['bytes'].seek(0)
                    
                    # Call enhancement function
                    enhanced_bytes, status_msg, enhancement_data = cv_enhancer.enhance_cv(
                        file_bytes=file_data['bytes'],
                        file_type=file_data['type'],
                        job_description=st.session_state.get('job_description', ''),
                        job_position=st.session_state.get('job_position', ''),
                        analysis_result=cv_analysis,
                        ai_response_func=get_ai_response,
                        provider=st.session_state.get('selected_provider', selected_provider),
                        model=st.session_state.get('selected_model', selected_model)
                    )
                    
                    if enhanced_bytes:
                        st.success(f"✅ {status_msg}")
                        
                        # Store enhanced data in session state
                        st.session_state.enhanced_cv_bytes = enhanced_bytes
                        st.session_state.enhancement_data = enhancement_data
                        st.session_state.enhanced_filename = selected_cv_name.replace(
                            f'.{file_data["type"]}', f'_Enhanced.{file_data["type"]}'
                        )
                        st.session_state.enhanced_file_type = file_data['type']
                    else:
                        st.error(f"❌ {status_msg}")
            else:
                st.error("❌ Analysis result not found for selected CV")
    else:
        st.warning("⚠️ Please analyze a CV first to enable enhancement.")

# Show enhancement results if available
if 'enhanced_cv_bytes' in st.session_state and st.session_state.enhanced_cv_bytes:
    st.divider()
    st.subheader("📥 Download Enhanced CV")
    
    enhancement_data = st.session_state.get('enhancement_data', {})
    
    # Show enhancement details
    if enhancement_data and "enhancements" in enhancement_data:
        with st.expander("📝 View Improvements Made", expanded=False):
            for idx, enh in enumerate(enhancement_data["enhancements"], 1):
                st.markdown(f"**{idx}. {enh.get('section', 'General')}**")
                col_before, col_after = st.columns(2)
                with col_before:
                    st.markdown("**Before:**")
                    original_text = enh.get('original', '')
                    st.text(original_text[:200] + "..." if len(original_text) > 200 else original_text)
                with col_after:
                    st.markdown("**After:**")
                    improved_text = enh.get('improved', '')
                    st.text(improved_text[:200] + "..." if len(improved_text) > 200 else improved_text)
                st.caption(f"💡 {enh.get('reason', '')}")
                st.markdown("---")
    
    # Download button
    file_extension = st.session_state.get('enhanced_file_type', 'docx')
    enhanced_filename = st.session_state.get('enhanced_filename', 'enhanced_cv.docx')
    
    st.session_state.enhanced_cv_bytes.seek(0)
    st.download_button(
        label=f"📥 Download Enhanced CV ({file_extension.upper()})",
        data=st.session_state.enhanced_cv_bytes.getvalue(),
        file_name=enhanced_filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if file_extension == "docx" else "application/pdf",
        type="primary",
        use_container_width=True
    )
    
    # Clear button
    if st.button("🔄 Clear and Start Over", use_container_width=True):
        for key in ['enhanced_cv_bytes', 'enhancement_data', 'enhanced_filename', 'enhanced_file_type']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown(
    f"""
    <div style='text-align: center; color: gray;'>
        💼 Smart ATS System | Powered by {selected_provider} ({selected_model})
    </div>
    """,
    unsafe_allow_html=True
)