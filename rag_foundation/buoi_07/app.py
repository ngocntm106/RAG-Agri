"""Streamlit UI cho Buổi 07 RAG.

Giao diện này chỉ dùng các hàm public có trong rag.py và không tái hiện lại
logic loader/index/query bên trong app.
"""

import streamlit as st

import rag  # noqa: E402


def load_config_safe() -> tuple[dict[str, object] | None, str | None]:
    try:
        config = rag.load_config()
        return config, None
    except Exception as exc:
        return None, str(exc)


def build_status_info(strategy: str, config: dict[str, object]) -> tuple[dict[str, object] | None, str | None]:
    try:
        status_info = rag.status(strategy=strategy)
        return status_info, None
    except Exception as exc:
        return None, str(exc)


def resolve_collection_state(strategy: str, config: dict[str, object]) -> tuple[dict[str, object], bool, int, str | None]:
    status_info, status_error = build_status_info(strategy, config)
    if status_error:
        return {}, False, 0, status_error
    collection_exists = bool(status_info.get("collection_exists", False))
    record_count = int(status_info.get("record_count", 0))
    return status_info, collection_exists, record_count, None


def format_collection_status(status_info: dict[str, object]) -> str:
    if not status_info.get("collection_exists"):
        return "Collection chưa tồn tại"
    return f"Đã tồn tại ({status_info.get('record_count', 0)} chunk)"


