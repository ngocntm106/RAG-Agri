"""Buổi 08 evaluation module — Bước 10.

Đo Recall@K, MRR@K, nDCG@K (binary relevance) và latency (mean, p50)
trên tập câu hỏi eval/questions.json.

Quy tắc:
- Không gọi generation (chỉ retrieval).
- Mỗi query lỗi: ghi fail rõ, không bỏ âm thầm.
- needs_human_review=true → báo warning; không tuyên bố mode thắng chính thức.
- Report lưu JSON tại reports/ với timestamp, config, model identity.
- Cùng corpus/query/k cho mọi mode.

CLI:
    python evaluate.py --strategy hierarchical --k 5
    python evaluate.py --questions eval/questions.json --modes bm25 hybrid --k 3
"""

import argparse
import json
import math
import os
import sys
import time as _time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent


# ──────────────────────────────────────────────────────────────────────────────
# Metric formulas (testable units)
# ──────────────────────────────────────────────────────────────────────────────

def recall_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """Recall@K — tỷ lệ relevant docs xuất hiện trong top-K retrieved.

    = |relevant ∩ retrieved[:k]| / |relevant|
    Trả 0.0 nếu relevant_ids rỗng (không phạt query ngoài phạm vi).
    """
    if not relevant_ids:
        return 0.0
    top_k_ids = set(retrieved_ids[:k])
    hits = sum(1 for rid in relevant_ids if rid in top_k_ids)
    return hits / len(relevant_ids)


