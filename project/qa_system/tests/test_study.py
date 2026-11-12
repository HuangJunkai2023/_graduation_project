import json
from dataclasses import replace
from pathlib import Path

import pytest
from docx import Document

from ocs_qa.config import Settings
from ocs_qa.store import Store
from ocs_qa.study import (QUOTAS, load_questions, validate_questions, save_review,
                          development_hash, freeze_study, blind_tasks, save_grade, save_passage_label, corpus_fingerprint, vector_fingerprint)


@pytest.fixture
def study_store(tmp_path):
    source = tmp_path / "TBT2073-2020.docx"
    doc = Document()
    doc.add_paragraph("本段是合成测试资料，零部件表面应清洁，不代表真实标准条文。")
    doc.save(source)
    settings = Settings(db_path=tmp_path/"kb.sqlite3", embedding_url="https://embedding.example/v1",
                        embedding_model="fixture", vector_weight=.5, min_coverage=.1, min_cosine=.3)
    store = Store(settings)
    store.ingest(source, allow_cloud=True)
    return store


def question(store, qid="dev-001", split="dev", category="clause"):
    record = store.records()[0]
    answerable = category != "unanswerable"
    return {"question_id": qid, "split": split, "category": category,
            "group_id": qid, "question": "合成部件表面有什么要求？", "history": [],
            "answerable": answerable, "reference_answer": "表面应清洁。" if answerable else "",
            "required_facts": ["表面应清洁"] if answerable else [],
            "evidence_units": [{"document_id": record["document_id"], "location": record["location"],
                                "quote": "零部件表面应清洁"}] if answerable else [],
            "unanswerable_reason": "指定版本不存在" if not answerable else "",
            "unanswerable_type": "missing_edition" if not answerable else "",
            "review_status": "unreviewed", "requested_standard": "TBT2073",
            "requested_edition": "2020" if answerable else "1900",
            "edition_stratum": "available" if answerable else "missing",
            "expected_action": "answer" if answerable else "refuse"}


def full_rows(store):
    dev_record = store.records()[0]
    source = store.settings.db_path.parent / "TBT2074-2020.docx"
    if not source.exists():
        doc = Document()
        doc.add_paragraph("这是测试集独立合成来源，零部件表面应清洁，不代表真实标准条文。")
        doc.save(source)
    report = store.ingest(source, allow_cloud=True)
    test_record = next(r for r in store.records() if r["document_id"] == report["document_id"])
    rows = []
    for split, quotas in QUOTAS.items():
        for category, count in quotas.items():
            for i in range(count):
                row = question(store, f"{split}-{category}-{i}", split, category)
                if not row['answerable']:
                    row['unanswerable_type'] = ('missing_edition', 'out_of_corpus', 'unrelated', 'ambiguous')[i % 4]
                record = dev_record if split == "dev" else test_record
                row["requested_standard"] = record["document"]["standard"]
                if row["answerable"]:
                    row["evidence_units"] = [{"document_id": record["document_id"], "location": record["location"],
                                               "quote": "零部件表面应清洁"}]
                row.update(review_status="approved", reviewer="Fixture reviewer", reviewed_at="2026-11-11T00:00:00+00:00")
                rows.append(row)
    return rows


def write_rows(path, rows):
    path.write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows), encoding="utf-8")


def test_source_quote_and_group_leakage(study_store):
    a = question(study_store)
    b = question(study_store, "test-001", "test")
    b["group_id"] = a["group_id"]
    b["evidence_units"][0]["quote"] = "不是原文的事实"
    check = validate_questions([a, b], study_store)
    assert not check["valid"]
    assert any("跨" in error for error in check["errors"])
    assert any("摘录" in error for error in check["errors"])


def test_evidence_leakage_ignores_different_group_ids(study_store):
    a = question(study_store)
    b = question(study_store, "test-001", "test")
    assert a["group_id"] != b["group_id"]
    b["evidence_units"][0]["quote"] = "零部件 表面 应清洁"
    check = validate_questions([a, b], study_store)
    assert not check["valid"]
    assert any("精确证据单元跨" in error for error in check["errors"])


def test_same_location_distinct_facts_not_rejected_as_exact_leakage(study_store):
    a = question(study_store)
    b = question(study_store, "test-001", "test")
    b["evidence_units"][0]["quote"] = "不代表真实标准条文"
    check = validate_questions([a, b], study_store)
    assert check["valid"]


