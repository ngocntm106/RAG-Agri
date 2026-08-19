# -*- coding: utf-8 -*-
"""Streamlit UI for Advanced RAG (Buổi 09)

Bốn tab:
1. Hỏi đáp Advanced RAG – end‑to‑end pipeline (default: hybrid_rerank).
2. So sánh Retrieval – bảng so sánh rank movement giữa BM25 / Semantic / Hybrid / Hybrid+Rerank.
3. Pipeline Trace – metric cards nhiều tầng + latency.
4. Đánh giá – feedback form.

Sidebar hiển thị cấu hình chi tiết, không lộ secret.
Không tự tải model/index/gọi API khi mở.
"""

import time
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

# Đảm bảo thư mục chứa package 'rag_foundation' nằm trong sys.path
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from rag_foundation.buoi_08.advanced_rag import (
    advanced_status,
    bm25_search,
    get_semantic_candidates,
    hybrid_retrieval,
    load_advanced_config,
    query_advanced_rag,
    rerank_candidates,
)
from rag_foundation.buoi_08.rag import load_config, load_chunks, build_collection_name

# ---------------------------------------------------------------------------
# Helpers UI
# ---------------------------------------------------------------------------

def _fmt(val, digits: int = 4):
    """Format số hoặc trả về '-' nếu None."""
    if val is None:
        return "-"
    if isinstance(val, float):
        return f"{val:.{digits}f}"
    return str(val)


def _rank_arrow(change):
    """Biểu tượng thay đổi hạng."""
    if change is None or change == "-":
        return "-"
    try:
        c = float(change)
    except (ValueError, TypeError):
        return "-"
    if c > 0:
        return f"⬆ +{int(c)}"
    if c < 0:
        return f"⬇ {int(c)}"
    return "= 0"


def _format_evidence_card(evd: Dict[str, Any], show_rerank: bool = True) -> None:
    """Render một evidence card."""
    chunk_id = evd.get("chunk_id", "-")
    accepted = evd.get("accepted")
    badge = "🟢" if accepted else ("🔴" if accepted is False else "⚪")
    with st.expander(f"{badge} Chunk `{chunk_id}`", expanded=False):
        col_meta, col_scores = st.columns(2)
        with col_meta:
            st.markdown("**Metadata**")
            st.write(f"**Source:** {evd.get('source', '-')}")
            st.write(f"**Page:** {evd.get('page_start', '-')}–{evd.get('page_end', '-')}")
        with col_scores:
            st.markdown("**Scores / Ranks**")
            st.write(f"BM25 rank/score: {_fmt(evd.get('bm25_rank'), 0)} / {_fmt(evd.get('bm25_score'))}")
            st.write(f"Semantic rank/dist: {_fmt(evd.get('semantic_rank'), 0)} / {_fmt(evd.get('semantic_distance'))}")
            st.write(f"RRF score/fused rank: {_fmt(evd.get('rrf_score'))} / {_fmt(evd.get('fused_rank'), 0)}")
            if show_rerank:
                st.write(f"Rerank score/rank: {_fmt(evd.get('rerank_score'))} / {_fmt(evd.get('rerank_rank'), 0)}")
                rc = evd.get("rank_change")
                st.write(f"Rank change: {_rank_arrow(rc)}")
        st.markdown("**Evidence Text**")
        st.write(evd.get("text", ""))
        if accepted is not None:
            color = "green" if accepted else "red"
            st.markdown(
                f"<span style='color:{color};font-weight:bold'>Accepted: {accepted}</span>",
                unsafe_allow_html=True,
            )