def mrr_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """MRR@K — Mean Reciprocal Rank tại vị trí K đầu tiên.

    = 1 / rank của relevant doc đầu tiên trong top-K (0 nếu không có).
    """
    if not relevant_ids:
        return 0.0
    relevant_set = set(relevant_ids)
    for rank, rid in enumerate(retrieved_ids[:k], start=1):
        if rid in relevant_set:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved_ids: List[str], relevant_ids: List[str], k: int) -> float:
    """nDCG@K với binary relevance (rel=1 nếu trong relevant_ids, 0 nếu không).

    DCG = Σ rel_i / log2(i+1)  (i bắt đầu từ 1)
    IDCG = DCG của ranking lý tưởng (tất cả relevant ở đầu).
    nDCG = DCG / IDCG
    Trả 0.0 nếu relevant_ids rỗng.
    """
    if not relevant_ids:
        return 0.0
    relevant_set = set(relevant_ids)

    # Tính DCG thực tế
    dcg = 0.0
    for i, rid in enumerate(retrieved_ids[:k], start=1):
        if rid in relevant_set:
            dcg += 1.0 / math.log2(i + 1)

    # Tính IDCG (số lượng relevant tối đa có thể có trong top-k)
    n_relevant_in_top_k = min(len(relevant_ids), k)
    idcg = sum(1.0 / math.log2(i + 1) for i in range(1, n_relevant_in_top_k + 1))

    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def aggregate_metrics(per_query: List[Dict[str, Any]]) -> Dict[str, float]:
    """Tính mean và p50 của từng metric từ danh sách per-query results."""
    if not per_query:
        return {}

    keys = ["recall", "mrr", "ndcg", "latency_ms"]
    result: Dict[str, float] = {}

    for key in keys:
        values = [q[key] for q in per_query if q.get("status") == "ok" and key in q]
        if not values:
            result[f"{key}_mean"] = 0.0
            result[f"{key}_p50"] = 0.0
            continue
        values_sorted = sorted(values)
        n = len(values_sorted)
        result[f"{key}_mean"] = sum(values_sorted) / n
        # p50
        if n % 2 == 1:
            result[f"{key}_p50"] = values_sorted[n // 2]
        else:
            result[f"{key}_p50"] = (values_sorted[n // 2 - 1] + values_sorted[n // 2]) / 2.0

    return result


# ──────────────────────────────────────────────────────────────────────────────
# Core evaluator
# ──────────────────────────────────────────────────────────────────────────────

def _import_advanced() -> Any:
    """Import advanced_rag từ cùng thư mục."""
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))
    import importlib
    return importlib.import_module("advanced_rag")


def _retrieve_for_mode(
    question: str,
    mode: str,
    strategy: str,
    k: int,
    adv: Any,
) -> Tuple[List[str], float]:
    """Chạy retrieval cho một mode, trả (retrieved_chunk_ids, latency_ms).

    Không gọi generation.
    """
    t0 = _time.perf_counter()

    if mode == "bm25":
        import importlib
        rag = importlib.import_module("rag")
        chunks, _ = rag.load_chunks(strategy=strategy)
        adv_cfg = adv.load_advanced_config()
        results = adv.bm25_search(
            question=question,
            chunks=chunks,
            candidate_k=adv_cfg["bm25_candidates"],
        )
        ids = [r["chunk_id"] for r in results[:k]]

    elif mode == "semantic":
        adv_cfg = adv.load_advanced_config()
        results = adv.get_semantic_candidates(
            question=question,
            candidate_k=adv_cfg["semantic_candidates"],
            strategy=strategy,
        )
        ids = [r["chunk_id"] for r in results[:k]]

    elif mode == "hybrid":
        fused, _ = adv.hybrid_retrieval(
            question=question,
            strategy=strategy,
        )
        ids = [r["chunk_id"] for r in fused[:k]]

    elif mode == "hybrid_rerank":
        fused, _ = adv.hybrid_retrieval(
            question=question,
            strategy=strategy,
        )
        adv_cfg = adv.load_advanced_config()
        pool = fused[: adv_cfg["rerank_candidates"]]
        reranked = adv.rerank_candidates(
            query=question,
            candidates=pool,
            top_k=k,
        )
        ids = [r["chunk_id"] for r in reranked]

    else:
        raise ValueError(f"Mode không hợp lệ: '{mode}'")

    latency_ms = (_time.perf_counter() - t0) * 1000
    return ids, latency_ms


def evaluate_dataset(
    questions_path: str = "eval/questions.json",
    modes: Optional[List[str]] = None,
    strategy: str = "hierarchical",
    top_k: int = 5,
    retriever_fn: Optional[Any] = None,
) -> Dict[str, Any]:
    """Chạy benchmark offline cho một hoặc nhiều modes.

    Args:
        questions_path: Đường dẫn đến file JSON chứa các câu hỏi.
        modes: Danh sách mode cần đánh giá. Mặc định: ['bm25', 'semantic', 'hybrid'].
        strategy: Chunking strategy.
        top_k: K dùng cho tất cả metrics.
        retriever_fn: Hàm thay thế cho retrieval (dùng trong test; signature:
                      (question, mode, strategy, k, adv) → (ids, latency_ms)).

    Returns:
        Dict chứa ``config``, ``per_query``, ``summary``, ``needs_human_review``,
        ``timestamp``, ``warnings``.
    """
    if modes is None:
        modes = ["bm25", "semantic", "hybrid"]

    questions_file = Path(questions_path)
    if not questions_file.is_absolute():
        questions_file = BASE_DIR / questions_path

    if not questions_file.exists():
        raise FileNotFoundError(f"Không tìm thấy file câu hỏi: {questions_file}")

    questions: List[Dict[str, Any]] = json.loads(questions_file.read_text(encoding="utf-8"))

    adv = _import_advanced()
    retrieve = retriever_fn if retriever_fn is not None else _retrieve_for_mode

    any_human_review = any(q.get("needs_human_review", False) for q in questions)
    global_warnings: List[str] = []

    if any_human_review:
        global_warnings.append(
            "⚠️ MỘT HOẶC NHIỀU câu hỏi có needs_human_review=true. "
            "Gold labels chưa được chuyên gia pháp lý duyệt. "
            "Không tuyên bố mode chiến thắng chính thức."
        )

    # ── Per-query, per-mode ────────────────────────────────────────────────
    per_query: List[Dict[str, Any]] = []

    for q in questions:
        qid = q.get("query_id", "?")
        question_text = q.get("question", "")
        relevant_ids: List[str] = q.get("relevant_chunk_ids", [])
        needs_review = q.get("needs_human_review", False)

        for mode in modes:
            row: Dict[str, Any] = {
                "query_id": qid,
                "mode": mode,
                "question": question_text,
                "relevant_chunk_ids": relevant_ids,
                "needs_human_review": needs_review,
            }
            try:
                retrieved_ids, latency_ms = retrieve(
                    question_text, mode, strategy, top_k, adv
                )
                row["retrieved_ids"] = retrieved_ids
                row["latency_ms"] = latency_ms
                row["recall"] = recall_at_k(retrieved_ids, relevant_ids, top_k)
                row["mrr"] = mrr_at_k(retrieved_ids, relevant_ids, top_k)
                row["ndcg"] = ndcg_at_k(retrieved_ids, relevant_ids, top_k)
                row["status"] = "ok"
            except Exception as exc:
                row["status"] = "fail"
                row["error"] = str(exc)
                row["retrieved_ids"] = []
                row["latency_ms"] = 0.0
                row["recall"] = 0.0
                row["mrr"] = 0.0
                row["ndcg"] = 0.0

            per_query.append(row)

    # ── Summary per mode ───────────────────────────────────────────────────
    summary: Dict[str, Any] = {}
    for mode in modes:
        mode_rows = [r for r in per_query if r["mode"] == mode]
        agg = aggregate_metrics(mode_rows)
        fail_count = sum(1 for r in mode_rows if r["status"] == "fail")
        summary[mode] = {**agg, "fail_count": fail_count, "total": len(mode_rows)}

    # ── Config block ───────────────────────────────────────────────────────
    try:
        adv_cfg = adv.load_advanced_config()
    except Exception:
        adv_cfg = {}

    config_block = {
        "strategy": strategy,
        "top_k": top_k,
        "modes": modes,
        "questions_file": str(questions_file),
        "reranker_model": adv_cfg.get("reranker_model", "unknown"),
        "embedding_model": adv_cfg.get("gemini_embedding_model", "unknown"),
        "generation_model": "NOT_USED",
    }

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config": config_block,
        "needs_human_review": any_human_review,
        "warnings": global_warnings,
        "summary": summary,
        "per_query": per_query,
    }

    return report