def test_full_benchmark_checks_each_unanswerable_subtype_quota(study_store):
    rows = full_rows(study_store)
    assert validate_questions(rows, study_store, require_full=True)["valid"]
    next(q for q in rows if q['split']=='dev' and q.get('unanswerable_type')=='ambiguous')['unanswerable_type']='unrelated'
    check = validate_questions(rows, study_store, require_full=True)
    assert not check['valid']
    assert any('dev/unanswerable/ambiguous' in error for error in check['errors'])


def test_approval_requires_identity_and_full_quotas(study_store):
    row = question(study_store)
    row["review_status"] = "approved"
    check = validate_questions([row], study_store, require_full=True)
    assert not check["valid"]
    assert any("审核人" in error for error in check["errors"])
    assert any("100题" in error for error in check["errors"])
    assert validate_questions(full_rows(study_store), study_store, require_full=True, require_approved=True)["valid"]


def test_review_persists_explicit_decision_utf8_and_audit(study_store, tmp_path):
    path = tmp_path/"candidates.jsonl"
    write_rows(path, [question(study_store)])
    with pytest.raises(ValueError):
        save_review(path, "dev-001", reviewer="", status="approved", store=study_store)
    save_review(path, "dev-001", reviewer="实际核查者", status="needs_revision", notes="需核对条件", store=study_store)
    assert load_questions(path)[0]["review_status"] == "needs_revision"
    save_review(path, "dev-001", reviewer="实际核查者", status="approved", notes="已对照原文", store=study_store)
    assert load_questions(path)[0]["reviewer"] == "实际核查者"
    assert len(load_questions(path.with_suffix('.reviews.jsonl'))) == 2
    with pytest.raises(ValueError):
        save_review(path, "dev-001", reviewer="实际核查者", status="approved", edits={"split": "test"}, store=study_store)


def test_development_hash_ignores_test_edits(study_store):
    rows = [question(study_store), question(study_store, "test-001", "test")]
    before = development_hash(rows)
    rows[1]["question"] = "测试集内容改变"
    assert development_hash(rows) == before
    rows[0]["question"] = "开发集内容改变"
    assert development_hash(rows) != before


def test_passage_label_requires_explicit_human_decision(tmp_path):
    path = tmp_path/"passage_labels.jsonl"
    write_rows(path, [{"label_id":"l1", "question_id":"dev-1", "proposed_relevant":True,
                       "relevant":None, "review_status":"unreviewed"}])
    with pytest.raises(ValueError):
        save_passage_label(path, "l1", reviewer="本人", relevant=None)
    with pytest.raises(ValueError):
        save_passage_label(path, "l1", reviewer="", relevant=True)
    save_passage_label(path, "l1", reviewer="本人", relevant=False, notes="只提术语，没有所需事实")
    assert load_questions(path)[0]["relevant"] is False
    assert load_questions(path)[0]["proposed_relevant"] is True
    assert len(load_questions(path.with_suffix('.reviews.jsonl'))) == 1


def calibration(path, rows, store, **updates):
    store.embed_pending(Vectors())
    selection = path.parent/"selection.json"
    selection.write_text('{"fixture": true}', encoding="utf-8")
    data = {"status": "validated", "validated_by": "fixture calibration runner",
            "validated_at": "2026-11-11T00:00:00+00:00", "selection_evidence": "selection.json",
            "development_dataset_sha256": development_hash(rows),
            "corpus_sha256": corpus_fingerprint(store),
            "vectors_sha256": vector_fingerprint(store),
            "selected": {"vector_weight": .5, "min_coverage": .1, "min_cosine": .3}}
    data.update(updates)
    path.write_text(json.dumps(data), encoding="utf-8")


class Vectors:
    def embed(self, texts):
        return [[1., 0.] for _ in texts]


def test_freeze_refuses_drafts_missing_calibration_and_wrong_hash(study_store, tmp_path):
    rows = full_rows(study_store)
    rows[0]["review_status"] = "unreviewed"
    dataset = tmp_path/"candidates.jsonl"
    write_rows(dataset, rows)
    config = tmp_path/"calibration.json"
    calibration(config, rows, study_store)
    with pytest.raises(ValueError, match="尚未人工通过"):
        freeze_study(dataset, study_store, config, tmp_path/"freeze")
    assert not (tmp_path/"freeze").exists()
    rows[0]["review_status"] = "approved"
    write_rows(dataset, rows)
    calibration(config, rows, study_store, status="unverified")
    with pytest.raises(ValueError, match="校准"):
        freeze_study(dataset, study_store, config, tmp_path/"freeze")
    calibration(config, rows, study_store, development_dataset_sha256="changed")
    with pytest.raises(ValueError, match="开发集已改变"):
        freeze_study(dataset, study_store, config, tmp_path/"freeze")


