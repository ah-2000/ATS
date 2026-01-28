# Streamlit ATS Application

This folder contains the legacy Streamlit-based version of the Smart ATS System.

## Files

- **app.py** - Main Streamlit application with CV analysis functionality
- **cv_enhancer.py** - CV enhancement module with formatting preservation
- **requirements.txt** - Python dependencies for Streamlit app
- **.env** - Environment variables (API keys)
- **.env.example** - Example environment configuration

## Features

- Multi-model AI support (Ollama, Google Gemini, OpenAI GPT, Anthropic Claude)
- CV analysis against job descriptions
- Batch resume processing
- CV enhancement with formatting preservation
- Export results to CSV/JSON
- Support for PDF and DOCX files

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure API keys in `.env` file:
   ```
   GOOGLE_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   OLLAMA_BASE_URL=http://localhost:11434
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Migration Note

This is the original Streamlit version. The project has been migrated to a modern Next.js frontend with FastAPI backend (see `../frontend` and `../backend` folders).

The Streamlit version is kept for:
- Reference purposes
- Quick local testing
- Users who prefer the Streamlit interface

## Differences from Next.js Version

| Feature | Streamlit | Next.js/FastAPI |
|---------|-----------|-----------------|
| UI Framework | Streamlit | Next.js + React |
| Backend | Integrated | Separate FastAPI |
| Deployment | Single app | Frontend + Backend |
| Dark Mode | ❌ | ✅ |
| Modern UI | Basic | Professional |
| API Structure | Monolithic | RESTful API |

## Usage

1. Select your AI provider and model from the sidebar
2. Choose or enter a job position
3. Paste the job description
4. Upload one or more resumes (PDF/DOCX)
5. Click "Analyze Resume(s)"
6. View detailed analysis results
7. Optionally enhance your CV with AI suggestions
8. Export results as CSV or JSON

## Support

For issues or questions about the Streamlit version, please refer to the main project README or create an issue in the repository.
