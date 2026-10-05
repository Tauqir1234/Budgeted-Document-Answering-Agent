import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="PDF Q&A Agent", layout="wide")
st.title("📄 PDF Q&A Agent")

# Sidebar for Document Upload
with st.sidebar:
    st.header("Document Management")
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])
    
    if uploaded_file is not None:
        if st.button("Process PDF"):
            with st.spinner("Processing PDF..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                response = requests.post(f"{API_URL}/upload-pdf", files=files)
                if response.status_code == 200:
                    st.success(f"Loaded '{uploaded_file.name}' successfully!")
                    st.session_state["doc_loaded"] = True
                else:
                    st.error(f"Error: {response.json().get('detail')}")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_query := st.chat_input("Ask a question about the PDF..."):
    if not st.session_state.get("doc_loaded"):
        st.warning("Please upload and process a PDF first.")
    else:
        st.session_state["messages"].append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing document and executing tool pipeline..."):
                res = requests.post(f"{API_URL}/query", json={"query": user_query})
                if res.status_code == 200:
                    data = res.json()
                    
                    # Render Main Answer
                    st.markdown(data["answer"])
                    st.session_state["messages"].append({"role": "assistant", "content": data["answer"]})
                    
                    # Render Human-Readable Execution Steps
                    with st.expander(f"🛠️ Agent Execution Steps ({data['call_count']}/6 tool calls used)"):
                        for step in data.get("trace", []):
                            call_num = step.get("call_num", "-")
                            tool_name = step.get("tool", "Unknown Tool")
                            args = step.get("args", {})
                            summary = step.get("result_summary", "No details returned.")

                            st.markdown(f"#### Step {call_num}: Executed `{tool_name}`")
                            
                            # Format input parameters cleanly
                            if args:
                                args_str = ", ".join([f"**{k}**: `{v}`" for k, v in args.items()])
                                st.markdown(f"* **Parameters:** {args_str}")
                            else:
                                st.markdown("* **Parameters:** None")
                            
                            st.markdown(f"* **Output Summary:** {summary}")
                            st.divider()
                else:
                    st.error(f"Error: {res.json().get('detail')}")