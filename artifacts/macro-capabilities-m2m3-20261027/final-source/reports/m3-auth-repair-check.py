"""Manual initial authorization only; zero inference. Safe public status output."""
import json
from pathlib import Path
from rosa_auth.oauth import SafeError
from rosa_auth.remembered import remembered_session

status = {'live_model_requests': 0, 'purpose': 'validate_post_fix_protected_login'}
path = Path('/mnt/c/Proj/robotics/introtorobotics/rosa-evaluation/artifacts/macro-capabilities-m2m3-20261027/auth-repair-login.json')
try:
    with remembered_session(request_budget=1, status=status):
        pass
except SafeError as error:
    status['error_code'] = error.code
finally:
    path.write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps(status))
