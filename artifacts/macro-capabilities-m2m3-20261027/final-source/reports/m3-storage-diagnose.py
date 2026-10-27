import json
import time
import traceback
from rosa_auth.protected_store import WindowsCredentialStore
from rosa_auth.oauth import SafeError

events = []
store = None
try:
    store = WindowsCredentialStore('m3_dummy_rotation')
    events.append({'op': 'open', 'poll': store._child.poll()})
    if store.load() is not None: raise RuntimeError('dummy_profile_exists')
    store.save({'synthetic': 'NO_REAL_CREDENTIAL'})
    events.append({'op': 'save_initial', 'poll': store._child.poll()})
    time.sleep(4)
    events.append({'op': 'after_delay', 'poll': store._child.poll()})
    store.save({'synthetic': 'NO_REAL_CREDENTIAL_REPLACEMENT'})
    events.append({'op': 'replace', 'pass': store.load() == {'synthetic': 'NO_REAL_CREDENTIAL_REPLACEMENT'}})
    store.delete()
except Exception as error:
    events.append({'error_type': type(error).__name__, 'code': getattr(error, 'code', None),
        'frames': [{'file': f.filename.rsplit('/', 1)[-1], 'function': f.name, 'line': f.lineno}
            for f in traceback.extract_tb(error.__traceback__)]})
finally:
    if store:
        try: store.close()
        except Exception as error: events.append({'close_error_type': type(error).__name__})
print(json.dumps(events))
