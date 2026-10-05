<div align="center">

# 📄 PDF Agent

An AI-powered PDF assistant built with **FastAPI** and the **Google Gemini API**.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?logo=googlegemini&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?logo=gunicorn&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white)

</div>

Upload a PDF, ask questions in plain language, and the agent decides which tools to call (read pages, search text, summarize, etc.) to answer you, with a full trace of every step it took.

## ✨ Features

- **Agentic tool use**: Gemini function calling picks and runs PDF tools on its own
- **Transparent reasoning**: every response returns the answer, a tool-call trace, and the call count
- **PDF tools**: text extraction, page-level reading, and search (see `backend/pdf_tools.py`)
- **Request logging**: structured logs via `logger.py`
- **Simple UI**: frontend in `frontend/app.py` that talks to the API

## 🏛️ Architecture

<img width="1266" height="522" alt="image" src="https://github.com/user-attachments/assets/66d27c39-f488-43a2-95a4-ffc755e7ddf0" />


## 🧰 Tech Stack

<p align="left">
  <a href="https://www.python.org" target="_blank">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" alt="Python" width="48" height="48"/>
  </a>
  <a href="https://fastapi.tiangolo.com" target="_blank">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="48" height="48"/>
  </a>
  <a href="https://streamlit.io" target="_blank">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/streamlit/streamlit-original.svg" alt="Streamlit" width="48" height="48"/>
  </a>
  <a href="https://git-scm.com" target="_blank">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" alt="Git" width="48" height="48"/>
  </a>
  <a href="https://github.com" target="_blank">
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" alt="GitHub" width="48" height="48"/>
  </a>
</p>

- Python 3.10+
- FastAPI + Uvicorn
- Google Gemini API
- Streamlit (frontend)

## 🗂️ Project Structure

```
pdf-agent/
├── backend/
│   ├── main.py           # FastAPI app and API endpoints
│   ├── agent.py          # Gemini agent loop (function calling + trace tracking)
│   ├── pdf_tools.py      # Tools the agent can call on PDFs
│   ├── logger.py         # Logging setup
│   └── requirements.txt
├── frontend/
│   └── app.py            # User interface
├── docs/
│   └── architecture.png  # Architecture diagram
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/pdf-agent.git
cd pdf-agent
```

### 2. Set up the backend

```bash
cd backend
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and add your key (get one from [Google AI Studio](https://aistudio.google.com/app/apikey)):

```env
GEMINI_API_KEY=your_key_here
```

> ⚠️ Never commit your `.env` file.

### 4. Check available models (optional)

```bash
python check_models.py
```

### 5. Run the backend

```bash
uvicorn main:app --reload
```

API runs at `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`.

### 6. Run the frontend

In a second terminal:

```bash
cd frontend
streamlit run app.py
```

If your frontend points to the backend URL, make sure it matches where the API is running.

## 📡 API Response Format

The agent returns:

```json
{
  "answer": "The final answer from the agent",
  "trace": ["...each tool call and result..."],
  "call_count": 3
}
```

## ☁️ Deployment

| Part | Suggested host | Notes |
|------|----------------|-------|
| Backend | Render / Railway | Root dir `backend`, build `pip install -r requirements.txt`, start `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Streamlit Community Cloud | Set the backend URL to your deployed API |

Add `GEMINI_API_KEY` as an environment variable on the hosting platform. Do not hardcode it.


