"""Read-only corpus and cached development checks for the three journal drafts."""
from collections import Counter
from contextlib import contextmanager
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess

import numpy as np
from ocs_qa.config import Settings
from ocs_qa.evaluation import retrieval_metrics
from ocs_qa.pipeline import resolve_query
from ocs_qa.retrieval import Retriever, normalize
from ocs_qa.study import canonical_hash, corpus_fingerprint, load_questions, vector_fingerprint

ROOT = Path(__file__).resolve().parents[4]
RESEARCH = ROOT / 'project/qa_system/runtime/research'
EVIDENCE = Path(__file__).resolve().parents[1]


class ReadOnlyStore:
    def __init__(self, settings):
        self.settings = settings

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.settings.db_path.resolve().as_uri() + '?mode=ro', uri=True)
        try:
            yield connection
        finally:
            connection.close()

    def documents(self):
        with self.connect() as connection:
            return [json.loads(row[0]) for row in connection.execute('SELECT payload FROM documents ORDER BY id')]

    def records(self):
        with self.connect() as connection:
            rows = connection.execute('SELECT c.payload,d.payload,v.identity,v.payload FROM chunks c '
                                      'JOIN documents d ON c.document_id=d.id '
                                      'LEFT JOIN vectors v ON c.id=v.chunk_id ORDER BY c.id').fetchall()
        return [{**json.loads(chunk), 'document': json.loads(document), 'vector_identity': identity,
                 'vector': json.loads(vector) if vector else None} for chunk, document, identity, vector in rows]


class ExistingQueryVectors:
    def __init__(self, settings):
        self.settings = settings
        self.keys = set()

    def embed(self, texts):
        vectors = []
        for text in texts:
            key = canonical_hash([self.settings.embedding_identity, text])
            path = RESEARCH / 'query_vectors' / (key + '.json')
            vector = json.loads(path.read_text(encoding='utf-8'))
            assert len(vector) == 1024 and np.isfinite(vector).all() and np.linalg.norm(vector) > 0
            self.keys.add(key)
            vectors.append(vector)
        return vectors


