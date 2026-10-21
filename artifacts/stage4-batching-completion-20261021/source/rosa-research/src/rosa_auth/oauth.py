"""Public-client PKCE/OIDC flow following the official OSS SIWC contract.

Only host/client registration identifiers are persisted. Tokens and authorization
codes are never written to disk or returned by the local HTTP status page.
"""
import base64
from dataclasses import dataclass, field
import hashlib
import hmac
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
import time
from threading import Lock
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4

import jwt

ISSUER = 'https://auth.openai.com'
RESOURCE = 'https://api.openai.com/v1'
PLAN_SCOPE = 'chatgpt.tokens.use.direct'
SCOPES = 'openid profile email offline_access resource.invoke chatgpt.tokens.use.direct'


class SafeError(Exception):
    """An error containing only a static/category code, safe for status reports."""
    def __init__(self, code, status=None):
        self.code = code
        self.status = status
        super().__init__(f'{code}' + (f' (HTTP {status})' if status else ''))


def error_code(value, fallback='request_failed'):
    # Never forward arbitrary provider messages, URLs, or response bodies to logs.
    allowed = {'access_denied', 'invalid_grant', 'invalid_scope', 'invalid_client',
               'unauthorized_client', 'unsupported_grant_type', 'invalid_request',
               'insufficient_scope', 'invalid_token', 'rate_limit_exceeded'}
    if isinstance(value, str) and (value in allowed or re.fullmatch(r'subscription_sharing_[a-z_]{1,80}', value)):
        return value
    return fallback


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


def open_request(request, timeout=30):
    try:
        return build_opener(NoRedirect()).open(request, timeout=timeout)
    except HTTPError as error:
        try:
            body = json.loads(error.read(16384))
            detail = body.get('error', {})
            code = detail.get('code') or detail.get('type') if isinstance(detail, dict) else detail
        except (ValueError, AttributeError):
            code = None
        raise SafeError(error_code(code, 'http_error'), error.code) from None
    except (URLError, TimeoutError, OSError):
        raise SafeError('transport_error') from None


def request_json(url, *, form=None, token=None):
    headers = {'Accept': 'application/json'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    data = None
    if form is not None:
        data = urlencode(form).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    with open_request(Request(url, data=data, headers=headers)) as response:
        body = response.read()
        try:
            parsed = json.loads(body) if body else {}
        except ValueError:
            raise SafeError('invalid_json_response') from None
        if not isinstance(parsed, dict):
            raise SafeError('invalid_json_object_response')
        return parsed


def pkce_challenge(verifier):
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode('ascii')).digest()).rstrip(b'=').decode('ascii')


def validate_identity(encoded, *, key, client_id, nonce, expected_subject_hash=None):
    try:
        claims = jwt.decode(encoded, key, algorithms=['RS256'], audience=client_id,
                            issuer=ISSUER, options={'require': ['iss', 'aud', 'sub', 'exp', 'nonce']}, leeway=30)
        if not isinstance(claims['sub'], str) or not claims['sub']:
            raise SafeError('invalid_identity')
        actual_nonce = claims.get('nonce')
        if not isinstance(actual_nonce, str) or not hmac.compare_digest(actual_nonce, nonce):
            raise SafeError('nonce_mismatch')
        audiences = claims['aud']
        if isinstance(audiences, list) and len(audiences) > 1 and claims.get('azp') != client_id:
            raise SafeError('authorized_party_mismatch')
        subject_hash = hashlib.sha256(claims['sub'].encode()).hexdigest()
        if expected_subject_hash and not hmac.compare_digest(subject_hash, expected_subject_hash):
            raise SafeError('selected_account_mismatch')
        return subject_hash
    except jwt.PyJWTError:
        raise SafeError('id_token_validation_failed') from None