def save_report(report: Dict[str, Any], output_dir: str = "reports") -> Path:
    """Lưu report ra file JSON tại output_dir với timestamp trong tên file."""
    out_dir = Path(output_dir)
    if not out_dir.is_absolute():
        out_dir = BASE_DIR / output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    modes_str = "_".join(report["config"].get("modes", ["unknown"]))
    filename = f"eval_{modes_str}_{ts}.json"
    out_path = out_dir / filename

    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def print_report(report: Dict[str, Any]) -> None:
    """In report ra stdout theo dạng dễ đọc."""
    print("\n" + "=" * 72)
    print(f"  EVALUATION REPORT — {report['timestamp']}")
    print("=" * 72)

    if report.get("warnings"):
        for w in report["warnings"]:
            print(f"\n{w}")

    cfg = report.get("config", {})
    print(f"\nConfig: strategy={cfg.get('strategy')}  k={cfg.get('top_k')}  "
          f"modes={cfg.get('modes')}")

    summary = report.get("summary", {})
    print(f"\n{'Mode':<18} {'Recall@K':>9} {'MRR@K':>9} {'nDCG@K':>9} "
          f"{'Lat(ms)':>9} {'FAIL':>5}")
    print("-" * 64)
    for mode, agg in summary.items():
        print(
            f"{mode:<18} "
            f"{agg.get('recall_mean', 0):.4f}    "
            f"{agg.get('mrr_mean', 0):.4f}    "
            f"{agg.get('ndcg_mean', 0):.4f}    "
            f"{agg.get('latency_ms_mean', 0):>7.1f}    "
            f"{agg.get('fail_count', 0):>3}"
        )

    if report.get("needs_human_review"):
        print("\n⚠️  Gold labels chưa duyệt – không tuyên bố mode chiến thắng.")
    print("=" * 72 + "\n")


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Đánh giá Retrieval: Recall@K, MRR@K, nDCG@K, Latency"
    )
    parser.add_argument(
        "--questions",
        default="eval/questions.json",
        help="Đường dẫn đến file questions JSON (mặc định: eval/questions.json)",
    )
    parser.add_argument(
        "--modes",
        nargs="+",
        default=["bm25", "semantic", "hybrid"],
        choices=["bm25", "semantic", "hybrid", "hybrid_rerank"],
        help="Danh sách mode cần đánh giá",
    )
    parser.add_argument(
        "--strategy",
        default="hierarchical",
        help="Chunking strategy (mặc định: hierarchical)",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Top-K cho tất cả metrics (mặc định: 5)",
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Không lưu report ra file",
    )
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = _build_parser()
    args = parser.parse_args()

    # Đảm bảo BASE_DIR trong sys.path
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    print(f"Đang đánh giá modes={args.modes}, strategy={args.strategy}, k={args.k}…")

    try:
        report = evaluate_dataset(
            questions_path=args.questions,
            modes=args.modes,
            strategy=args.strategy,
            top_k=args.k,
        )
    except Exception as exc:
        print(f"LỖI: {exc}", file=sys.stderr)
        return 1

    print_report(report)

    if not args.no_save:
        try:
            out_path = save_report(report)
            print(f"Report đã lưu: {out_path}")
        except Exception as exc:
            print(f"WARN: Không thể lưu report: {exc}", file=sys.stderr)

    # Exit code 0 ngay cả khi có fail (fail đã được ghi vào report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