def save(week, name, result):
    target = EVIDENCE / f'week{week}' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    manifest = json.loads((RESEARCH / 'freezes/closing-v1/manifest.json').read_text(encoding='utf-8'))
    settings = Settings(db_path=RESEARCH / 'kb.sqlite3', **manifest['config'])
    store = ReadOnlyStore(settings)
    documents, records = store.documents(), store.records()
    matrix = np.asarray([row['vector'] for row in records])
    assert matrix.shape == (3341, 1024) and np.isfinite(matrix).all()
    assert (np.linalg.norm(matrix, axis=1) > 0).all()
    assert all(row['vector_identity'] == settings.embedding_identity for row in records)
    assert all(hashlib.sha256(Path(row['path']).read_bytes()).hexdigest() == row['id'] for row in documents)
    corpus_hash, vector_hash = corpus_fingerprint(store), vector_fingerprint(store)
    assert corpus_hash == manifest['corpus_sha256'] and vector_hash == manifest['vectors_sha256']
    dev = load_questions(RESEARCH / 'closing_review/dev/dev_reviewed.jsonl')
    assert len(dev) == 20 and all(row['split'] == 'dev' for row in dev)
    assert sum(row['answerable'] for row in dev) == 16
    client = ExistingQueryVectors(settings)
    retriever = Retriever(store, client)
    scores = {mode: [] for mode in ['bm25', 'dense', 'hybrid']}
    comparisons, formula_checks, cosine_checks = [], 0, 0
    for question in dev:
        if not question['answerable']:
            continue
        query, error = resolve_query(question['question'], question.get('history', []))
        assert error is None
        row = {'question_id': question['question_id'], 'rankings': {}}
        for mode in scores:
            result = retriever.search(query, mode=mode)
            assert result['status'] == 'retrieved'
            metric = retrieval_metrics(result['sources'], question['evidence_units'])
            scores[mode].append(metric)
            row['rankings'][mode] = [source['id'] for source in result['sources']]
            if mode == 'hybrid':
                for source in result['sources']:
                    expected = .5 * source['bm25_normalized'] + .5 * source['dense_normalized']
                    assert abs(source['score'] - expected) < 1e-12
                    formula_checks += 1
            if mode == 'dense':
                query_vector = np.asarray(client.embed([query])[0])
                source = result['sources'][0]
                vector = next(record['vector'] for record in records if record['id'] == source['id'])
                cosine = np.dot(query_vector, vector) / (np.linalg.norm(query_vector) * np.linalg.norm(vector))
                assert abs(cosine - source['vector_score']) < 1e-12
                cosine_checks += 1
        comparisons.append(row)
    first_query, _ = resolve_query(dev[0]['question'], dev[0].get('history', []))
    reloaded = Retriever(ReadOnlyStore(settings), ExistingQueryVectors(settings)).search(first_query, mode='dense')
    assert [row['id'] for row in reloaded['sources']] == comparisons[0]['rankings']['dense']
    assert normalize({}) == {}
    assert normalize({0: 2, 1: 2}) == {0: 1., 1: 1.}
    assert normalize({0: 0, 1: 0}) == {0: 0., 1: 0.}
    assert normalize({0: 2, 1: 4}) == {0: 0., 1: 1.}
    checked_at = datetime.now(timezone.utc)
    common = {'checked_at': checked_at.isoformat(),
              'activity_date_local': checked_at.astimezone(timezone(timedelta(hours=8))).date().isoformat(),
              'actor': 'Codex', 'method': 'read_only_database_and_cached_development_replay',
              'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'api_requests': 0, 'test_questions_accessed': 0, 'formal_results_modified': False,
              'corpus_sha256': corpus_hash, 'vectors_sha256': vector_hash,
              'scope': 'Post-experiment documentation check; original implementation and calibration dated 12 November remain historical.'}
    save(11, 'verification.json', {**common, 'documents': len(documents), 'chunks': len(records),
        'vectors': len(matrix), 'dimensions': 1024, 'all_source_hashes_match': True,
        'cloud_allowed_documents': sum(row['allow_cloud'] for row in documents),
        'unique_document_ids': len({row['id'] for row in documents}),
        'confirmed_formal_edition_pairs': 0, 'bm25_development_items': len(scores['bm25']),
        'bm25_gold_recall_sum': sum(row['recall_at_5'] for row in scores['bm25']),
        'm2_status': 'document and index count met; formal edition-pair objective unmet'})
    save(12, 'preparation_checks.json', {**common, 'entry_status': 'advance_preparation_draft',
        'embedding_model': settings.embedding_model, 'dimensions': 1024,
        'finite_nonzero_document_vectors': len(matrix), 'cosine_cross_checks': cosine_checks,
        'cached_query_vectors_used': len(client.keys), 'reloaded_cache_same_top_five': True,
        'development_items': len(scores['dense']),
        'dense_gold_recall_sum': sum(row['recall_at_5'] for row in scores['dense'])})
    save(13, 'preparation_checks.json', {**common, 'entry_status': 'advance_preparation_draft',
        'development_items': len(comparisons), 'fusion_formula_checks': formula_checks,
        'queries_with_different_top_five_lists': sum(len({tuple(ids) for ids in row['rankings'].values()}) > 1
                                                    for row in comparisons),
        'normalization_edge_cases_passed': 4, 'replayed_weight': .5,
        'selection_origin': 'Existing development-only calibration on 2026-11-12; unchanged',
        'metrics': {mode: {'recall_at_5': sum(row['recall_at_5'] for row in values)/16,
                           'mrr_at_5': sum(row['mrr_at_5'] for row in values)/16}
                    for mode, values in scores.items()}, 'rankings': comparisons})
    print(json.dumps({'documents': len(documents), 'chunks': len(records),
        'cosine_cross_checks': cosine_checks, 'formula_checks': formula_checks,
        'metrics': {mode: sum(row['recall_at_5'] for row in values)/16 for mode, values in scores.items()},
        'api_requests': 0}, indent=2))


if __name__ == '__main__':
    main()
