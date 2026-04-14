#!/usr/bin/env node
// caveman — i18n locale resolver (CommonJS, stdlib only)
//
// Resolution order for locale:
//   1. CAVEMAN_LANG environment variable
//   2. Config file lang field: ~/.config/caveman/config.json (or XDG/APPDATA)
//   3. Default: 'pt-br'
//
// Fallback cascade in t():
//   1. Active locale
//   2. pt-br
//   3. key literal (never crashes)

'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const VALID_LANGS = ['pt-br', 'en'];

// Module-level cache: lang -> locale object
const _cache = {};

function getConfigDir() {
  if (process.env.XDG_CONFIG_HOME) {
    return path.join(process.env.XDG_CONFIG_HOME, 'caveman');
  }
  if (process.platform === 'win32') {
    return path.join(
      process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'),
      'caveman'
    );
  }
  return path.join(os.homedir(), '.config', 'caveman');
}

function getLang() {
  try {
    // 1. Environment variable
    const envLang = process.env.CAVEMAN_LANG;
    if (envLang) {
      const normalized = envLang.toLowerCase();
      if (VALID_LANGS.includes(normalized)) {
        return normalized;
      }
      // Invalid value -> fall through silently
    }

    // 2. Config file
    try {
      const configPath = path.join(getConfigDir(), 'config.json');
      const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
      if (config.lang && VALID_LANGS.includes(config.lang.toLowerCase())) {
        return config.lang.toLowerCase();
      }
    } catch (e) {
      // Config file missing or invalid — fall through
    }
  } catch (e) {
    // Any unexpected error — fall through to default
  }

  // 3. Default
  return 'pt-br';
}

function resolveLocalePath(lang) {
  // Primary: plugin root (repo root / installed plugin root)
  const primary = path.join(__dirname, '..', 'locales', lang + '.json');
  // Fallback: same directory as hook (standalone install)
  const fallback = path.join(__dirname, 'locales', lang + '.json');
  return { primary, fallback };
}

function loadLocale(lang) {
  if (_cache[lang] !== undefined) {
    return _cache[lang];
  }

  try {
    const { primary, fallback } = resolveLocalePath(lang);
    let raw;
    try {
      raw = fs.readFileSync(primary, 'utf8');
    } catch (e) {
      try {
        raw = fs.readFileSync(fallback, 'utf8');
      } catch (e2) {
        // Neither path found
        _cache[lang] = {};
        return {};
      }
    }
    const parsed = JSON.parse(raw);
    _cache[lang] = parsed;
    return parsed;
  } catch (e) {
    // JSON parse error or any other error
    _cache[lang] = {};
    return {};
  }
}

function getNestedValue(obj, key) {
  // Support dot-notation keys: 'hooks.activate.banner'
  const parts = key.split('.');
  let current = obj;
  for (const part of parts) {
    if (current === null || current === undefined || typeof current !== 'object') {
      return undefined;
    }
    current = current[part];
  }
  return current;
}

function interpolate(str, opts) {
  if (!opts || typeof str !== 'string') return str;
  return str.replace(/\{(\w+)\}/g, (match, name) => {
    return opts[name] !== undefined ? opts[name] : match;
  });
}

function t(key, opts) {
  try {
    const lang = getLang();

    // 1. Try active locale
    const activeLocale = loadLocale(lang);
    const activeValue = getNestedValue(activeLocale, key);
    if (activeValue !== undefined && activeValue !== null) {
      return interpolate(String(activeValue), opts);
    }

    // 2. Fallback to pt-br (if not already pt-br)
    if (lang !== 'pt-br') {
      const ptbrLocale = loadLocale('pt-br');
      const ptbrValue = getNestedValue(ptbrLocale, key);
      if (ptbrValue !== undefined && ptbrValue !== null) {
        return interpolate(String(ptbrValue), opts);
      }
    }

    // 3. Key literal (never crashes, aids debug)
    return key;
  } catch (e) {
    // Total silent-fail: return key literal
    return key;
  }
}

module.exports = { getLang, t, loadLocale };
