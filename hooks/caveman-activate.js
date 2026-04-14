#!/usr/bin/env node
// caveman — Claude Code SessionStart activation hook
//
// Runs on every session start:
//   1. Writes flag file at ~/.claude/.caveman-active (statusline reads this)
//   2. Emits caveman ruleset as hidden SessionStart context
//   3. Detects missing statusline config and emits setup nudge

const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode } = require('./caveman-config');
const { t } = require('./caveman-i18n');

const claudeDir = path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.caveman-active');
const settingsPath = path.join(claudeDir, 'settings.json');

const mode = getDefaultMode();

// "off" mode — skip activation entirely, don't write flag or emit rules
if (mode === 'off') {
  try { fs.unlinkSync(flagPath); } catch (e) {}
  process.stdout.write('OK');
  process.exit(0);
}

// 1. Write flag file
try {
  fs.mkdirSync(path.dirname(flagPath), { recursive: true });
  fs.writeFileSync(flagPath, mode);
} catch (e) {
  // Silent fail -- flag is best-effort, don't block the hook
}

// 2. Emit full caveman ruleset, filtered to the active intensity level.
//    The old 2-sentence summary was too weak — models drifted back to verbose
//    mid-conversation, especially after context compression pruned it away.
//    Full rules with examples anchor behavior much more reliably.
//
//    Reads SKILL.md at runtime so edits to the source of truth propagate
//    automatically — no hardcoded duplication to go stale.

// Modes that have their own independent skill files — not caveman intensity levels.
// For these, emit a short activation line; the skill itself handles behavior.
const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);

if (INDEPENDENT_MODES.has(mode)) {
  try {
    process.stdout.write(t('hooks.activate.banner_with_mode', { mode: mode }) + '. Behavior defined by /caveman-' + mode + ' skill.');
  } catch (e) {
    process.stdout.write('CAVEMAN MODE ACTIVE — level: ' + mode + '. Behavior defined by /caveman-' + mode + ' skill.');
  }
  process.exit(0);
}

const modeLabel = mode;

// Read SKILL.md — the single source of truth for caveman behavior.
// Plugin installs: __dirname = <plugin_root>/hooks/, SKILL.md at <plugin_root>/skills/caveman/SKILL.md
// Standalone installs: __dirname = ~/.claude/hooks/, SKILL.md won't exist — falls back to hardcoded rules.
let skillContent = '';
try {
  skillContent = fs.readFileSync(
    path.join(__dirname, '..', 'skills', 'caveman', 'SKILL.md'), 'utf8'
  );
} catch (e) { /* standalone install — will use fallback below */ }

let output;

if (skillContent) {
  // Strip YAML frontmatter
  const body = skillContent.replace(/^---[\s\S]*?---\s*/, '');

  // Filter intensity table: keep header rows + only the active level's row
  const filtered = body.split('\n').reduce((acc, line) => {
    // Intensity table rows start with | **level** |
    const tableRowMatch = line.match(/^\|\s*\*\*(\S+?)\*\*\s*\|/);
    if (tableRowMatch) {
      // Keep only the active level's row (and always keep header/separator)
      if (tableRowMatch[1] === modeLabel) {
        acc.push(line);
      }
      return acc;
    }

    // Example lines start with "- level:" — keep only lines matching active level
    const exampleMatch = line.match(/^- (\S+?):\s/);
    if (exampleMatch) {
      if (exampleMatch[1] === modeLabel) {
        acc.push(line);
      }
      return acc;
    }

    acc.push(line);
    return acc;
  }, []);

  try {
    output = t('hooks.activate.banner_with_mode', { mode: modeLabel }) + '\n\n' + filtered.join('\n');
  } catch (e) {
    output = 'CAVEMAN MODE ACTIVE — level: ' + modeLabel + '\n\n' + filtered.join('\n');
  }
} else {
  // Fallback when SKILL.md is not found (standalone hook install without skills dir).
  // This is the minimum viable ruleset — better than nothing.
  try {
    output = t('hooks.activate.fallback_ruleset', { mode: modeLabel });
  } catch (e) {
    output =
      'MODO CAVEMAN ATIVO — nível: ' + modeLabel + '\n\n' +
      'Responder curto como caveman esperto. Todo conteúdo técnico ficar. Só enrolação morrer.\n\n' +
      '## Persistência\n\n' +
      'ATIVO EM TODA RESPOSTA. Sem reverter após muitas trocas. Sem enchimento. Ainda ativo se incerto. Desliga só com: "parar caveman" / "modo normal".\n\n' +
      'Nível atual: **' + modeLabel + '**. Mudar: `/caveman lite|full|ultra`.\n\n' +
      '## Regras\n\n' +
      'Remover: artigos (o/a/os/as/um/uma), enchimento (só/realmente/basicamente/na verdade/simplesmente), gentilezas (claro/certamente/com prazer/fico feliz em), hedging. ' +
      'Fragmentos OK. Sinônimos curtos (grande não extenso, corrigir não "implementar uma solução para"). Termos técnicos exatos. Code blocks sem alteração. Erros citados exatos.\n\n' +
      'Padrão: `[coisa] [ação] [motivo]. [próximo passo].`\n\n' +
      'Não: "Claro! Fico feliz em ajudar com isso. O problema que você está enfrentando provavelmente é causado por..."\n' +
      'Sim: "Bug no middleware de auth. Verificação de expiry de token usa `<` não `<=`. Corrigir:"\n\n' +
      '## Auto-Clarity\n\n' +
      'Largar caveman para: avisos de segurança, confirmações de ação irreversível, sequências multi-passo onde ordem de fragmento pode ser mal interpretada, usuário pede esclarecimento ou repete pergunta. Retomar caveman depois da parte clara.\n\n' +
      '## Limites\n\n' +
      'Código/commits/PRs: escrever normal. "parar caveman" ou "modo normal": reverter. Nível persiste até mudar ou sessão terminar.';
  }
}

// 3. Detect missing statusline config — nudge Claude to help set it up
try {
  let hasStatusline = false;
  if (fs.existsSync(settingsPath)) {
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    if (settings.statusLine) {
      hasStatusline = true;
    }
  }

  if (!hasStatusline) {
    const isWindows = process.platform === 'win32';
    const scriptName = isWindows ? 'caveman-statusline.ps1' : 'caveman-statusline.sh';
    const scriptPath = path.join(__dirname, scriptName);
    const command = isWindows
      ? `powershell -ExecutionPolicy Bypass -File "${scriptPath}"`
      : `bash "${scriptPath}"`;
    const statusLineSnippet =
      '"statusLine": { "type": "command", "command": ' + JSON.stringify(command) + ' }';
    try {
      output += "\n\n" + t('hooks.activate.statusline_nudge') + " " + statusLineSnippet;
    } catch (e) {
      output += "\n\n" +
        "STATUSLINE SETUP NEEDED: The caveman plugin includes a statusline badge showing active mode " +
        "(e.g. [CAVEMAN], [CAVEMAN:ULTRA]). It is not configured yet. " +
        "To enable, add this to ~/.claude/settings.json: " +
        statusLineSnippet + " " +
        "Proactively offer to set this up for the user on first interaction.";
    }
  }
} catch (e) {
  // Silent fail — don't block session start over statusline detection
}

process.stdout.write(output);
