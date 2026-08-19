import os

import streamlit as st
from dotenv import load_dotenv

import rag

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


def _pg_status() -> str:
    try:
        conn, is_pg = rag._get_storage_connection()
        conn.close()
        return "OK" if is_pg else "Local SQLite"
    except Exception:
        return "Không kết nối"


def _chroma_status() -> str:
    try:
        collection = rag._get_collection()
        return "Sẵn sàng" if collection is not None else "Không sẵn sàng"
    except Exception:
        return "Không sẵn sàng"


def main() -> None:
    st.set_page_config(page_title="Buổi 06 - Demo RAG", layout="wide")
    st.title("Buổi 06 - Demo RAG")
    st.caption("Question → Top-k → Gemini → Answer")

    with st.sidebar:
        st.header("Trạng thái")
        st.write(f"PostgreSQL: {_pg_status()}")
        st.write(f"ChromaDB: {_chroma_status()}")
        st.write("Gemini API Key:", "Có" if rag.GEMINI_API_KEY else "Thiếu")
        if st.button("Index"):
            with st.spinner("Đang index..."):
                count = rag.index()
            st.success(f"Đã index {count} chunk")

    question = st.text_area("Câu hỏi", height=120)
    k = st.slider("Top-k", min_value=1, max_value=5, value=3)

    if st.button("Trả lời"):
        if not question.strip():
            st.warning("Vui lòng nhập câu hỏi")
        else:
            with st.spinner("Đang tìm kiếm..."):
                docs = rag.retrieve(question, k=k)
                answer = rag.answer(question, k=k)

            st.subheader("Top-k")
            for doc in docs:
                st.write(f"- {doc['source']}: {doc['text'][:400]}")

            st.subheader("Answer")
            if rag.GEMINI_API_KEY:
                st.write(answer)
            else:
                st.info("Thiếu API Key, chỉ hiển thị Retrieval")
                st.write(answer)


if __name__ == "__main__":
    main()

