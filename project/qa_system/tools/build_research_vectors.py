"""Resume research embeddings; reuse only identical text and model vectors."""
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
from ocs_qa.config import APP_ROOT, Settings
from ocs_qa.store import Store
from ocs_qa.api import ModelClient


def main():
    root = APP_ROOT / 'runtime/research'
    target = Store(Settings.load(root / 'kb.sqlite3'))
    backup = root / 'kb.before-vectors.sqlite3'
    if not backup.exists():
        with sqlite3.connect(backup) as destination, target.connect() as source:
            source.backup(destination)
    demo = Store(Settings.load(APP_ROOT / 'runtime/kb.sqlite3'))
    known = {r['id']: r for r in demo.records()
             if r['vector_identity'] == target.settings.embedding_identity}
    reused = 0
    with target.connect() as db:
        for row in target.records():
            other = known.get(row['id'])
            if (row['vector_identity'] != target.settings.embedding_identity and other
                    and row['document_id'] == other['document_id'] and row['text'] == other['text']
                    and row['location'] == other['location']):
                db.execute('INSERT OR REPLACE INTO vectors VALUES (?,?,?)',
                           (row['id'], target.settings.embedding_identity, json.dumps(other['vector'])))
                reused += 1
    print(json.dumps({'reused_identical_vectors': reused}), flush=True)

    class ProgressClient(ModelClient):
        completed = 0
        def embed(self, texts):
            result = super().embed(texts)
            self.completed += len(texts)
            print(json.dumps({'new_vectors_completed': self.completed}), flush=True)
            return result

    result = target.embed_pending(ProgressClient(target.settings), batch_size=16)
    records = target.records()
    receipt = {'checked_at': datetime.now(timezone.utc).isoformat(),
               'documents': len(target.documents()), 'chunks': len(records),
               'vectors_current_model': sum(r['vector_identity'] == target.settings.embedding_identity for r in records),
               'dimensions': sorted({len(r['vector']) for r in records if r['vector']}),
               'reused_this_run': reused, **result,
               'model_identity': target.settings.embedding_identity,
               'note': 'Vector readiness is an interface check, not measured retrieval quality.'}
    (root / 'vector_readiness.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
