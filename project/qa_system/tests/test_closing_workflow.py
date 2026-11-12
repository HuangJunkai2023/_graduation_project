"""Regression coverage for delegated source review and separate experiment attempts."""
import json

from ocs_qa.study import freeze_study, load_questions, save_review
from ocs_qa.study_run import _budget_review, run_development, run_frozen, run_recovery
from ocs_qa.pipeline import resolve_query
from test_study import study_store, full_rows, write_rows, calibration
from test_study_run import frozen, budget, FakePipeline


def test_assistant_review_retains_actual_attribution(study_store, tmp_path):
    rows = full_rows(study_store)
    for row in rows:
        row.update(review_method='assistant_source_review', reviewer='Codex fixture')
    dataset = tmp_path / 'questions.jsonl'
    write_rows(dataset, rows)
    save_review(dataset, rows[0]['question_id'], reviewer='Codex fixture', status='approved',
                review_method='assistant_source_review', notes='Synthetic source review', store=study_store)
    selected = tmp_path / 'calibration.json'
    calibration(selected, load_questions(dataset), study_store)
    manifest = freeze_study(dataset, study_store, selected, tmp_path / 'freeze')
    assert manifest['human_reviews_complete'] is False
    assert manifest['review_methods'] == {'assistant_source_review': 100}
    assert load_questions(dataset.with_suffix('.reviews.jsonl'))[0]['review_method'] == 'assistant_source_review'


def test_development_uses_only_twenty_questions_and_resumes(frozen, budget, tmp_path, monkeypatch):
    store, freeze, _, _ = frozen
    monkeypatch.setattr('ocs_qa.study_run.Pipeline', FakePipeline)
    FakePipeline.calls = []
    FakePipeline.fail_at = None
    output = tmp_path / 'development'
    summary = run_development(freeze / 'questions.jsonl', store, output, budget, client=object())
    assert summary['total_slots'] == 100
    assert summary['formal_test_slots'] == 0
    assert all(row['split'] == 'dev' for row in load_questions(output / 'B1.jsonl'))
    run_development(freeze / 'questions.jsonl', store, output, budget, client=object())
    assert len(FakePipeline.calls) == 100


def test_recovery_keeps_primary_bytes_and_only_recovers_failures(frozen, budget, tmp_path, monkeypatch):
    store, freeze, _, _ = frozen
    monkeypatch.setattr('ocs_qa.study_run.Pipeline', FakePipeline)
    FakePipeline.calls = []
    FakePipeline.fail_at = None
    output = tmp_path / 'formal'
    run_frozen(freeze, store, output, budget, client=object())
    before = (output / 'B1.jsonl').read_bytes()
    summary = run_recovery(freeze, store, output, budget, client=object())
    assert summary['total_slots'] == 1
    assert len(FakePipeline.calls) == 401
    assert (output / 'B1.jsonl').read_bytes() == before
    recovered = load_questions(output / 'recovery/attempt-02/B1.jsonl')
    assert recovered[0]['attempt_id'] == 2
    run_recovery(freeze, store, output, budget, client=object())
    assert len(FakePipeline.calls) == 401


def test_unknown_history_can_use_explicit_budget_allocation(budget):
    row = json.loads(budget.read_text(encoding='utf-8'))
    row.update(historical_cost_unknown=True, spent_gbp=None, historical_cost_reserve_gbp=35,
               reserve_basis='budget allocation, not observed spending', cost_evidence=['fixture ledger'])
    budget.write_text(json.dumps(row), encoding='utf-8')
    accepted = _budget_review(budget)
    assert accepted['historical_cost_unknown'] is True
    assert accepted['spent_gbp'] is None


def test_conflicting_bare_edition_clarifies_but_a1_keeps_its_ablation():
    question = '依据TB/T2073-2020回答，但适用版本又是2010版，应先采用哪个版本？'
    assert resolve_query(question, [])[1] == 'clarify_edition'
    assert resolve_query(question, [], edition_filter=False)[1] is None
    assert resolve_query('依据TB/T2073-2020回答', [])[1] is None


def test_long_followups_inherit_the_existing_standard_topic():
    history = [{'question': '请查阅Q/CR1001-2023中的预埋槽道要求。',
                'resolved_query': 'Q/CR1001-2023 预埋槽道要求'}]
    questions = [
        '那采用热浸镀锌时，按哪个标准进行，镀锌后表面不应出现什么？',
        '那槽道本体和锚杆的热浸镀锌应符合哪份标准的什么等级，最小厚度是多少？',
        '那么T型螺栓及配用螺母、垫圈的热浸镀锌应符合哪份标准的什么等级，最小厚度是多少？',
    ]
    for question in questions:
        resolved, error = resolve_query(question, history)
        assert error is None
        assert resolved.startswith('Q/CR1001-2023 预埋槽道要求')
        assert question in resolved
        assert resolve_query(question, [])[1] == 'clarify_context'
    new_topic = '那依据TB/T2073-2020，表面质量有什么要求？'
    assert resolve_query(new_topic, history) == (new_topic, None)


def test_activate_selected_parameters_preserves_other_configuration(frozen, tmp_path, monkeypatch):
    from ocs_qa.calibration import activate_calibration
    store, freeze, _, _ = frozen
    monkeypatch.setattr('ocs_qa.calibration.APP_ROOT', tmp_path)
    (tmp_path / '.env').write_text('FIXTURE_SETTING=keep\nVECTOR_WEIGHT=0.6\n', encoding='utf-8')
    result = activate_calibration(freeze / 'calibration.json', freeze / 'questions.jsonl', store)
    assert result['status'] == 'activated'
    contents = (tmp_path / '.env').read_text(encoding='utf-8')
    assert 'FIXTURE_SETTING=keep' in contents
    assert 'VECTOR_WEIGHT=0.5' in contents
    assert 'MIN_COSINE_SIMILARITY=0.3' in contents
    assert list((tmp_path / 'runtime/config-backups').iterdir())
