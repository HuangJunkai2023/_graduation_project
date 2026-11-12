"""Source-bound benchmark review, blinded grading and fail-closed study freeze.

These utilities do not call model services or automatically approve any label.
Private question text, review events and frozen snapshots belong under runtime/.
"""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
import hashlib
import json
import math
import os
import random
import re
import platform
from importlib.metadata import version

from .config import APP_ROOT
from .pipeline import SYSTEM, compact

QUOTAS = {
    "dev": {"clause": 6, "term": 3, "edition": 4, "follow_up": 3, "unanswerable": 4},
    "test": {"clause": 24, "term": 12, "edition": 16, "follow_up": 12, "unanswerable": 16},
}
REVIEW_STATES = {"unreviewed", "approved", "needs_revision"}
STRATA = {"available", "missing", "ambiguous", "not_applicable"}
UNANSWERABLE_TYPES = ("missing_edition", "out_of_corpus", "unrelated", "ambiguous")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def development_hash(rows):
    """Hash reviewed development records only, independently of test rows."""
    return canonical_hash(sorted((q for q in rows if q.get("split") == "dev"),
                                 key=lambda q: q["question_id"]))


def load_questions(path):
    path = Path(path)
    if not path.exists():
        return []
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"第{line_number}行不是有效JSON。") from exc
            if not isinstance(row, dict):
                raise ValueError(f"第{line_number}行必须为JSON对象。")
            rows.append(row)
    return rows


def _atomic_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                            prefix=path.name + ".", suffix=".tmp", delete=False) as handle:
        tmp = Path(handle.name)
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _review_identity(reviewer):
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("请填写实际审核人姓名。")
    return reviewer.strip()


def _source_index(store):
    index = {}
    with store.connect() as db:
        records = [json.loads(r[0]) for r in db.execute("SELECT payload FROM chunks ORDER BY id")]
    for record in records:
        index.setdefault((record["document_id"], record["location"]), []).append(record)
    return index


def source_units(store, document_id, location):
    """Read only source text for a location; avoid loading the whole vector index."""
    with store.connect() as db:
        records = [json.loads(r[0]) for r in db.execute("SELECT payload FROM chunks WHERE document_id=? ORDER BY id", (document_id,))]
    return [r for r in records if r.get("location") == location]


