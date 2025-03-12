import streamlit as st
import google.generativeai as genai
import os
import pdfplumber
import json
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input):
    model = genai.GenerativeModel('gemini-1.5-pro')
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
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, 
data analyst, and big data engineering, Machine Learning, Cloud Computing, DevOps, Artificial Intelligence,
generative AI, and Deep Learning. Your task is to evaluate the resume 
based on the given job description. You must consider the job market is very 
competitive and you should provide the best assistance for improving the resumes. 
Assign the percentage matching based on JD and list the missing keywords with high accuracy.
Evaluate the resume against the job description with **high accuracy** while ignoring name, gender, and age.

**Requirements:**
- Assign a JD match percentage (accurate score).
- Highlight missing skills (only relevant ones).
- Ensure the response **always contains** a "Profile Summary".

**Input:**
resume: {text}
job description: {jd}

**Return Response in Strict JSON Format:**
{{
    "JD Match": "XX%",
    "MissingKeywords": ["Skill1", "Skill2", "Skill3"],
    "Profile Summary": "Concise evaluation of strengths and gaps."
}}
"""



# Streamlit App Interface
st.title("💼 Smart ATS System")

jd = st.text_area("📌 Job Description:")
uploaded_file = st.file_uploader("📂 Upload Your Resume", type="pdf", help="Upload only PDF format.")

submit = st.button("🔍 Analyze Resume")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        formatted_prompt = input_prompt.format(text=text, jd=jd)
        response = get_gemini_response(formatted_prompt)

        # Parse and clean AI response
        parsed_response = clean_json_response(response)

        if parsed_response:
            st.subheader("📊 Resume Analysis Report")

            # JD Match Percentage
            st.write(f"**📌 JD Match:** `{parsed_response.get('JD Match', 'N/A')}`")

            # Missing Keywords
            missing_keywords = parsed_response.get("MissingKeywords", [])
            if missing_keywords:
                st.write("🔴 **Missing Keywords:**", ", ".join(missing_keywords))
            else:
                st.write("✅ **No Missing Keywords Found!**")

            # **Ensure "Profile Summary" Always Shows**
            st.write("📝 **Profile Summary:**")
            profile_summary = parsed_response.get("Profile Summary", "No summary available.")
            st.info(profile_summary)

        else:
            st.error("⚠️ AI Response Formatting Error! Please try again.")
            st.write("🔍 **Possible Issue:** AI is not returning JSON correctly.")
            st.write("📌 **Suggestion:** Try modifying the job description and rerun.")
