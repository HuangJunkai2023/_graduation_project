"""Select the checked local research index, preserving the previous configuration."""
from datetime import datetime, timezone
from pathlib import Path
import shutil
from ocs_qa.config import APP_ROOT, Settings
from ocs_qa.store import Store


def main():
    path = APP_ROOT / 'runtime/research/kb.sqlite3'
    store = Store(Settings.load(path))
    records = store.records()
    if len(store.documents()) < 20 or not records or any(
            r['vector_identity'] != store.settings.embedding_identity for r in records):
        raise ValueError('Research corpus/vector index is not ready.')
    env_path = APP_ROOT / '.env'
    backup_dir = APP_ROOT / 'runtime/config-backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    if env_path.exists():
        shutil.copy2(env_path, backup_dir / f'env.before-research-{stamp}.txt')
        lines = env_path.read_text(encoding='utf-8-sig').splitlines()
    else:
        lines = []
    lines = [line for line in lines if not line.strip().startswith('OCS_DB_PATH=')]
    lines.append(f'OCS_DB_PATH={path.as_posix()}')
    env_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('Selected the research database. Refresh the local question-answering page.')


if __name__ == '__main__':
    main()
