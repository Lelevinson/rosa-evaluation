"""Zero-inference restart check. Never print protected records or token values."""
import json
from pathlib import Path
from unittest.mock import patch

from rosa_auth.oauth import SafeError
from rosa_auth.protected_store import WindowsCredentialStore
from rosa_auth.remembered import remembered_session

destination = Path('/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027/auth-resume-check.json')
status = {'live_model_requests': 0, 'new_consent_allowed': False, 'pass': False}
try:
    with WindowsCredentialStore('research') as store:
        status['protected_record_present_before'] = store.load() is not None
        if not status['protected_record_present_before']:
            raise SafeError('no_protected_record_no_automatic_login')
        with patch('rosa_auth.remembered.LoginServer', side_effect=AssertionError('unexpected_browser_login')):
            with remembered_session(store=store, request_budget=1, status=status):
                pass
        status['pass'] = bool(status.get('authorization_source') == 'PROTECTED_REFRESH'
            and status.get('token_refreshes') == 1 and status.get('credential_retained'))
except SafeError as error:
    status['error_code'] = error.code
except Exception as error:
    status['error_type'] = type(error).__name__
destination.write_text(json.dumps(status, indent=2) + '\n')
print(json.dumps(status))
raise SystemExit(0 if status['pass'] else 1)
