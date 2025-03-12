# ATS
This code is a Smart ATS (Application Tracking System) built using Streamlit and Google Gemini AI. It helps job seekers analyze their resumes against a given job description (JD) and provides feedback on how well they match the job.

Step-by-Step Explanation:
Importing Necessary Tools

The code imports libraries like streamlit (to create a web app), google.generativeai (to use Gemini AI), pdfplumber (to read PDFs), and dotenv (to load secret API keys from a .env file).
The Google API key is loaded securely from a .env file.
Setting Up AI Model

The AI model (gemini-1.5-pro) is configured to process the input and generate a response.
Reading the Resume (PDF File)

When a user uploads a PDF resume, the code extracts the text from it using pdfplumber.
Defining the AI Prompt

A structured prompt is prepared for the AI.
It tells the AI to act like an experienced ATS and analyze resumes based on different tech fields like Software Engineering, Data Science, AI, DevOps, etc.
The AI must return a percentage match, list of missing keywords, and a profile summary in JSON format.
Creating the Web App Interface

The Streamlit library is used to create a user-friendly web interface:
A text area for the job description.
A file uploader to upload the resume (only in PDF format).
A submit button to start the analysis.
Processing and Displaying Results

When the user clicks the Analyze Resume button:
The resume text and job description are sent to the AI.
The AI returns a JSON response with a match percentage, missing keywords, and a profile summary.
The JSON is cleaned and formatted before displaying results.
Handling Errors

If the AI does not return a proper response, an error message is shown.
Users are advised to modify their job description and try again.
