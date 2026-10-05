import sys
from pathlib import Path
from pdf_tools import DocumentToolSystem
from logger import CallBudgetTracker, BudgetExceededError

# Absolute path to your downloaded PDF
PDF_FILENAME = r"c:\Users\admin\Downloads\CSCI415009_V2.pdf"

pdf_path = Path(PDF_FILENAME)

print(f"--- 1. CHECKING PDF FILE LOCATION ---", flush=True)
print(f"Target path: {pdf_path}", flush=True)

if not pdf_path.exists():
    print(f"\n[ERROR] PDF file '{PDF_FILENAME}' not found!", flush=True)
    sys.exit(1)

tools = DocumentToolSystem()
tracker = CallBudgetTracker(tools, max_calls=6)

print("\n--- 2. LOADING PDF INTO TOOL SYSTEM ---", flush=True)
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

tools.load_pdf_from_bytes(doc_id="doc_1", file_bytes=pdf_bytes, filename=pdf_path.name)
print("PDF loaded successfully!", flush=True)

print("\n--- 3. TESTING TOOL CALLS AGAINST PDF ---", flush=True)

try:
    docs = tracker.execute_tool("list_documents")
    print(f"Call 1 (list_documents):\n  {docs}\n", flush=True)

    headings = tracker.execute_tool("list_headings", doc_id="doc_1")
    print(f"Call 2 (list_headings):\n  Found {len(headings)} headings. Preview: {headings[:3]}\n", flush=True)

    search_term = "the"
    matching_pages = tracker.execute_tool("search_keyword", doc_id="doc_1", keyword=search_term)
    print(f"Call 3 (search_keyword '{search_term}'):\n  Matching pages: {matching_pages}\n", flush=True)

    page_1_text = tracker.execute_tool("get_page", doc_id="doc_1", page_number=1)
    print(f"Call 4 (get_page 1):\n  Text preview (first 200 chars):\n  \"{page_1_text[:200]}...\"\n", flush=True)

    print(f"Total budget used: {tracker.call_count}/6 calls.", flush=True)

except Exception as e:
    print(f"Tool execution failed: {e}", flush=True)

print("\n--- 4. TOOL CALL TRACE ---", flush=True)
for entry in tracker.trace:
    print(entry, flush=True)