def main() -> None:
    st.set_page_config(page_title="RAG Buổi 07", layout="wide")

    st.title("RAG Buổi 07")
    st.write(
        "Giao diện dùng các hàm `status`, `index_chunks` và `query_knowledge` trong `rag.py`. "
        "Không tái tạo lại logic retrieval và generation trong app."
    )

    if "last_index_result" not in st.session_state:
        st.session_state.last_index_result = None
    if "last_query_result" not in st.session_state:
        st.session_state.last_query_result = None
    if "collection_status" not in st.session_state:
        st.session_state.collection_status = {}

    config, config_error = load_config_safe()
    strategy = st.sidebar.selectbox("Chọn strategy", ["hierarchical", "semantic", "fixed-size"])
    top_k = st.sidebar.slider("Số tài liệu truy xuất (top-k)", 1, 10, 5)
    reset_collection = st.sidebar.checkbox("Reset collection trước khi index")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Trạng thái hệ thống")

    if config is None:
        st.sidebar.error("Không đọc được cấu hình .env. Vui lòng kiểm tra biến môi trường.")
        st.sidebar.write(f"Lỗi: {config_error}")
        api_key_text = "Thiếu"
        embedding_model = "-"
        embedding_dim = "-"
        generation_model = "-"
        rag_max_distance = "-"
        collection_name = "-"
        collection_exists = False
        record_count = 0
    else:
        api_key_text = "Có" if config.get("gemini_api_key") else "Thiếu"
        embedding_model = config.get("gemini_embedding_model", "-")
        embedding_dim = config.get("gemini_embedding_dim", "-")
        generation_model = config.get("gemini_generation_model", "-")
        rag_max_distance = config.get("rag_max_distance", "-")
        collection_name = rag.build_collection_name(strategy, embedding_model, int(embedding_dim) if isinstance(embedding_dim, int) else int(str(embedding_dim))) if embedding_model != "-" else "-"
        status_info, collection_exists, record_count, status_error = resolve_collection_state(strategy, config)
        if status_error:
            st.sidebar.warning("Không thể kiểm tra trạng thái collection: hãy kiểm tra cấu hình và index lại.")
            st.sidebar.write(f"Lỗi: {status_error}")
            collection_exists = False
            record_count = 0
        else:
            st.session_state.collection_status = status_info or {}

    st.sidebar.write(f"**API key:** {api_key_text}")
    st.sidebar.write(f"**Embedding model:** {embedding_model}")
    st.sidebar.write(f"**Embedding dimension:** {embedding_dim}")
    st.sidebar.write(f"**Generation model:** {generation_model}")
    st.sidebar.write(f"**Strategy:** {strategy}")
    st.sidebar.write(f"**Collection name:** {collection_name}")
    st.sidebar.write(f"**Collection:** {'Đã tồn tại' if collection_exists else 'Chưa tồn tại'}")
    st.sidebar.write(f"**Số chunk:** {record_count}")
    st.sidebar.write(f"**RAG_MAX_DISTANCE:** {rag_max_distance}")

    st.sidebar.markdown("---")
    st.sidebar.info("Khi đổi strategy, app sẽ cập nhật collection tương ứng chỉ bằng hàm status.")

    col_index, col_query = st.columns([1, 1])

    with col_index:
        st.header("Index dữ liệu")
        st.write("Chỉ gọi `index_chunks` khi bấm nút. Không tự động index khi mở app.")
        can_index = config is not None and api_key_text == "Có"
        if not can_index:
            st.warning("Không thể index: thiếu cấu hình hoặc API key.")

        index_pressed = st.button("Index dữ liệu")
        if index_pressed:
            if config is None:
                st.error("Không thể index do thiếu cấu hình `.env`.")
            else:
                before_count = record_count
                try:
                    with st.spinner("Đang index dữ liệu..."):
                        result = rag.index_chunks(strategy=strategy, reset=reset_collection)
                    st.success("Index hoàn thành.")
                    st.session_state.last_index_result = result
                    st.session_state.collection_status = {
                        "collection_exists": True,
                        "record_count": result.get("records", 0),
                        "collection_name": result.get("collection_name"),
                    }
                    after_count = result.get("records", 0)
                    st.write(f"**Strategy:** {result.get('strategy')}" )
                    st.write(f"**Collection:** {result.get('collection_name')}" )
                    st.write(f"**Chunk trước khi index:** {before_count}")
                    st.write(f"**Chunk sau khi index:** {after_count}")
                    if result.get("stats"):
                        stats = result["stats"]
                        st.write(f"**Empty text bỏ qua:** {stats.get('empty_text_skipped', 0)}")
                        st.write(f"**Valid chunks:** {stats.get('valid_chunks', 0)}")
                        st.write(f"**Tổng record chọn:** {stats.get('selected_records', 0)}")
                except Exception as exc:
                    st.error("Index không thành công. Vui lòng kiểm tra `.env` và trạng thái collection.")
                    st.write(str(exc))

        if st.session_state.last_index_result is not None:
            st.markdown("### Kết quả index gần nhất")
            last = st.session_state.last_index_result
            st.write(f"Strategy: {last.get('strategy')}")
            st.write(f"Collection: {last.get('collection_name')}")
            st.write(f"Số bản ghi trong collection: {last.get('records')}")
            if last.get('stats'):
                stats = last['stats']
                st.write(f"Empty text bỏ qua: {stats.get('empty_text_skipped', 0)}")
                st.write(f"Valid chunks: {stats.get('valid_chunks', 0)}")

    with col_query:
        st.header("Hỏi câu hỏi")
        question = st.text_area("Câu hỏi", value="", height=180)
        ask_pressed = st.button("Gửi câu hỏi")

        if ask_pressed:
            if config is None:
                st.error("Không thể hỏi do thiếu cấu hình `.env`.")
            elif api_key_text != "Có":
                st.error("Không thể hỏi do thiếu API key trong `.env`.")
            elif not collection_exists:
                st.error("Không thể hỏi, collection chưa tồn tại hoặc chưa index.")
                st.info("Hãy bấm nút Index dữ liệu trước, rồi thử lại.")
            elif record_count < 1:
                st.error("Không thể hỏi, collection hiện tại đang rỗng.")
            elif not question.strip():
                st.error("Vui lòng nhập câu hỏi trước khi gửi.")
            else:
                try:
                    with st.spinner("Đang truy vấn và tạo câu trả lời..."):
                        generator = rag.build_generation_service(config)
                        result = rag.query_knowledge(
                            question=question,
                            top_k=top_k,
                            strategy=strategy,
                            generator=generator,
                        )
                    st.session_state.last_query_result = result
                except Exception as exc:
                    st.error("Không thể thực hiện truy vấn. Vui lòng kiểm tra cấu hình và collection.")
                    st.write(str(exc))

        if st.session_state.last_query_result is not None:
            result = st.session_state.last_query_result
            st.markdown("### Kết quả truy vấn")
            st.write(f"**Trạng thái:** {result.get('status')}")
            if result.get('status') == 'insufficient_evidence':
                st.info("Không tìm thấy đủ thông tin liên quan trong tài liệu đã cung cấp.")
            elif result.get('status') == 'retrieval_only':
                st.warning("Đã truy xuất được nguồn nhưng chưa thể tạo câu trả lời tổng hợp.")

            st.subheader("Answer")
            st.write(result.get('answer', ''))

            if result.get('warnings'):
                st.subheader("Cảnh báo")
                for warning in result['warnings']:
                    st.warning(warning)

            st.subheader("Citations")
            citations = result.get('citations', [])
            if citations:
                for citation in citations:
                    st.write(citation.get('display'))
            else:
                st.write("Không có citation hợp lệ.")

            st.subheader("Nguồn tham khảo")
            evidences = result.get('evidence', [])
            if not evidences:
                st.info("Chưa có evidence.")
            for evidence in evidences:
                title = f"{evidence.get('source', '-') } – tr. {evidence.get('page_start')}" if evidence.get('page_start') == evidence.get('page_end') else f"{evidence.get('source', '-') } – tr. {evidence.get('page_start')}-{evidence.get('page_end')} – {evidence.get('chunk_id', '-') }"
                with st.expander(title):
                    st.write(f"Evidence ID: {evidence.get('evidence_id')}")
                    st.write(f"Source: {evidence.get('source')}")
                    st.write(f"Page: {evidence.get('page_start')} - {evidence.get('page_end')}")
                    st.write(f"Chunk ID: {evidence.get('chunk_id')}")
                    st.write(f"Distance: {evidence.get('distance'):.4f} (khoảng cách cosine; số nhỏ hơn thường liên quan hơn)")
                    st.write(f"Accepted: {'Có' if evidence.get('accepted') else 'Không'}")
                    st.write(evidence.get('text', ''))


if __name__ == "__main__":
    main()
