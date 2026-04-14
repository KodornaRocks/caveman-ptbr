# Caveman Hooks PT-BR

Hooks **bundles com plugin caveman** e ativam auto quando plugin instalado. Sem setup manual preciso.

Se instalou caveman standalone (sem plugin), pode usar `bash hooks/install.sh` para wire em settings.json manual.

## O Que Tem

### `caveman-activate.js` — SessionStart hook

- Roda uma vez quando Claude Code inicia
- Escreve `full` em `~/.claude/.caveman-active` (flag file)
- Emite regras caveman como SessionStart context escondido
- Detecta statusline config ausente e emite nudge setup

### `caveman-mode-tracker.js` — UserPromptSubmit hook

- Dispara em cada user prompt, checa por comandos `/caveman`
- Escreve modo ativo em flag file quando caveman command detectado
- Suporta: `full`, `lite`, `ultra`, `commit`, `review`, `compress`

### `caveman-statusline.sh` / `caveman-statusline.ps1` — Statusline badge

- Lê `~/.claude/.caveman-active` e output badge colorido
- Mostra `[CAVEMAN]`, `[CAVEMAN:LITE]`, `[CAVEMAN:ULTRA]`, `[CAVEMAN:COMMIT]`, etc.

## Badge Statusline

Badge statusline mostra qual caveman modo ativo direto em status bar Claude Code.

**Plugin users:** Se já não tem `statusLine` configurado, Claude detecta em primeira sessão após install e oferece setup. Aceita e pronto.

Se já tem statusline custom, caveman não sobrescreve e Claude fica quieto. Add badge snippet em script existente ao invés.

**Standalone users:** `install.sh` / `install.ps1` wires statusline auto se não já tem statusline custom. Se tem, installer deixa sozinha.

**Manual:** Se precisa configurar você mesmo, add um desses em `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /path/to/caveman-statusline.sh"
  }
}
```

Replace path com locação script real.

**Custom statusline:** Se já tem statusline script, add snippet:

```bash
caveman_text=""
caveman_flag="$HOME/.claude/.caveman-active"
if [ -f "$caveman_flag" ]; then
  caveman_mode=$(cat "$caveman_flag" 2>/dev/null)
  if [ "$caveman_mode" = "full" ] || [ -z "$caveman_mode" ]; then
    caveman_text=$'\033[38;5;172m[CAVEMAN]\033[0m'
  else
    caveman_suffix=$(echo "$caveman_mode" | tr '[:lower:]' '[:upper:]')
    caveman_text=$'\033[38;5;172m[CAVEMAN:'"${caveman_suffix}"$']\033[0m'
  fi
fi
```

Badge exemplos:
- `/caveman` → `[CAVEMAN]`
- `/caveman ultra` → `[CAVEMAN:ULTRA]`
- `/caveman-commit` → `[CAVEMAN:COMMIT]`

## Como Funciona

```
SessionStart hook ──writes "full"──▶ ~/.claude/.caveman-active ◀──writes mode── UserPromptSubmit hook
                                              │
                                           reads
                                              ▼
                                     Statusline script
                                    [CAVEMAN:ULTRA] │ ...
```

SessionStart stdout injected como hidden system context. Statusline roda como separate process. Flag file é bridge.

## Desinstalar

Se instalou via plugin: disable plugin — hooks deativam auto.

Se instalou via `install.sh`:
```bash
bash hooks/uninstall.sh
```

Ou manual:
1. Remove `~/.claude/hooks/caveman-activate.js`, `~/.claude/hooks/caveman-mode-tracker.js`, statusline script
2. Remove SessionStart, UserPromptSubmit, statusLine entries de `~/.claude/settings.json`
3. Delete `~/.claude/.caveman-active`

---

🇺🇸 [English version](README.md)
