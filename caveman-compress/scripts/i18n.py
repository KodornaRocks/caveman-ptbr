"""
caveman — i18n locale resolver (Python stdlib only)

Resolution order for locale:
  1. cli_arg (--lang flag from CLI)
  2. CAVEMAN_LANG environment variable
  3. Config file lang field: ~/.config/caveman/config.json (or XDG/APPDATA)
  4. Default: 'pt-br'

Fallback cascade in t():
  1. Active locale
  2. pt-br
  3. key literal (never crashes)
"""

import json
import os
import re
from pathlib import Path
from typing import Optional

VALID_LANGS = {'pt-br', 'en'}

# Module-level cache: lang -> locale dict
_cache: dict = {}


def _get_config_dir() -> Path:
    xdg = os.environ.get('XDG_CONFIG_HOME')
    if xdg:
        return Path(xdg) / 'caveman'
    if os.name == 'nt':
        appdata = os.environ.get('APPDATA') or str(Path.home() / 'AppData' / 'Roaming')
        return Path(appdata) / 'caveman'
    return Path.home() / '.config' / 'caveman'


def get_lang(cli_arg: Optional[str] = None) -> str:
    try:
        # 1. CLI argument (highest priority)
        if cli_arg is not None:
            normalized = cli_arg.lower()
            if normalized in VALID_LANGS:
                return normalized
            # Invalid -> fall through silently

        # 2. Environment variable
        env_lang = os.environ.get('CAVEMAN_LANG')
        if env_lang:
            normalized = env_lang.lower()
            if normalized in VALID_LANGS:
                return normalized
            # Invalid -> fall through silently

        # 3. Config file
        try:
            config_path = _get_config_dir() / 'config.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            lang = config.get('lang', '')
            if lang and lang.lower() in VALID_LANGS:
                return lang.lower()
        except Exception:
            pass  # Config missing or invalid — fall through

    except Exception:
        pass  # Any unexpected error — fall through to default

    # 4. Default
    return 'pt-br'


def _resolve_locale_path(lang: str) -> list:
    """Return candidate paths for locale file, primary first."""
    # Primary: repo root / locales/ (two levels up from this script)
    script_dir = Path(__file__).parent
    primary = script_dir.parent.parent / 'locales' / f'{lang}.json'
    # Fallback: one level up (in case of flattened install)
    fallback = script_dir.parent / 'locales' / f'{lang}.json'
    # Second fallback: same directory
    same_dir = script_dir / 'locales' / f'{lang}.json'
    return [primary, fallback, same_dir]


def load_locale(lang: str) -> dict:
    if lang in _cache:
        return _cache[lang]

    try:
        candidates = _resolve_locale_path(lang)
        for candidate in candidates:
            try:
                with open(candidate, 'r', encoding='utf-8') as f:
                    parsed = json.load(f)
                _cache[lang] = parsed
                return parsed
            except FileNotFoundError:
                continue
            except Exception:
                # JSON parse error or other — try next
                continue
        # None of the candidates worked
        _cache[lang] = {}
        return {}
    except Exception:
        _cache[lang] = {}
        return {}


def _get_nested(obj: dict, key: str):
    """Resolve dot-notation key: 'hooks.activate.banner' -> obj['hooks']['activate']['banner']."""
    parts = key.split('.')
    current = obj
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
        if current is None:
            return None
    return current


def _interpolate(s: str, kwargs: dict) -> str:
    if not kwargs or not isinstance(s, str):
        return s
    def replace(match):
        name = match.group(1)
        return str(kwargs[name]) if name in kwargs else match.group(0)
    return re.sub(r'\{(\w+)\}', replace, s)


def t(key: str, **kwargs) -> str:
    try:
        lang = get_lang()

        # 1. Try active locale
        active = load_locale(lang)
        value = _get_nested(active, key)
        if value is not None:
            return _interpolate(str(value), kwargs)

        # 2. Fallback to pt-br (if not already pt-br)
        if lang != 'pt-br':
            ptbr = load_locale('pt-br')
            value = _get_nested(ptbr, key)
            if value is not None:
                return _interpolate(str(value), kwargs)

        # 3. Key literal
        return key
    except Exception:
        return key
