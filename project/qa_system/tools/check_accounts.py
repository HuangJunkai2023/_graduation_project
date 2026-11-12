"""Save a local balance receipt without printing keys or personal profile fields."""
import json
from datetime import datetime, timezone
from pathlib import Path
import httpx
from ocs_qa.config import Settings, APP_ROOT


def main():
    settings = Settings.load()
    receipt = {'checked_at': datetime.now(timezone.utc).isoformat(), 'providers': {}}
    for label, base, endpoint, key in [
        ('deepseek', settings.chat_url, '/user/balance', settings.chat_key),
        ('embedding', settings.embedding_url, '/user/info', settings.embedding_key),
    ]:
        if not key:
            receipt['providers'][label] = {'status': 'not_configured'}
            continue
        try:
            with httpx.Client(timeout=20, follow_redirects=False) as client:
                response = client.get(base.rstrip('/') + endpoint, headers={'Authorization': f'Bearer {key}'})
            row = {'http_status': response.status_code}
            if response.status_code == 200:
                data = response.json()
                if label == 'deepseek':
                    row.update(is_available=data.get('is_available'), balance_infos=[
                        {k: b.get(k) for k in ['currency', 'total_balance', 'granted_balance', 'topped_up_balance']}
                        for b in data.get('balance_infos', [])])
                else:
                    row.update({k: data.get('data', {}).get(k) for k in ['balance', 'chargeBalance', 'totalBalance']})
            receipt['providers'][label] = row
        except (httpx.HTTPError, ValueError, TypeError):
            receipt['providers'][label] = {'status': 'unavailable'}
    destination = APP_ROOT / 'runtime/research/account_balance.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'saved': str(destination), 'http_statuses': {
        label: value.get('http_status', value.get('status')) for label, value in receipt['providers'].items()},
        'note': 'A current balance does not establish historical project spending.'}))


if __name__ == '__main__':
    main()