def validate_questions(rows, store=None, *, require_full=False, require_approved=False):
    """Return explicit schema/source/quota errors; empty or draft sets never freeze."""
    errors = []
    counts = Counter()
    unanswerable_counts = Counter()
    ids = set()
    groups = {}
    evidence_splits = {}
    source_index = _source_index(store) if store is not None else None
    for number, q in enumerate(rows, 1):
        label = q.get("question_id", f"row-{number}")
        if not isinstance(q.get("question_id"), str) or not q["question_id"].strip():
            errors.append(f"{label}: question_id缺失。")
        else:
            if q["question_id"] in ids:
                errors.append(f"{label}: question_id重复。")
            ids.add(q["question_id"])
        if q.get("split") not in QUOTAS:
            errors.append(f"{label}: split必须为dev/test。")
        elif q.get("category") not in QUOTAS[q["split"]]:
            errors.append(f"{label}: category无效。")
        else:
            counts[(q["split"], q["category"])] += 1
        group = q.get("group_id")
        if not isinstance(group, str) or not group.strip():
            errors.append(f"{label}: group_id缺失。")
        elif group in groups and groups[group] != q.get("split"):
            errors.append(f"{label}: 同一group_id跨开发/测试划分。")
        else:
            groups[group] = q.get("split")
        if not isinstance(q.get("question"), str) or not q["question"].strip():
            errors.append(f"{label}: question缺失。")
        if not isinstance(q.get("history"), list):
            errors.append(f"{label}: history须为列表。")
        if type(q.get("answerable")) is not bool:
            errors.append(f"{label}: answerable须明确为布尔值。")
        if q.get("review_status") not in REVIEW_STATES:
            errors.append(f"{label}: review_status无效。")
        if q.get("review_status") == "approved":
            if not q.get("reviewer") or not q.get("reviewed_at"):
                errors.append(f"{label}: approved必须保留审核人与时间。")
        if require_approved and q.get("review_status") != "approved":
            errors.append(f"{label}: 尚未人工通过。")
        if q.get("edition_stratum") not in STRATA:
            errors.append(f"{label}: edition_stratum无效。")
        if q.get("expected_action") not in {"answer", "refuse", "clarify"}:
            errors.append(f"{label}: expected_action无效。")
        for field in ["requested_standard", "requested_edition", "unanswerable_reason"]:
            if not isinstance(q.get(field), str):
                errors.append(f"{label}: {field}须为字符串。")
        facts, evidence = q.get("required_facts"), q.get("evidence_units")
        if not isinstance(facts, list) or any(not isinstance(v, str) or not v.strip() for v in facts):
            errors.append(f"{label}: required_facts须为非空文本列表（不可答允许空列表）。")
        if not isinstance(evidence, list):
            errors.append(f"{label}: evidence_units须为列表。")
            evidence = []
        if q.get("answerable") is True:
            if not facts or len(facts) > 3 or not evidence or not q.get("reference_answer"):
                errors.append(f"{label}: 可回答题需1–3项必要事实、参考答案及证据。")
            if q.get("category") == "unanswerable" or q.get("expected_action") != "answer":
                errors.append(f"{label}: 可回答性、类别与预期动作冲突。")
        elif q.get("answerable") is False:
            subtype = q.get("unanswerable_type")
            if subtype not in UNANSWERABLE_TYPES:
                errors.append(f"{label}: 不可回答题须明确unanswerable_type。")
            else:
                unanswerable_counts[(q.get("split"), subtype)] += 1
            if evidence or not q.get("unanswerable_reason") or q.get("expected_action") == "answer":
                errors.append(f"{label}: 不可回答题不得有gold证据，须说明理由及非作答动作。")
            if q.get("category") != "unanswerable":
                errors.append(f"{label}: 不可回答题应计入unanswerable类别。")
        for unit in evidence:
            if not isinstance(unit, dict) or not all(isinstance(unit.get(k), str) and unit[k].strip()
                                                   for k in ["document_id", "location", "quote"]):
                errors.append(f"{label}: 证据需document_id/location/quote。")
                continue
            evidence_key = (unit["document_id"], unit["location"], compact(unit["quote"]))
            if evidence_key in evidence_splits and evidence_splits[evidence_key] != q.get("split"):
                errors.append(f"{label}: 同一精确证据单元跨开发/测试划分，即使group_id不同也不允许。")
            else:
                evidence_splits[evidence_key] = q.get("split")
            if source_index is not None:
                hits = source_index.get((unit["document_id"], unit["location"]), [])
                if not any(compact(unit["quote"]) in compact(hit["text"]) for hit in hits):
                    errors.append(f"{label}: gold摘录无法在对应文档位置的块中核对。")
    if require_full:
        if len(rows) != 100:
            errors.append(f"需100题，当前{len(rows)}题。")
        for split, quotas in QUOTAS.items():
            for category, expected in quotas.items():
                if counts[(split, category)] != expected:
                    errors.append(f"{split}/{category}: 应{expected}题，实际{counts[(split, category)]}题。")
            for subtype in UNANSWERABLE_TYPES:
                expected = 1 if split == "dev" else 4
                if unanswerable_counts[(split, subtype)] != expected:
                    errors.append(f"{split}/unanswerable/{subtype}: 应{expected}题，实际{unanswerable_counts[(split, subtype)]}题。")
    return {"valid": not errors, "errors": errors, "questions": len(rows),
            "approved": sum(q.get("review_status") == "approved" for q in rows),
            "counts": {f"{s}/{c}": n for (s, c), n in sorted(counts.items())}}


