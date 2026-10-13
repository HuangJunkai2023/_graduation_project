"""Transactional SQLite persistence; exact file deduplication and vector identity."""
from pathlib import Path
from contextlib import contextmanager
import json
import sqlite3
from .documents import parse_file
from .api import APIError


class Store:
    def __init__(self, settings):
        self.settings = settings
        settings.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS chunks(id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE, payload TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS vectors(chunk_id TEXT PRIMARY KEY REFERENCES chunks(id) ON DELETE CASCADE, identity TEXT NOT NULL, payload TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS chunks_document ON chunks(document_id);
                CREATE TABLE IF NOT EXISTS imports(id INTEGER PRIMARY KEY, payload TEXT NOT NULL);
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.settings.db_path, timeout=30)
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def documents(self):
        with self.connect() as db: return [json.loads(r[0]) for r in db.execute("SELECT payload FROM documents ORDER BY id")]

    def records(self):
        with self.connect() as db:
            rows = db.execute("SELECT c.payload,d.payload,v.identity,v.payload FROM chunks c JOIN documents d ON c.document_id=d.id LEFT JOIN vectors v ON c.id=v.chunk_id ORDER BY c.id").fetchall()
        result = []
        for chunk, doc, identity, vector in rows:
            result.append({**json.loads(chunk), "document": json.loads(doc), "vector_identity": identity,
                           "vector": json.loads(vector) if vector else None})
        return result

    def ingest(self, path, **kwargs):
        try:
            document, chunks = parse_file(path, self.settings, **kwargs)
            with self.connect() as db:
                exists = db.execute("SELECT 1 FROM documents WHERE id=?", (document["id"],)).fetchone()
                if exists: status = "duplicate"
                elif not chunks: status = "no_text"
                else:
                    db.execute("INSERT INTO documents VALUES (?,?)", (document["id"], json.dumps(document, ensure_ascii=False)))
                    db.executemany("INSERT INTO chunks VALUES (?,?,?)", [(c["id"], document["id"], json.dumps(c, ensure_ascii=False)) for c in chunks])
                    status = "imported"
                report = {"name": document["name"], "status": status, "chunks": len(chunks) if status == "imported" else 0,
                          "document_id": document["id"], "warnings": document["warnings"]}
        except Exception as exc:
            # File parsing failures are isolated and do not destroy the existing index.
            report = {"name": Path(kwargs.get("display_name") or path).name, "status": "error", "chunks": 0,
                      "message": str(exc)[:300] if isinstance(exc, ValueError) else f"无法解析文件（{type(exc).__name__}）。"}
        with self.connect() as db: db.execute("INSERT INTO imports(payload) VALUES (?)", (json.dumps(report, ensure_ascii=False),))
        return report

    def import_reports(self):
        with self.connect() as db: return [json.loads(r[0]) for r in db.execute("SELECT payload FROM imports ORDER BY id DESC LIMIT 100")]

    def set_cloud_permission(self, document_ids, allowed):
        with self.connect() as db:
            for doc_id in document_ids:
                row = db.execute("SELECT payload FROM documents WHERE id=?", (doc_id,)).fetchone()
                if not row: raise ValueError("文档不存在。")
                document = json.loads(row[0]); document["allow_cloud"] = bool(allowed)
                db.execute("UPDATE documents SET payload=? WHERE id=?", (json.dumps(document, ensure_ascii=False), doc_id))

    def remove(self, document_id):
        with self.connect() as db: db.execute("DELETE FROM documents WHERE id=?", (document_id,))

    def embed_pending(self, client, batch_size=8):
        if batch_size < 1: raise ValueError("batch_size must be positive")
        identity = self.settings.embedding_identity
        records = self.records()
        pending = [r for r in records if r["document"]["allow_cloud"] and r["vector_identity"] != identity]
        # Commit each validated batch: interruption can resume without re-embedding completed batches.
        done = 0
        expected_dim = next((len(r["vector"]) for r in records if r["vector_identity"] == identity), None)
        for start in range(0, len(pending), batch_size):
            batch = pending[start:start+batch_size]
            vectors = client.embed([r["text"] for r in batch])
            if len(vectors) != len(batch): raise APIError("invalid_embedding", "向量数量与文本数量不一致。")
            for vector in vectors:
                expected_dim = expected_dim or len(vector)
                if len(vector) != expected_dim: raise APIError("embedding_dimension", "向量维度发生变化，请更换模型配置或重建向量。")
            with self.connect() as db:
                db.executemany("INSERT OR REPLACE INTO vectors VALUES (?,?,?)", [(r["id"], identity, json.dumps(v)) for r,v in zip(batch,vectors)])
            done += len(batch)
        return {"embedded": done, "blocked_chunks": sum(not r["document"]["allow_cloud"] for r in records)}
