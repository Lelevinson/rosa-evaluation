"""Reuse existing renewal; deliberately offer no consent or login fallback."""
from contextlib import contextmanager
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

from rosa_auth.oauth import ISSUER,SCOPES,SafeError,load_registration,request_json
from rosa_auth.protected_store import WindowsCredentialStore
from rosa_auth.remembered import RememberedSession
from rosa_auth.responses import SiwcBackend

ROOT=Path(__file__).resolve().parent
MODEL='gpt-6.1-sol'


@contextmanager
def restore_only(status):
    """Existing public restore/access_token APIs; never construct a login server."""
    active=None
    with WindowsCredentialStore('research') as store:
        try:
            record=store.load()
            if record is None:raise SafeError('manual_sign_in_required_no_automatic_login')
            status['protected_record_present']=True
            registration=load_registration(Path.home()/'.local/share/rosa-siwc/registration.json')
            discovery=request_json(ISSUER+'/.well-known/openid-configuration')
            active=RememberedSession(discovery,store,registration)
            active.restore(record)
            active.access_token()  # Forced real renewal by the existing restore implementation.
            active.require_renewable()
            granted=set(active.tokens['scope'].split())
            if not {'offline_access','resource.invoke','chatgpt.tokens.use.direct'}<=granted<=set(SCOPES.split()):
                raise SafeError('invalid_saved_scope_grant')
            status.update(provider_renewal_verified=True,granted_scopes=sorted(granted),
                scopes_unchanged=True,renewable=True,authorization_source='PROTECTED_REFRESH')
            yield active
        finally:
            if active:
                status['token_refreshes']=active.refresh_count
                active.clear_memory()
            status['credential_retained']=store.load() is not None
            status['memory_cleanup']='CLEARED' if active else 'NO_ACTIVE_SESSION'


def check_models(active,status):
    backend=SiwcBackend(token_provider=active.access_token,request_budget=291)
    try:
        models=backend.models()
        if MODEL not in {row['slug'] for row in models}:raise SafeError('required_model_not_in_authorized_catalogue')
        status.update(authenticated_model_catalogue=True,required_model_available=True,
                      inference_quota='UNKNOWN',inference_requests=0)
    finally:backend.close()


def main():
    assert not (ROOT/'authorization-preflight.json').exists(),'Preserve the first preflight result.'
    status={'checked_utc':datetime.now(timezone.utc).isoformat(),'pass':False,
            'inference_requests':0,'inference_quota':'UNKNOWN','automatic_login':False}
    try:
        with restore_only(status) as active:check_models(active,status)
        status['pass']=True
    except Exception as error:
        status.update(error_type=type(error).__name__)
        if isinstance(error,SafeError):status.update(error_code=error.code,http_status=error.status)
    (ROOT/'authorization-preflight.json').write_text(json.dumps(status,indent=2)+'\n')
    print(json.dumps(status))
    if not status['pass']:raise SystemExit(1)


if __name__=='__main__':main()