def save_review(path, question_id, *, reviewer, status, notes="", edits=None, store=None):
    """Persist one deliberate human decision, with append-only review history."""
    reviewer = _review_identity(reviewer)
    if status not in REVIEW_STATES:
        raise ValueError("审核状态无效。")
    rows = load_questions(path)
    selected = next((q for q in rows if q.get("question_id") == question_id), None)
    if selected is None:
        raise ValueError("题号不存在。")
    before = canonical_hash(selected)
    allowed = {"question", "history", "reference_answer", "required_facts", "evidence_units",
               "unanswerable_reason", "requested_standard", "requested_edition",
               "edition_stratum", "expected_action"}
    if edits:
        unknown = set(edits) - allowed
        if unknown:
            raise ValueError("此审核接口不能修改题号、分组、划分或配额。")
        selected.update(edits)
    selected.update(review_status=status, reviewer=reviewer, reviewed_at=utc_now(), review_notes=notes)
    checked = validate_questions(rows, store)
    if not checked["valid"]:
        raise ValueError("\n".join(checked["errors"][:10]))
    _atomic_jsonl(path, rows)
    event = {"question_id": question_id, "reviewer": reviewer, "reviewed_at": selected["reviewed_at"],
             "status": status, "notes": notes, "before_sha256": before,
             "after_sha256": canonical_hash(selected)}
    with Path(path).with_suffix(".reviews.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return selected


def corpus_fingerprint(store):
    """Portable evidence fingerprint: exclude local source paths and secrets."""
    with store.connect() as db:
        records = [{**json.loads(chunk), "document": json.loads(document)} for chunk, document in db.execute(
            "SELECT c.payload,d.payload FROM chunks c JOIN documents d ON c.document_id=d.id ORDER BY c.id")]
    return canonical_hash(sorted(({
        "id": r["id"], "document_id": r["document_id"], "text": r["text"],
        "location": r["location"], "document": {k: r["document"].get(k)
           for k in ["id", "standard", "year", "publication_status"]},
    } for r in records), key=lambda r: r["id"]))


def vector_fingerprint(store):
    """Freeze the actual numeric index, not just the provider/model alias."""
    with store.connect() as db:
        rows = [(chunk_id, identity, json.loads(payload)) for chunk_id, identity, payload in
                db.execute('SELECT chunk_id,identity,payload FROM vectors ORDER BY chunk_id')]
    return canonical_hash(rows)


def runtime_identity():
    return {'python': platform.python_version(), 'platform': platform.system(),
            'packages': {name: version(name) for name in
                         ['numpy', 'pymupdf', 'python-docx', 'python-dotenv', 'httpx', 'streamlit', 'jieba']}}


def save_passage_label(path, label_id, *, reviewer, relevant, notes=""):
    """Record human passage support labels; never promote proposed_relevant."""
    reviewer = _review_identity(reviewer)
    if type(relevant) is not bool:
        raise ValueError("请明确判断候选段落是否支持该问题。")
    rows = load_questions(path)
    row = next((r for r in rows if r.get("label_id") == label_id), None)
    if row is None:
        raise ValueError("候选证据编号不存在。")
    before = canonical_hash(row)
    row.update(relevant=relevant, review_status="approved", reviewer=reviewer,
               reviewed_at=utc_now(), review_reason=notes)
    _atomic_jsonl(path, rows)
    event = {"label_id": label_id, "reviewer": reviewer, "reviewed_at": row["reviewed_at"],
             "relevant": relevant, "notes": notes, "before_sha256": before,
             "after_sha256": canonical_hash(row)}
    with Path(path).with_suffix(".reviews.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return row


def freeze_study(dataset_path, store, calibration_path, output_dir):
    rows = load_questions(dataset_path)
    check = validate_questions(rows, store, require_full=True, require_approved=True)
    if not check["valid"]:
        raise ValueError("题集不能冻结：" + "；".join(check["errors"][:10]))
    calibration = json.loads(Path(calibration_path).read_text(encoding="utf-8-sig"))
    if (calibration.get("status") != "validated" or not calibration.get("validated_by")
            or not calibration.get("validated_at") or not calibration.get("selection_evidence")):
        raise ValueError("须先完成开发集校准并核对选择依据。")
    if calibration.get("development_dataset_sha256") != development_hash(rows):
        raise ValueError("开发集已改变，需重新核对校准记录。")
    if calibration.get("corpus_sha256") != corpus_fingerprint(store):
        raise ValueError("语料已改变，需重新核对校准记录。")
    if calibration.get('vectors_sha256') != vector_fingerprint(store):
        raise ValueError('向量已改变，需重新核对校准记录。')
    evidence_path = Path(calibration["selection_evidence"])
    if not evidence_path.is_absolute():
        evidence_path = Path(calibration_path).parent / evidence_path
    if not evidence_path.is_file():
        raise ValueError("开发集选择依据文件不存在。")
    selected = calibration.get("selected", {})
    if (selected.get("vector_weight") not in {0.25, 0.50, 0.75}
            or selected.get("min_coverage") not in {0.05, 0.10, 0.20}
            or selected.get("min_cosine") not in {0.20, 0.30, 0.40, 0.50}):
        raise ValueError("选择的参数不在预先约定网格中。")
    s = store.settings
    if s.top_k != 5:
        raise ValueError("正式研究Top-K必须固定为5。")
    if any(not math.isclose(getattr(s, key), value) for key, value in selected.items()):
        raise ValueError("研究库配置与已选择参数不一致。")
    with store.connect() as db:
        count = db.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
        vector_count = db.execute("SELECT COUNT(*) FROM chunks c JOIN vectors v ON c.id=v.chunk_id WHERE v.identity=?", (s.embedding_identity,)).fetchone()[0]
    if not count:
        raise ValueError("研究知识库为空。")
    if vector_count != count:
        raise ValueError("研究语料尚未全部使用当前模型构建向量。")
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise ValueError("冻结目录已存在，请使用新版本目录，不能覆盖。")
    code_files = list((APP_ROOT / "ocs_qa").rglob("*.py")) + [APP_ROOT / "pyproject.toml"]
    lockfile = APP_ROOT / 'requirements-lock-windows.txt'
    if lockfile.exists(): code_files.append(lockfile)
    for directory in [APP_ROOT / "ocs_qa/resources", APP_ROOT / "resources"]:
        if directory.exists():
            code_files.extend(p for p in directory.rglob("*") if p.is_file())
    files = {str(p.relative_to(APP_ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(set(code_files))}
    config = {k: getattr(s, k) for k in ["chat_url", "chat_model", "embedding_url", "embedding_model",
              "timeout", "chunk_size", "chunk_overlap", "top_k", "vector_weight", "min_coverage", "min_cosine"]}
    manifest = {"schema": "ocs-study-freeze.v1", "created_at": utc_now(),
        "dataset_sha256": canonical_hash(rows), "development_dataset_sha256": development_hash(rows),
        "corpus_sha256": corpus_fingerprint(store), "vectors_sha256": vector_fingerprint(store), "config": config,
        "runtime_identity": runtime_identity(),
        "prompt_sha256": hashlib.sha256(SYSTEM.encode("utf-8")).hexdigest(),
        "code_sha256": files, "calibration_sha256": canonical_hash(calibration),
        "validation": check, "configurations": {
          "B1": {"mode": "bm25", "edition_filter": True, "evidence_check": True},
          "B2": {"mode": "dense", "edition_filter": True, "evidence_check": True},
          "B3": {"mode": "hybrid", "edition_filter": True, "evidence_check": True},
          "A1": {"mode": "hybrid", "edition_filter": False, "evidence_check": True},
          "A2": {"mode": "hybrid", "edition_filter": True, "evidence_check": False}},
        "main_execution_slots": 400, "human_reviews_complete": True}
    output_dir.mkdir(parents=True)
    _atomic_jsonl(output_dir / "questions.jsonl", rows)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "calibration.json").write_text(json.dumps(calibration, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def blind_tasks(run_paths, *, seed=20261111):
    """Group only byte-equivalent answer/evidence tuples; do not expose labels."""
    groups = {}
    for path in sorted(map(Path, run_paths)):
        for row in load_questions(path):
            result = row.get("result", {})
            sources = [{k: s.get(k) for k in ["document_id", "location", "text"]}
                       for s in result.get("sources", [])]
            fingerprint = canonical_hash({"question_id": row.get("question_id"),
                "question_snapshot": row.get("question_snapshot"),
                "answer": result.get("answer"), "claims": result.get("claims", []),
                "sources": sources, "status": result.get("status")})
            if fingerprint not in groups:
                groups[fingerprint] = {"blind_id": fingerprint[:16], "question_id": row.get("question_id"),
                    "answerable": row.get("answerable"), "reference_answer": row.get("reference_answer"),
                    "question_snapshot": row.get("question_snapshot"),
                    "result": result, "run_slots": []}
            groups[fingerprint]["run_slots"].append({"run_file": path.name, "question_id": row.get("question_id")})
    tasks = list(groups.values())
    random.Random(seed).shuffle(tasks)
    return tasks


def save_grade(path, task, *, reviewer, correct, claim_support, wrong_edition,
               justified_refusal, false_refusal, failure_type, reason):
    reviewer = _review_identity(reviewer)
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("请填写原文核查依据或判分理由。")
    for value in [correct, wrong_edition, justified_refusal, false_refusal]:
        if value is not None and type(value) is not bool:
            raise ValueError("评分必须为布尔值或明确的不适用。")
    claims = task.get("result", {}).get("claims", [])
    if task.get("answerable") is True and (type(correct) is not bool or type(false_refusal) is not bool):
        raise ValueError("可回答题必须明确判断正确性和误拒答，不能记不适用。")
    if task.get("answerable") is False and type(justified_refusal) is not bool:
        raise ValueError("不可回答题必须明确判断是否合理拒答。")
    if len(claim_support) != len(claims) or any(type(v) is not bool for v in claim_support):
        raise ValueError("需逐条判断已展示claim的证据支撑。")
    grade = {"blind_id": task["blind_id"], "question_id": task["question_id"],
             "reviewer": reviewer, "reviewed_at": utc_now(), "correct": correct,
             "claim_support": claim_support, "wrong_edition": wrong_edition,
             "justified_refusal": justified_refusal, "false_refusal": false_refusal,
             "failure_type": failure_type, "reason": reason.strip(), "run_slots": task["run_slots"]}
    rows = load_questions(path)
    rows = [r for r in rows if r.get("blind_id") != task["blind_id"]] + [grade]
    _atomic_jsonl(path, rows)
    with Path(path).with_suffix(".events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(grade, ensure_ascii=False) + "\n")
    return grade
