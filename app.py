"""
Optional Streamlit web UI for the RAG research assistant.

Run with:
    streamlit run app.py
"""
import streamlit as st
from pathlib import Path

import config
from src.rag_pipeline import ingest_documents, ask_question

st.set_page_config(page_title="RAG Research Assistant", page_icon="📚", layout="wide")
st.title("📚 RAG Research Assistant")
st.caption("Ask questions about your documents — every answer is cited.")

with st.sidebar:
    st.header("Documents")
    uploaded = st.file_uploader(
        "Upload PDF / TXT / MD files", accept_multiple_files=True,
        type=["pdf", "txt", "md"]
    )
    if uploaded:
        config.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        for f in uploaded:
            dest = config.DOCUMENTS_DIR / f.name
            dest.write_bytes(f.getvalue())
        st.success(f"Saved {len(uploaded)} file(s) to data/documents/")

    if st.button("🔄 (Re)ingest documents"):
        with st.spinner("Ingesting..."):
            n = ingest_documents()
        st.success(f"Ingested {n} new chunk(s).")

    existing = sorted(
        p.name for p in config.DOCUMENTS_DIR.glob("*")
        if p.suffix.lower() in config.SUPPORTED_EXTENSIONS
    ) if config.DOCUMENTS_DIR.exists() else []
    if existing:
        st.subheader("Indexed files")
        for name in existing:
            st.write(f"- {name}")

if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.markdown(turn["content"])

question = st.chat_input("Ask a question about your documents...")
if question:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = ask_question(question)
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("Sources"):
                st.text(result["sources"])

    st.session_state.history.append({"role": "assistant", "content": result["answer"]})
