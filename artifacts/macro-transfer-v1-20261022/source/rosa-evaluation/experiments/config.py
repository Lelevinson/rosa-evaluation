"""Shared paths and tool settings. No third-party dependencies are required."""
from copy import deepcopy
from pathlib import Path
import re
import tomllib
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]


def _merge(base, overrides):
    result = deepcopy(base)
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(root=ROOT):
    """Read shared defaults, then optional local overrides."""
    root = Path(root)
    with (root / 'config.toml').open('rb') as stream:
        config = tomllib.load(stream)
    local = root / 'config.local.toml'
    if local.is_file():
        with local.open('rb') as stream:
            config = _merge(config, tomllib.load(stream))
    return config


def resolve_path(value, root=ROOT):
    path = Path(value).expanduser()
    return (path if path.is_absolute() else Path(root) / path).resolve()


def configured_path(name, root=ROOT):
    return resolve_path(load_config(root)['paths'][name], root)


def checkout(name, root=ROOT):
    try:
        value = load_config(root)['checkouts'][name]
    except KeyError as error:
        raise ValueError(f'Unknown checkout {name!r}; configure it in config.toml or config.local.toml.') from error
    return resolve_path(value, root)


def _component(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', value):
        raise ValueError(f'Expected a single output identifier, got {value!r}.')
    return value


def run_dir(run_id, root=ROOT):
    return configured_path('results', root) / 'runs' / _component(run_id)


def tool_output_dir(run_id, tool, root=ROOT):
    return run_dir(run_id, root) / _component(tool)


def validation_dir(suite_id, tool, root=ROOT):
    return configured_path('results', root) / 'validations' / _component(suite_id) / _component(tool)


def tool_state_dir(tool, root=ROOT):
    return configured_path('state', root) / _component(tool)


def phoenix_url(root=ROOT):
    url = load_config(root)['tools']['phoenix']['url'].rstrip('/')
    parsed = urlparse(url)
    if (parsed.scheme != 'http' or parsed.hostname not in {'127.0.0.1', 'localhost'}
            or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment):
        raise ValueError('Phoenix URL must be an HTTP loopback address, for example http://127.0.0.1:6006.')
    return url


def phoenix_project(root=ROOT):
    return load_config(root)['tools']['phoenix']['project']
