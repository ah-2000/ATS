import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(input)
    return response.text.strip()  # Trim whitespace

def input_pdf_text(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# JSON Cleaning Function
def clean_json_response(response):
    try:
        response = response.strip("```json").strip("```").strip()
        return json.loads(response)  # Ensure it's valid JSON
    except json.JSONDecodeError:
        return None  # If parsing fails, return None

# Prompt Template (Forcing Proper JSON Output)
# Note: The {job_position} placeholder is added to reflect the selected job field.
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
    "Profile Summary": "Concise evaluation of strengths and gaps."
}}
"""

# Streamlit App Interface
st.title("💼 Smart ATS System")

# New Job Position Select Box for both technical and non-technical roles
job_position = st.selectbox("Select Job Position:", [
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
    "Customer Support"
    "Business Development Manager",
    "Marketing Specialist",
    "Sales Representative",
    "Graphic Designer",
    "Product Manager",
    "Project Manager",
    "Content Writer",
    "Financial Analyst",
    "Human Resources Manager",
])

# Job description input
jd = st.text_area("📌 Job Description:", height=200)

# Resume file uploader
uploaded_file = st.file_uploader("📂 Upload Your Resume", type="pdf", help="Upload only PDF format.")

submit = st.button("🔍 Analyze Resume")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        # Add the job_position selection into the formatted prompt
        formatted_prompt = input_prompt.format(text=text, jd=jd, job_position=job_position)
        response = get_gemini_response(formatted_prompt)

        # Parse and clean AI response
        parsed_response = clean_json_response(response)

        if parsed_response:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📌 Job Match Details")
                st.write(f"**JD Match:** `{parsed_response.get('JD Match', 'N/A')}`")
                missing_keywords = parsed_response.get("MissingKeywords", [])
                if missing_keywords:
                    st.write("🔴 **Missing Keywords:**", ", ".join(missing_keywords))
                else:
                    st.write("✅ **No Missing Keywords Found!**")

            with col2:
                st.subheader("📈 Strengths & Recommendations")
                key_strength = parsed_response.get("KeyStrength", "N/A")
                recommendations = parsed_response.get("Recommendations", "N/A")
                st.write("**Key Strength:**", key_strength)
                st.write("**Recommendations:**", recommendations)

            st.subheader("📝 **Profile Summary:**")
            profile_summary = parsed_response.get("Profile Summary", "No summary available.")
            st.info(profile_summary)
        else:
            st.error("⚠️ AI Response Formatting Error! Please try again.")
            st.write("🔍 **Possible Issue:** AI is not returning JSON correctly.")
            st.write("📌 **Suggestion:** Try modifying the job description and rerun.")
