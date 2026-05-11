import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"
st.set_page_config(page_title="Mini RAG", layout="wide")
st.title("Mini RAG System")

if "project_id" not in st.session_state:
    st.session_state.project_id = None

#upload
st.header("📄 Upload PDF")
file = st.file_uploader("Upload a PDF", type=["pdf"])

if st.button("Upload"):
    res = requests.post(f"{BASE_URL}/upload", files={"file": (file.name, file, "application/pdf")})
    if res.status_code == 200:
        st.session_state.project_id = res.json()["project_id"]
        st.success(f"{file.name} uploaded successfully!")
    else:
        st.error(f"Failed to upload {file.name}")

#process
st.header("⚙️ Process Document")
if st.button("Process"):
    if not st.session_state.project_id:
        st.error("Upload a file first")
    else:
        res = requests.post(f"{BASE_URL}/process/{st.session_state.project_id}")
        if res.status_code == 200:
            chunk_count = res.json()["chunk_count"]
            st.success(f"Processed successfully! Total chunks: {chunk_count}")
        else:
            st.error(f"Processing failed: {res.text}")

#Query
st.header("❓ Ask a Question")
question = st.text_area("Ask anything about the CV (English or Arabic)")

if st.button("Get Answer"):
    if not st.session_state.project_id:
        st.error("Upload and process a file first")
    elif not question.strip(): #lw el so2al fady
        st.warning("Please enter a question")
    else:
        res = requests.post(f"{BASE_URL}/search/{st.session_state.project_id}",json={"question": question})
        if res.status_code == 200:
            data = res.json()
            st.subheader("Answer")
            st.write(data["answer"])
            st.subheader("Sources")
            st.json(data["sources"])
        else:
            st.error(f"Failed to get answer: {res.text}")