def _load_sidebar_config() -> Dict[str, Any]:
    """Load config và hiển thị sidebar. Không gọi API, không tải model."""
    base_cfg = load_config()
    adv_cfg = load_advanced_config()

    # advanced_status chỉ đọc filesystem, không tải gì
    status = advanced_status()

    with st.sidebar:
        st.header("⚙️ Cấu hình Pipeline")

        st.markdown("**Strategy**")
        st.write(adv_cfg.get("strategy", "hierarchical"))

        st.markdown("**Retrieval mode mặc định**")
        st.write("`hybrid_rerank`")

        st.markdown("**Final top‑k**")
        st.write(adv_cfg.get("final_top_k"))

        st.markdown("**Candidates**")
        st.write(f"BM25: **{adv_cfg.get('bm25_candidates')}** | Semantic: **{adv_cfg.get('semantic_candidates')}**")

        st.markdown("**RRF**")
        st.write(
            f"k={adv_cfg.get('rrf_k')}, "
            f"w_bm25={adv_cfg.get('rrf_bm25_weight')}, "
            f"w_sem={adv_cfg.get('rrf_semantic_weight')}"
        )

        st.markdown("**Reranker**")
        st.write(f"Model: `{adv_cfg.get('reranker_model')}`")
        st.write(f"Device: {adv_cfg.get('rerank_device')}")
        cache_ok = status.get("reranker_cache_exists", False)
        st.write(f"Cache: {'✅ Có' if cache_ok else '❌ Chưa tải'}")

        st.markdown("**Rerank limits**")
        st.write(
            f"Pool K: {adv_cfg.get('rerank_candidates')} | "
            f"Min score: {adv_cfg.get('rerank_min_score')}"
        )

        st.markdown("**Semantic collection**")
        st.write(f"`{status.get('semantic_collection_name', '-')}`")
        st.write(f"Số chunk: {status.get('collection_count', '-')}")

        st.markdown("**API key**")
        has_key = bool(base_cfg.get("gemini_api_key"))
        st.write("✅ Có" if has_key else "❌ Thiếu")

    return {"base": base_cfg, "adv": adv_cfg, "status": status}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(
        page_title="Advanced RAG – Buổi 09",
        page_icon="🧭",
        layout="wide",
    )
    st.title("🧭 Advanced RAG – Buổi 09")
    st.caption(
        "Pipeline nhiều tầng: BM25 → Semantic → RRF Fusion → Cross‑Encoder Rerank. "
        "Khác biệt so với Buổi 07 ở bảng so sánh rank movement và trace từng tầng."
    )

    config = _load_sidebar_config()
    adv = config["adv"]

    tabs = st.tabs([
        "🤖 Hỏi đáp Advanced RAG",
        "🔎 So sánh Retrieval",
        "📊 Pipeline Trace",
        "📝 Đánh giá",
    ])

    # ─────────────────────────────────────────────────────────────────────
    # Tab 1 – Answer (full pipeline)
    # ─────────────────────────────────────────────────────────────────────
    with tabs[0]:
        st.subheader("🤖 Hỏi đáp Advanced RAG")
        st.info(
            "Nhập câu hỏi và chọn chế độ retrieval. "
            "Model/index chỉ được tải khi bấm **Trả lời**."
        )
        question = st.text_input("Câu hỏi", "", key="q1")
        mode = st.selectbox(
            "Chế độ retrieval",
            ["bm25", "semantic", "hybrid", "hybrid_rerank"],
            index=3,
            key="mode1",
        )

        if st.button("▶ Trả lời", key="btn_answer"):
            if not question.strip():
                st.error("Vui lòng nhập câu hỏi.")
            else:
                with st.spinner("Đang thực thi pipeline…"):
                    t0 = time.time()
                    try:
                        result = query_advanced_rag(
                            question=question,
                            top_k=adv.get("final_top_k", 5),
                            mode=mode,
                            strategy=adv.get("strategy", "hierarchical"),
                        )
                    except Exception as exc:
                        st.error(f"❌ Lỗi: {exc}")
                        st.stop()
                    total_ms = (time.time() - t0) * 1000

                # Status
                status_val = result.get("status", "?")
                if status_val == "ok":
                    st.success(f"✅ Status: **{status_val}** | Mode: **{mode}** | {total_ms:.0f} ms")
                else:
                    st.warning(f"⚠️ Status: **{status_val}** | Mode: **{mode}** | {total_ms:.0f} ms")

                # Warnings
                for w in result.get("warnings", []):
                    st.warning(w)

                # Answer
                if result.get("answer"):
                    st.markdown("### 🗨️ Câu trả lời")
                    st.write(result["answer"])

                # Citations
                if result.get("citations"):
                    st.markdown("### 📑 Nguồn trích dẫn")
                    for cit in result["citations"]:
                        st.write(cit)

                # Evidence cards
                if result.get("evidence"):
                    st.markdown("### 📌 Evidence chunks")
                    is_rerank = mode in ("hybrid_rerank",)
                    for ev in result["evidence"]:
                        _format_evidence_card(ev, show_rerank=is_rerank)

                # Save trace to session
                st.session_state["last_trace"] = result.get("trace", {})
                st.session_state["last_total_ms"] = total_ms
                st.session_state["last_mode"] = mode

    # ─────────────────────────────────────────────────────────────────────
    # Tab 2 – Comparison (retrieval only, NO generation)
    # ─────────────────────────────────────────────────────────────────────
    with tabs[1]:
        st.subheader("🔎 So sánh Retrieval – Bảng rank movement")
        st.info(
            "Chỉ chạy retrieval (không gọi LLM). "
            "Bảng so sánh cho thấy rank của mỗi chunk qua 4 tầng: "
            "BM25 → Semantic → RRF Fusion → Rerank."
        )
        question_cmp = st.text_input("Câu hỏi (so sánh)", "", key="cmp_q")

        if st.button("▶ So sánh", key="cmp_btn"):
            if not question_cmp.strip():
                st.error("Vui lòng nhập câu hỏi.")
            else:
                strategy = adv.get("strategy", "hierarchical")

                with st.spinner("Đang chạy BM25…"):
                    chunks, _ = load_chunks(strategy=strategy)
                    t0 = time.time()
                    bm25_res = bm25_search(
                        question=question_cmp,
                        chunks=chunks,
                        candidate_k=adv.get("bm25_candidates", 20),
                    )
                    bm25_ms = (time.time() - t0) * 1000

                with st.spinner("Đang chạy Semantic…"):
                    t0 = time.time()
                    try:
                        sem_res = get_semantic_candidates(
                            question=question_cmp,
                            candidate_k=adv.get("semantic_candidates", 20),
                            strategy=strategy,
                        )
                        sem_ms = (time.time() - t0) * 1000
                        sem_error = None
                    except Exception as exc:
                        sem_res = []
                        sem_ms = 0.0
                        sem_error = str(exc)

                with st.spinner("Đang chạy Hybrid RRF…"):
                    t0 = time.time()
                    try:
                        fused_res, trace_hybrid = hybrid_retrieval(
                            question=question_cmp,
                            strategy=strategy,
                        )
                        hybrid_ms = (time.time() - t0) * 1000
                        hybrid_error = None
                    except Exception as exc:
                        fused_res = []
                        trace_hybrid = {}
                        hybrid_ms = 0.0
                        hybrid_error = str(exc)

                with st.spinner("Đang chạy Rerank…"):
                    t0 = time.time()
                    rerank_pool = fused_res[: adv.get("rerank_candidates", 20)]
                    try:
                        reranked = rerank_candidates(
                            query=question_cmp,
                            candidates=rerank_pool,
                            top_k=adv.get("final_top_k", 5),
                        )
                        rerank_ms = (time.time() - t0) * 1000
                        rerank_error = None
                    except Exception as exc:
                        reranked = []
                        rerank_ms = 0.0
                        rerank_error = str(exc)

                # ── Latency summary ──────────────────────────────────────
                st.markdown("#### ⏱ Latency từng tầng")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("BM25", f"{bm25_ms:.0f} ms")
                c2.metric("Semantic", f"{sem_ms:.0f} ms" if not sem_error else "lỗi")
                c3.metric("Hybrid RRF", f"{hybrid_ms:.0f} ms" if not hybrid_error else "lỗi")
                c4.metric("Rerank", f"{rerank_ms:.0f} ms" if not rerank_error else "lỗi")

                if sem_error:
                    st.warning(f"⚠️ Semantic: {sem_error}")
                if hybrid_error:
                    st.warning(f"⚠️ Hybrid: {hybrid_error}")
                if rerank_error:
                    st.warning(f"⚠️ Rerank: {rerank_error}")

                # ── Comparison table ─────────────────────────────────────
                st.markdown("#### 📋 Bảng so sánh Rank (mỗi dòng = 1 chunk)")

                # Collect all unique chunk IDs
                all_ids = set()
                for lst in [bm25_res, sem_res, fused_res, reranked]:
                    all_ids.update(c["chunk_id"] for c in lst)

                bm25_map = {r["chunk_id"]: r for r in bm25_res}
                sem_map = {r["chunk_id"]: r for r in sem_res}
                fused_map = {r["chunk_id"]: r for r in fused_res}
                rerank_map = {r["chunk_id"]: r for r in reranked}

                rows = []
                for cid in sorted(all_ids):
                    bm_r = bm25_map.get(cid, {}).get("bm25_rank")
                    se_r = sem_map.get(cid, {}).get("semantic_rank")
                    fu_r = fused_map.get(cid, {}).get("fused_rank")
                    re_r = rerank_map.get(cid, {}).get("rerank_rank")

                    # Rank change: fused → rerank
                    if fu_r is not None and re_r is not None:
                        change = fu_r - re_r
                        arrow = _rank_arrow(change)
                    else:
                        arrow = "-"

                    # Which modes found this chunk
                    found_in = []
                    if bm_r is not None:
                        found_in.append("BM25")
                    if se_r is not None:
                        found_in.append("Sem")
                    if fu_r is not None:
                        found_in.append("Hybrid")
                    if re_r is not None:
                        found_in.append("Rerank")

                    rows.append({
                        "Chunk ID": cid,
                        "BM25 rank": _fmt(bm_r, 0),
                        "Semantic rank": _fmt(se_r, 0),
                        "Fused rank": _fmt(fu_r, 0),
                        "Rerank rank": _fmt(re_r, 0),
                        "Rank change ↕": arrow,
                        "Xuất hiện trong": ", ".join(found_in),
                    })

                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)

                # ── Per-mode candidate counts ────────────────────────────
                st.markdown("#### 🔢 Số ứng viên từng tầng")
                m1, m2, m3, m4, m5 = st.columns(5)
                m1.metric("BM25", len(bm25_res))
                m2.metric("Semantic", len(sem_res))
                m3.metric("After RRF", len(fused_res))
                m4.metric("Rerank pool", len(rerank_pool))
                m5.metric("Final (reranked)", len(reranked))

                # Save compare trace
                st.session_state["last_trace"] = trace_hybrid
                st.session_state["last_total_ms"] = bm25_ms + sem_ms + hybrid_ms + rerank_ms

    # ─────────────────────────────────────────────────────────────────────
    # Tab 3 – Pipeline Trace (metric cards)
    # ─────────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.subheader("📊 Pipeline Trace – Nhiều tầng")
        trace = st.session_state.get("last_trace")

        if not trace:
            st.info("Chưa có trace. Hãy chạy một truy vấn trong Tab 1 hoặc Tab 2 trước.")
        else:
            mode_label = trace.get("mode") or st.session_state.get("last_mode", "?")
            st.markdown(f"**Mode:** `{mode_label}` | **Strategy:** `{trace.get('strategy', '?')}`")

            st.markdown("#### Số ứng viên qua từng tầng")
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("BM25", trace.get("bm25_candidate_count", "-"))
            col2.metric("Semantic", trace.get("semantic_candidate_count", "-"))
            col3.metric("Union", trace.get("union_count", "-"))
            col4.metric("Overlap", trace.get("overlap_count", "-"))
            col5.metric("After RRF", trace.get("fused_count", "-"))

            col6, col7, col8 = st.columns(3)
            col6.metric("Rerank pool", trace.get("rerank_pool_size", "-"))
            col7.metric("Reranked count", trace.get("reranked_count", "-"))
            col8.metric("Accepted", trace.get("accepted_count", "-"))

            st.markdown("#### Latency từng bước (ms)")
            lat = trace.get("latency_ms", {})
            lat_cols = st.columns(max(1, len(lat) + 2))
            for i, (name, ms) in enumerate(lat.items()):
                lat_cols[i].metric(f"⏱ {name}", f"{ms:.1f} ms")

            rerank_lat = trace.get("rerank_latency_ms")
            gen_lat = trace.get("generation_latency_ms")
            total_ms = st.session_state.get("last_total_ms", 0)

            extra_col1, extra_col2, extra_col3 = st.columns(3)
            if rerank_lat is not None:
                extra_col1.metric("⏱ rerank", f"{rerank_lat:.1f} ms")
            if gen_lat is not None:
                extra_col2.metric("⏱ generation", f"{gen_lat:.1f} ms")
            extra_col3.metric("⏱ Total", f"{total_ms:.1f} ms")

            st.markdown("#### RRF Parameters")
            st.write(
                f"k = **{trace.get('rrf_k', '-')}**, "
                f"bm25_weight = **{trace.get('rrf_bm25_weight', '-')}**, "
                f"semantic_weight = **{trace.get('rrf_semantic_weight', '-')}**"
            )

            if trace.get("rerank_skipped"):
                st.warning("⚠️ Rerank bị bỏ qua (model cache chưa có hoặc lỗi import).")

            st.markdown("#### Raw trace (JSON)")
            with st.expander("Xem raw trace"):
                st.json(trace)

    # ─────────────────────────────────────────────────────────────────────
    # Tab 4 – Evaluation / Feedback
    # ─────────────────────────────────────────────────────────────────────
    with tabs[3]:
        st.subheader("📝 Đánh giá trải nghiệm")
        rating = st.slider("Đánh giá chất lượng trả lời (1–5)", 1, 5, 4)
        comment = st.text_area("Nhận xét của bạn")
        if st.button("Gửi phản hồi", key="btn_feedback"):
            st.success("✅ Cảm ơn bạn đã gửi phản hồi!")
            st.write(f"**Rating:** {'⭐' * rating}")
            if comment:
                st.write(f"**Nhận xét:** {comment}")


if __name__ == "__main__":
    main()
