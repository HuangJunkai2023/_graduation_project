from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import dotenv_values

APP_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    db_path: Path = APP_ROOT / "runtime/kb.sqlite3"
    chat_key: str = field(default="", repr=False)
    chat_url: str = "https://api.deepseek.com"
    chat_model: str = "deepseek-flash"
    embedding_key: str = field(default="", repr=False)
    embedding_url: str = ""
    embedding_model: str = ""
    timeout: float = 60
    chunk_size: int = 600
    chunk_overlap: int = 80
    top_k: int = 5
    vector_weight: float = .6
    min_coverage: float = .2
    min_cosine: float = .35

    def __post_init__(self):
        if not 0 <= self.chunk_overlap < self.chunk_size or self.chunk_size < 50:
            raise ValueError("切块长度至少 50，重叠长度须小于切块长度。")
        if not 1 <= self.top_k <= 20 or not 0 <= self.vector_weight <= 1:
            raise ValueError("Top-K 须在 1–20，融合权重须在 0–1。")
        if not 0 < self.timeout <= 300 or not 0 <= self.min_coverage <= 1 or not -1 <= self.min_cosine <= 1:
            raise ValueError("超时或证据门槛配置无效。")

    @property
    def embedding_identity(self):
        return f"{self.embedding_url.rstrip('/')}|{self.embedding_model}"

    @classmethod
    def load(cls, db_path=None):
        env = {**dotenv_values(APP_ROOT / ".env"), **os.environ}
        return cls(
            db_path=Path(db_path or env.get("OCS_DB_PATH") or APP_ROOT / "runtime/kb.sqlite3"),
            chat_key=env.get("DEEPSEEK_API_KEY", "") or "",
            chat_url=env.get("DEEPSEEK_BASE_URL") or "https://api.deepseek.com",
            chat_model=env.get("DEEPSEEK_MODEL") or "deepseek-flash",
            embedding_key=env.get("EMBEDDING_API_KEY", "") or "",
            embedding_url=env.get("EMBEDDING_BASE_URL", "") or "",
            embedding_model=env.get("EMBEDDING_MODEL", "") or "",
            timeout=float(env.get("API_TIMEOUT_SECONDS", 60)),
            chunk_size=int(env.get("CHUNK_SIZE", 600)), chunk_overlap=int(env.get("CHUNK_OVERLAP", 80)),
            top_k=int(env.get("TOP_K", 5)), vector_weight=float(env.get("VECTOR_WEIGHT", .6)),
            min_coverage=float(env.get("MIN_LEXICAL_COVERAGE", .2)),
            min_cosine=float(env.get("MIN_COSINE_SIMILARITY", .35)),
        )
