import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from pdf_tools import DocumentToolSystem
from agent import PDFQuestionAnsweringAgent

app = FastAPI(
    title="PDF Q&A Agent API",
    description="FastAPI service for uploading PDFs and answering questions using Gemini Function Calling.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Shared in-memory instances
tool_system = DocumentToolSystem()
agent = None

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    call_count: int
    trace: list

@app.get("/")
def read_root():
    return {"message": "PDF Q&A Agent API is running."}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads a PDF file, loads it into the document tool system, and initializes the agent."""
    global agent

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        doc_id = "doc_1"
        
        tool_system.load_pdf_from_bytes(
            doc_id=doc_id,
            file_bytes=content,
            filename=file.filename
        )

        # Initialize Agent with max_calls=6
        agent = PDFQuestionAnsweringAgent(tools_system=tool_system, max_calls=6)

        return {
            "status": "success",
            "filename": file.filename,
            "message": f"Successfully loaded '{file.filename}'. You can now query the agent."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """Processes a user question about the uploaded document using the QA Agent."""
    global agent

    if agent is None:
        raise HTTPException(
            status_code=400, 
            detail="No document loaded. Please upload a PDF file via /upload-pdf first."
        )

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query string cannot be empty.")

    try:
        result = agent.run(request.query)
        return QueryResponse(
            answer=result["answer"],
            call_count=result["call_count"],
            trace=result["trace"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {str(e)}")