def test_freeze_validated_snapshot_has_no_key_and_is_immutable(study_store, tmp_path):
    rows = full_rows(study_store)
    dataset = tmp_path/"candidates.jsonl"
    write_rows(dataset, rows)
    config = tmp_path/"calibration.json"
    calibration(config, rows, study_store)
    study_store.embed_pending(Vectors())
    manifest = freeze_study(dataset, study_store, config, tmp_path/"freeze")
    assert manifest["main_execution_slots"] == 400
    assert manifest["configurations"]["A1"]["edition_filter"] is False
    assert "chat_key" not in manifest["config"]
    assert len(load_questions(tmp_path/"freeze/questions.jsonl")) == 100
    with pytest.raises(ValueError, match="不能覆盖"):
        freeze_study(dataset, study_store, config, tmp_path/"freeze")
    # A post-freeze label edit leaves the immutable copied questions intact.
    rows[0]["question"] = "之后修改的候选题"
    write_rows(dataset, rows)
    assert load_questions(tmp_path/"freeze/questions.jsonl")[0]["question"] != rows[0]["question"]


def test_freeze_rejects_untuned_weight(study_store, tmp_path):
    rows = full_rows(study_store)
    dataset = tmp_path/"candidates.jsonl"; write_rows(dataset, rows)
    config = tmp_path/"calibration.json"
    calibration(config, rows, study_store, selected={"vector_weight": .6, "min_coverage": .1, "min_cosine": .3})
    with pytest.raises(ValueError, match="网格"):
        freeze_study(dataset, study_store, config, tmp_path/"freeze")
    calibration(config, rows, study_store)
    changed = Store(replace(study_store.settings, top_k=3))
    with pytest.raises(ValueError, match="Top-K"):
        freeze_study(dataset, changed, config, tmp_path/"freeze")


def test_blind_dedup_requires_identical_evidence_and_retains_slots(tmp_path):
    a = {"question_id": "q1", "answerable": True, "result": {"answer": "一样的答案", "status": "answered",
         "claims": [{"text": "事实", "citations": []}], "sources": [{"document_id": "doc1", "location": "p1", "text": "依据"}]}}
    b = json.loads(json.dumps(a))
    c = json.loads(json.dumps(a)); c["result"]["sources"][0]["location"] = "p2"
    paths = [tmp_path/f"{name}.jsonl" for name in ['B1','B2','B3']]
    for path, row in zip(paths, [a,b,c]): write_rows(path, [row])
    tasks = blind_tasks(paths)
    assert len(tasks) == 2
    assert sorted(len(t["run_slots"]) for t in tasks) == [1,2]
    assert len({t["blind_id"] for t in tasks}) == 2


def test_grade_requires_human_reason_and_each_claim(tmp_path):
    task = {"blind_id":"blind", "question_id":"q1", "answerable":True,
            "result":{"claims":[{"text":"事实"}]}, "run_slots":[{"run_file":"B1.jsonl", "question_id":"q1"}]}
    base = dict(reviewer="本人", correct=True, claim_support=[True], wrong_edition=False,
                justified_refusal=None, false_refusal=False, failure_type="none", reason="原文充分支持")
    path = tmp_path/"grades.jsonl"
    with pytest.raises(ValueError, match="逐条"):
        save_grade(path, task, **{**base, "claim_support":[]})
    with pytest.raises(ValueError, match="理由"):
        save_grade(path, task, **{**base, "reason":""})
    with pytest.raises(ValueError, match="可回答题"):
        save_grade(path, task, **{**base, "correct":None})
    save_grade(path, task, **base)
    assert load_questions(path)[0]["correct"] is True


def test_blind_tasks_keep_the_frozen_gold_not_mutable_candidate(tmp_path):
    row = {"question_id": "test-001", "answerable": True,
           "question_snapshot": {"question_id": "test-001", "question": "Frozen question",
                                 "reference_answer": "Frozen reference", "required_facts": ["Frozen fact"]},
           "result": {"answer": "same", "status": "answered", "claims": [], "sources": []}}
    other = json.loads(json.dumps(row))
    other['question_snapshot']['reference_answer'] = 'Different frozen reference'
    paths = [tmp_path / 'B1.jsonl', tmp_path / 'B2.jsonl']
    for path, value in zip(paths, [row, other]): write_rows(path, [value])
    tasks = blind_tasks(paths)
    assert len(tasks) == 2
    assert {task['question_snapshot']['reference_answer'] for task in tasks} == {'Frozen reference', 'Different frozen reference'}


