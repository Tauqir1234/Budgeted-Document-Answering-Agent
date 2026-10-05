import time
from google import genai
from google.genai import types, errors
from pdf_tools import DocumentToolSystem
from logger import CallBudgetTracker, BudgetExceededError

class PDFQuestionAnsweringAgent:
    def __init__(self, tools_system: DocumentToolSystem, max_calls: int = 6):
        # Strict limit of 6 tool calls per query
        self.tracker = CallBudgetTracker(tools_system, max_calls=max_calls)
        self.client = genai.Client()
        
        self.primary_model = "gemini-3.5-flash-lite"
        self.fallback_models = ["gemini-3.5-flash", "gemini-3.1-pro-preview"]

    def _get_tool_declarations(self):
        """Define function schemas for Gemini Function Calling."""
        return [
            types.FunctionDeclaration(
                name="list_documents",
                description="Returns metadata for all loaded documents (doc_id, title, page count).",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={}
                )
            ),
            types.FunctionDeclaration(
                name="list_headings",
                description="Returns table of contents/headings for a given document.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "doc_id": types.Schema(type=types.Type.STRING, description="Document ID")
                    },
                    required=["doc_id"]
                )
            ),
            types.FunctionDeclaration(
                name="search_keyword",
                description="Searches for a keyword in the document and returns matching page numbers.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "doc_id": types.Schema(type=types.Type.STRING, description="Document ID"),
                        "keyword": types.Schema(type=types.Type.STRING, description="Keyword/term to search")
                    },
                    required=["doc_id", "keyword"]
                )
            ),
            types.FunctionDeclaration(
                name="get_page",
                description="Fetches full text content for a specific page number.",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "doc_id": types.Schema(type=types.Type.STRING, description="Document ID"),
                        "page_number": types.Schema(type=types.Type.INTEGER, description="1-indexed page number")
                    },
                    required=["doc_id", "page_number"]
                )
            )
        ]

    def _generate_content_with_retry(self, contents, config):
        models_to_try = [self.primary_model] + self.fallback_models

        for model in models_to_try:
            for attempt in range(3):
                try:
                    return self.client.models.generate_content(
                        model=model,
                        contents=contents,
                        config=config
                    )
                except errors.ServerError:
                    time.sleep(3)
                    continue
                except errors.ClientError as e:
                    if e.code in (429, 404):
                        break
                    break

        raise RuntimeError("All configured Gemini models failed. Please verify API rate limits or try again shortly.")

    def run(self, user_query: str) -> dict:
        # CRITICAL FIX 1: Always reset call counter and trace per query
        self.tracker.call_count = 0
        self.tracker.trace = []

        # Prompt optimized to complete comparisons efficiently within 6 calls
        system_instruction = (
            "You are a strict, highly efficient document QA assistant analyzing an uploaded PDF.\n"
            "You operate under a STRICT MAXIMUM BUDGET OF 6 TOOL CALLS PER QUERY.\n\n"
            "EFFICIENT SEARCH PROTOCOL:\n"
            "1. TYPOS & ACRONYMS: Fix typos in the query (e.g., 'Comapre' -> 'Compare') and extract key terms.\n"
            "2. COMPARISONS (e.g., 'Compare BFS and DFS'):\n"
            "   - Call `search_keyword(doc_id='doc_1', keyword='bfs')` [Call #1]\n"
            "   - Call `search_keyword(doc_id='doc_1', keyword='dfs')` [Call #2]\n"
            "   - Select ONLY the single most relevant page for each topic.\n"
            "   - Call `get_page` on the top matching page for topic 1 [Call #3]\n"
            "   - Call `get_page` on the top matching page for topic 2 [Call #4]\n"
            "   - Formulate your answer immediately using those fetched pages.\n"
            "3. DO NOT make redundant search calls or list document headings unless specifically asked for an overview.\n\n"
            "STRICT GROUNDING & CITATION RULES:\n"
            "1. NEVER use outside knowledge. Base every claim strictly on content fetched via `get_page`.\n"
            "2. Cite exact page numbers inline (e.g., '[Page 20]').\n"
            "3. End your response with: **Sources Referenced:** Page X, Page Y\n"
            "4. If no information is found after searching, state: "
            "'The uploaded document does not contain information to answer this question.'"
        )

        tools = [types.Tool(function_declarations=self._get_tool_declarations())]
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=tools,
            temperature=0.2
        )

        contents = [user_query]

        while True:
            response = self._generate_content_with_retry(contents, config)

            function_calls = response.function_calls
            if not function_calls:
                return {
                    "answer": response.text,
                    "trace": self.tracker.trace,
                    "call_count": self.tracker.call_count
                }

            contents.append(response.candidates[0].content)

            function_responses = []
            for call in function_calls:
                tool_name = call.name
                tool_args = dict(call.args)

                try:
                    result = self.tracker.execute_tool(tool_name, **tool_args)
                except BudgetExceededError as e:
                    result = f"Error: Tool call budget exceeded! {e}"
                except Exception as e:
                    result = f"Error executing tool {tool_name}: {e}"

                function_responses.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": result}
                    )
                )

            contents.append(types.Content(role="user", parts=function_responses))
            time.sleep(1)