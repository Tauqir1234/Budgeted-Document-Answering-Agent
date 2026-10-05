import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

from pdf_tools import DocumentToolSystem
from agent import PDFQuestionAnsweringAgent

PDF_FILENAME = r"c:\Users\admin\Downloads\CSCI415009_V2.pdf"
pdf_path = Path(PDF_FILENAME)

# 1. Initialize tool system and load PDF
tools = DocumentToolSystem()
with open(pdf_path, "rb") as f:
    tools.load_pdf_from_bytes(doc_id="doc_1", file_bytes=f.read(), filename=pdf_path.name)

# 2. Instantiate Agent
agent = PDFQuestionAnsweringAgent(tools_system=tools, max_calls=6)

# 3. Test Query
query = "What is discussed in section 1.1 of the document?"
print(f"User Query: {query}\n" + "="*50)

result = agent.run(query)

print("\n--- FINAL ANSWER ---")
print(result["answer"])

print(f"\n--- TOOL CALL TRACE ({result['call_count']}/6 calls used) ---")
for entry in result["trace"]:
    print(entry)