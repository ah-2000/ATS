1. Start Backend (Terminal 1)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

2. Start Frontend (Terminal 2)
cd frontend
npm install
npm run dev