def test_review_ui_starts_without_model_calls(study_store, tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from ocs_qa.api import ModelClient
    def forbidden(*args, **kwargs):
        raise AssertionError("Review UI must not call external model services")
    monkeypatch.setattr(ModelClient, "embed", forbidden)
    monkeypatch.setattr(ModelClient, "chat", forbidden)
    # An empty default corpus is a legitimate readiness page, not a model call.
    app = Path(__file__).resolve().parents[1]/"review_app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    assert not at.exception
    assert any("核查" in t.value for t in at.title)


def test_review_ui_explicit_save_uses_isolated_fixture(study_store, tmp_path):
    from streamlit.testing.v1 import AppTest
    dataset = tmp_path/"candidates.jsonl"
    write_rows(dataset, [question(study_store)])
    app = Path(__file__).resolve().parents[1]/"review_app.py"
    at = AppTest.from_file(str(app), default_timeout=30).run()
    at.sidebar.text_input[0].set_value(str(dataset))
    at.sidebar.text_input[1].set_value(str(study_store.settings.db_path))
    at.sidebar.text_input[2].set_value("Fixture reviewer")
    at.run()
    assert not at.exception
    next(s for s in at.selectbox if s.label == "本次决定").set_value("approved")
    next(b for b in at.button if b.label == "保存本次人工决定").click().run()
    assert not at.exception
    saved = load_questions(dataset)[0]
    assert saved["review_status"] == "approved"
    assert saved["reviewer"] == "Fixture reviewer"
    assert saved["reviewed_at"]


def test_candidate_rebuild_preserves_existing_human_decisions(tmp_path):
    import importlib.util
    source = Path(__file__).resolve().parents[1] / 'tools/build_benchmark.py'
    spec = importlib.util.spec_from_file_location('benchmark_builder_fixture', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    build = module.build
    destination = tmp_path / "candidates.jsonl"
    write_rows(destination, [{"question_id": "dev-001", "review_status": "approved",
                              "reviewer": "Fixture reviewer", "reviewed_at": "2026-11-12T00:00:00+00:00"}])
    before = destination.read_bytes()
    with pytest.raises(ValueError, match="human review history"):
        build(tmp_path / "absent.sqlite3", tmp_path / "absent.json", destination, tmp_path / "public")
    assert destination.read_bytes() == before
    write_rows(destination, [{"question_id": "dev-001", "review_status": "unreviewed"}])
    destination.with_suffix('.reviews.jsonl').write_text('{}\n', encoding="utf-8")
    with pytest.raises(ValueError, match="human review history"):
        build(tmp_path / "absent.sqlite3", tmp_path / "absent.json", destination, tmp_path / "public")


def test_blind_review_ui_displays_claim_citations_and_frozen_gold(study_store, tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from ocs_qa.api import ModelClient
    monkeypatch.setattr(ModelClient, "_post", lambda *a, **kw: pytest.fail("Review UI cannot call models"))
    q = question(study_store)
    q['question'] = 'Frozen reference question'
    dataset = tmp_path / 'benchmark/candidates.jsonl'
    dataset.parent.mkdir()
    write_rows(dataset, [q])
    record = study_store.records()[0]
    row = {'question_id': q['question_id'], 'answerable': True, 'question_snapshot': q,
           'result': {'status': 'answered', 'answer': 'Fixture response',
                      'claims': [{'text': '表面应清洁', 'citations': [{'source': 3, 'quote': '零部件表面应清洁'}]}],
                      'sources': [{'source': 3, 'document_id': record['document_id'],
                                   'location': record['location'], 'text': record['text']}]}}
    result = tmp_path / 'results/B1.jsonl'
    result.parent.mkdir()
    write_rows(result, [row])
    # This private export must not be mistaken for a sixth result file.
    write_rows(result.parent / 'blind_tasks.private.jsonl', [{'private': True}])
    app_path = Path(__file__).resolve().parents[1] / 'review_app.py'
    source = app_path.read_text(encoding='utf-8').replace('ROOT = APP_ROOT / "runtime/research"', f'ROOT = Path({str(tmp_path)!r})')
    at = AppTest.from_string(source, default_timeout=30).run()
    assert not at.exception
    assert any('来源 3' in item.value for item in at.markdown)
    assert any('引文 1 → 来源 3' in item.value for item in at.caption)
    assert any(item.value == '零部件表面应清洁' for item in at.text)
    assert any(item.label == '查看冻结gold证据与原文位置' for item in at.expander)
    assert next(m.value for m in at.metric if m.label == '盲评进度') == '0 / 1'