def load_registration(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.exists():
        record = json.loads(path.read_text())
        if not isinstance(record.get('host_id'), str) or not record['host_id'].startswith('urn:uuid:'):
            raise SafeError('invalid_registration_record')
        return record
    record = {'host_id': 'urn:uuid:' + str(uuid4())}
    save_registration(path, record)
    return record


def save_registration(path, record):
    # Whitelist non-token fields so a future caller cannot accidentally persist a token set.
    allowed = {key: record[key] for key in ('host_id', 'client_id', 'subject_hash') if key in record}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix('.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as stream:
        json.dump(allowed, stream)
    os.replace(temporary, path)
    os.chmod(path, 0o600)


@dataclass(repr=False)
class Attempt:
    host_id: str
    saved_client_id: str | None = None
    state: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    nonce: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    verifier: str = field(default_factory=lambda: secrets.token_urlsafe(64))
    redirect_uri: str = ''
    callback: dict | None = None

    def authorization_url(self, endpoint):
        params = {'client_id': self.saved_client_id or 'dynamic_agent_client',
                  'ext_agent_host_id': self.host_id, 'response_type': 'code',
                  'redirect_uri': self.redirect_uri, 'scope': SCOPES, 'resource': RESOURCE,
                  'state': self.state, 'nonce': self.nonce,
                  'code_challenge_method': 'S256', 'code_challenge': pkce_challenge(self.verifier)}
        if not self.saved_client_id:
            params['agent_name_hint'] = 'ROSA Research Agent'
        return endpoint + '?' + urlencode(params)

    def accept_callback(self, query):
        values = parse_qs(query, keep_blank_values=True)
        if any(len(value) != 1 for value in values.values()):
            raise SafeError('duplicate_callback_parameter')
        received_state = values.get('state', [''])[0]
        if not hmac.compare_digest(received_state, self.state):
            raise SafeError('state_mismatch')
        if self.callback is not None:
            raise SafeError('callback_already_received')
        if 'error' in values:
            self.callback = {'error': error_code(values['error'][0], 'authorization_denied')}
            return
        client_id = values.get('client_id', [self.saved_client_id or ''])[0]
        if not client_id or client_id == 'dynamic_agent_client':
            raise SafeError('missing_issued_client_id')
        if self.saved_client_id and client_id != self.saved_client_id:
            raise SafeError('client_id_mismatch')
        code = values.get('code', [''])[0]
        if not code:
            raise SafeError('missing_authorization_code')
        self.callback = {'code': code, 'client_id': client_id}


class LoginServer(HTTPServer):
    allow_reuse_address = False
    request_timeout = 5

    def get_request(self):
        connection, address = super().get_request()
        # Browser preconnections must not block the consent deadline indefinitely.
        connection.settimeout(self.request_timeout)
        return connection, address

    def __init__(self, attempt, endpoint, port=1455, *, request_budget=3):
        self.attempt = attempt
        self.endpoint = endpoint
        if type(request_budget) is not int or not 1 <= request_budget <= 2000:
            raise ValueError('Request budget must be between 1 and 2000')
        self.request_budget = request_budget
        super().__init__(('127.0.0.1', port), LoginHandler)
        self.timeout = 1
        self.base_url = f'http://127.0.0.1:{self.server_port}'
        attempt.redirect_uri = self.base_url + '/auth/callback'


class LoginHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Default access logs would expose authorization codes in callback URLs.

    def reply(self, status, text):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        try:
            self.wfile.write(text.encode())
        except (BrokenPipeError, ConnectionResetError):
            pass  # Browsers may cancel speculative loopback connections.

    def do_GET(self):
        if self.headers.get('Host') != f'127.0.0.1:{self.server.server_port}':
            self.reply(400, 'Invalid local host.')
            return
        parsed = urlsplit(self.path)
        if parsed.path == '/':
            url = escape(self.server.attempt.authorization_url(self.server.endpoint), quote=True)
            self.reply(200, '<!doctype html><meta charset="utf-8"><title>ROSA Research sign-in</title>'
                '<main style="font:18px system-ui;max-width:680px;margin:80px auto;line-height:1.6">'
                '<h1>ROSA Research OAuth smoke test</h1>'
                '<p>Sign in with your own ChatGPT account and review the requested plan-usage permission.</p>'
                f'<p>This run will make at most {self.server.request_budget} AI requests using an available account model. '
                'Only isolated simulation tools are exposed; no physical robot is connected. Tokens stay in memory and the helper attempts '
                'session revocation when finished. No API-key billing fallback is configured.</p>'
                f'<p><a href="{url}" style="background:#111;color:white;padding:12px 20px;border-radius:8px;text-decoration:none">Continue with ChatGPT</a></p>'
                '<p>After sign-in, return to the chat. No password or token should be pasted there.</p></main>')
        elif parsed.path == '/auth/callback':
            try:
                self.server.attempt.accept_callback(parsed.query)
            except SafeError as error:
                self.reply(400, escape(error.code))
                return
            self.reply(200, '<!doctype html><title>ROSA Research</title><h1>Authorization received</h1>'
                       '<p>Return to the chat. The helper is checking identity, permission, and model access.</p>')
        else:
            self.reply(404, 'Not found.')


class MemorySession:
    def __init__(self, discovery):
        for key in ('authorization_endpoint', 'token_endpoint', 'revocation_endpoint', 'jwks_uri'):
            url = urlsplit(discovery.get(key, ''))
            if url.scheme != 'https' or url.netloc != 'auth.openai.com':
                raise SafeError('unexpected_provider_endpoint')
        if discovery.get('issuer') != ISSUER:
            raise SafeError('unexpected_provider_issuer')
        self.discovery = discovery
        self.tokens = None
        self.client_id = None
        self._expires_at = 0
        self._refresh_lock = Lock()
        self.refresh_count = 0

    def exchange(self, attempt, expected_subject_hash=None):
        if not attempt.callback:
            raise SafeError('missing_callback')
        if 'error' in attempt.callback:
            raise SafeError(attempt.callback['error'])
        self.client_id = attempt.callback['client_id']
        self.tokens = request_json(self.discovery['token_endpoint'], form={
            'grant_type': 'authorization_code', 'client_id': self.client_id,
            'code': attempt.callback['code'], 'code_verifier': attempt.verifier,
            'redirect_uri': attempt.redirect_uri, 'resource': RESOURCE})
        encoded = self.tokens.get('id_token', '')
        try:
            key = jwt.PyJWKClient(self.discovery['jwks_uri'], timeout=15).get_signing_key_from_jwt(encoded).key
        except (jwt.PyJWTError, URLError, ValueError):
            raise SafeError('id_token_key_validation_failed') from None
        subject_hash = validate_identity(encoded, key=key, client_id=self.client_id,
                                        nonce=attempt.nonce, expected_subject_hash=expected_subject_hash)
        if not isinstance(self.tokens.get('access_token'), str) or self.tokens.get('token_type', '').lower() != 'bearer':
            raise SafeError('invalid_access_token_response')
        self._expires_at = time.monotonic() + float(self.tokens.get('expires_in', 3600))
        return subject_hash

    def access_token(self):
        """Renew near expiry, serialize rotation, and never persist or log tokens."""
        with self._refresh_lock:
            if not self.tokens:
                raise SafeError('oauth_session_closed')
            if time.monotonic() >= self._expires_at - 60:
                if not self.tokens.get('refresh_token'):
                    raise SafeError('refresh_token_unavailable')
                renewed = request_json(self.discovery['token_endpoint'], form={
                    'grant_type': 'refresh_token', 'client_id': self.client_id,
                    'refresh_token': self.tokens['refresh_token'], 'resource': RESOURCE})
                if (not renewed.get('access_token') or not renewed.get('refresh_token') or
                        renewed.get('token_type', '').lower() != 'bearer'):
                    raise SafeError('invalid_refresh_response')
                replacement = {**self.tokens, **renewed}
                if PLAN_SCOPE not in replacement.get('scope', '').split():
                    raise SafeError('plan_usage_scope_not_granted')
                self.tokens = replacement
                self._expires_at = time.monotonic() + float(renewed.get('expires_in', 3600))
                self.refresh_count += 1
            return self.tokens['access_token']

    def has_plan_scope(self):
        return self.tokens is not None and PLAN_SCOPE in self.tokens.get('scope', '').split()

    def revoke(self):
        if not self.tokens:
            return 'NO_TOKEN_SESSION'
        try:
            refresh = self.tokens.get('refresh_token')
            if not refresh:
                return 'NOT_CONFIRMED_NO_REFRESH_TOKEN'
            request_json(self.discovery['revocation_endpoint'], form={
                'token': refresh, 'token_type_hint': 'refresh_token', 'client_id': self.client_id})
            return 'REVOKED'
        except SafeError:
            return 'NOT_CONFIRMED_NETWORK_OR_PROVIDER_ERROR'
        finally:
            self.tokens.clear()
            self.tokens = None
