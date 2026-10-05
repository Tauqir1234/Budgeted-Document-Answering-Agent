import fitz  # PyMuPDF

class DocumentToolSystem:
    def __init__(self):
        self.documents = {}

    def load_pdf_from_bytes(self, doc_id: str, file_bytes: bytes, filename: str):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        self.documents[doc_id] = {
            "fitz_doc": doc,
            "filename": filename,
            "num_pages": len(doc)
        }

    def list_documents(self) -> list[dict]:
        """Returns metadata for all loaded documents."""
        res = []
        for doc_id, data in self.documents.items():
            res.append({
                "doc_id": doc_id,
                "title": data["filename"],
                "num_pages": data["num_pages"]
            })
        return res

    def list_headings(self, doc_id: str) -> list[dict]:
        """Returns Table of Contents / Outline headings if present."""
        if doc_id not in self.documents:
            raise ValueError(f"Document ID '{doc_id}' not found.")
        doc = self.documents[doc_id]["fitz_doc"]
        toc = doc.get_toc()  # Returns list of [level, title, page_number]
        return [{"level": item[0], "title": item[1], "page": item[2]} for item in toc]

    def search_keyword(self, doc_id: str, keyword: str) -> list[int]:
        """Searches for keywords or phrases with multi-word and case-insensitive fallbacks."""
        if doc_id not in self.documents:
            raise ValueError(f"Document ID '{doc_id}' not found.")

        doc = self.documents[doc_id]["fitz_doc"]
        matching_pages = set()
        
        clean_keyword = keyword.strip().lower()

        # Strategy 1: Exact match search via PyMuPDF
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").lower()
            
            # Normalize whitespace to catch line-break matches
            normalized_text = " ".join(text.split())
            if clean_keyword in normalized_text:
                matching_pages.add(page_num + 1)

        # Strategy 2: If multi-word search yields nothing, search for main key words
        if not matching_pages and " " in clean_keyword:
            words = [w for w in clean_keyword.split() if len(w) > 2 and w not in ["and", "the", "for", "with", "from"]]
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = " ".join(page.get_text("text").lower().split())
                if any(word in text for word in words):
                    matching_pages.add(page_num + 1)

        return sorted(list(matching_pages))

    def get_page(self, doc_id: str, page_number: int) -> str:
        """Fetches full text content of a specific page (1-indexed)."""
        if doc_id not in self.documents:
            raise ValueError(f"Document ID '{doc_id}' not found.")

        doc = self.documents[doc_id]["fitz_doc"]
        if page_number < 1 or page_number > len(doc):
            return f"Error: Page number {page_number} out of range (1 - {len(doc)})."

        return doc[page_number - 1].get_text("text")