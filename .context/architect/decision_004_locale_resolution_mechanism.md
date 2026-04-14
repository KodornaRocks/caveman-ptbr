# ADR-004: Mecanismo tecnico de resolucao de locale

**Status**: accepted
**Date**: 2026-04-14
**Deciders**: architect

## Context

ADR-001 decidiu locale JSON + runtime flag. ADR-003 definiu contrato de paridade. Falta especificar COMO, na pratica, hooks JS e CLI Python resolvem o locale e como documentos Markdown sao selecionados. Restricoes:

- Zero dependencias novas (P-001)
- Silent-fail obrigatorio em hooks (P-004)
- Hooks JS sao standalone (sem require tree alem do stdlib)
- Python CLI ja usa stdlib + anthropic opcional

## Decision

### 1. Resolucao de locale (regra compartilhada)

Ordem de prioridade para determinar o locale ativo:

1. Flag CLI `--lang=<code>` (apenas CLI Python; hooks JS nao tem CLI)
2. Variavel de ambiente `CAVEMAN_LANG` (valores aceitos: `pt-br`, `en`)
3. Arquivo de config `~/.config/caveman/config.json`, chave `lang` (analogo a como `caveman-config.js` ja resolve `default_mode`)
4. Default: `pt-br`

Valores invalidos -> fallback silencioso para `pt-br`.

### 2. Resolver JS: `hooks/caveman-i18n.js`

Novo modulo Node.js (CommonJS) compartilhado por `caveman-activate.js` e `caveman-mode-tracker.js`:

```
// Assinatura publica
function getLang() -> 'pt-br' | 'en'
function t(key, opts = {}) -> string
function loadLocale(lang) -> object   // cacheado em memoria por sessao
```

Comportamento:
- `loadLocale` le `<plugin_root>/locales/<lang>.json` via `fs.readFileSync`. Em caso de erro, retorna `{}`.
- `t(key, opts)` executa cascata: locale ativo -> `pt-br` -> string vazia. Se resultado tem placeholders `{name}`, substitui por `opts[name]`. Se chave ausente em ambos locales, retorna `key` literal (facilita debug; nao crasha).
- Todo o modulo envolve I/O em try/catch. `getLang` nunca lanca.

Integracao:
- `caveman-activate.js` linhas 48/96/138-143 (banner, nudge, etc.) passam a chamar `t('hooks.activate.banner', { mode })`.
- `caveman-mode-tracker.js` usa `t` para mensagens que emitir.
- Localizacao do arquivo de locale: relativo ao arquivo JS via `path.join(__dirname, '..', 'locales', lang + '.json')`. Caminho tolerante a instalacao standalone (`~/.claude/hooks/`) via fallback: se primeiro path nao existir, tenta `path.join(__dirname, 'locales', lang + '.json')`.

Silent-fail: falha de leitura de locale emite `''` (vazio) do banner em vez de crashar. Hook continua funcional; apenas sem mensagem visivel. Aceitavel.

### 3. Resolver Python: `caveman-compress/scripts/i18n.py`

Novo modulo stdlib:

```
# API publica
def get_lang(cli_arg: str | None = None) -> str
def t(key: str, **kwargs) -> str
def load_locale(lang: str) -> dict   # cacheado em modulo
```

Comportamento:
- `get_lang` aplica ordem do item 1 (CLI arg > env > config file > default pt-br)
- `t(key, **kwargs)` usa mesmo cascade fallback do JS
- Arquivo de locale localizado via `importlib.resources` ou `os.path` a partir de `__file__`: `<repo_root>/locales/<lang>.json`. CLI instalado via plugin copia locales/ junto.

Integracao:
- `cli.py`: todas as strings hardcoded movidas. `cli.py` le `--lang` do argv antes de processar `<filepath>`.
- `compress.py`: mensagens de progresso e erro usam `t()`. Ver tambem ADR-002 item Categoria 5 para prompts LLM (esses detectam idioma do input, nao do CAVEMAN_LANG).

### 4. Selecao de documentos Markdown

Arquivos paralelos com sufixo `.pt-br.md` e `.md` (EN). Regra de selecao:

- **GitHub renderizacao**: README.md e o que GitHub exibe por default (usuarios EN). README.pt-br.md linkado no topo do README.md.
- **Skill/plugin loaders**: leem `SKILL.md` se existente (compat upstream). Skills PT-BR explicitas (caso aplicavel) viriam como nome de skill diferente, nao como seletor de locale. Nao implementar seletor dinamico de SKILL.md por locale nesta versao — complexidade nao justificada.
- **`skills/caveman/SKILL.pt-br.md`**: existe como referencia editorial para contribuidores BR e para gerar documentacao PT-BR. NAO e consumido em runtime pelo agente (o agente consome SKILL.md EN + modo `caveman-ptbr` se ativado para saida PT-BR). Ver ADR-005.

### 5. Organizacao de arquivos

```
repo/
  locales/
    pt-br.json
    en.json
    required_keys.json
  hooks/
    caveman-i18n.js          # novo
    caveman-activate.js      # atualizado
    caveman-mode-tracker.js  # atualizado
    caveman-config.js        # sem mudanca
  caveman-compress/
    scripts/
      i18n.py                # novo
      cli.py                 # atualizado
      compress.py            # atualizado
  README.md                  # EN reduzido
  README.pt-br.md            # PT-BR canonico
  skills/caveman/
    SKILL.md                 # EN canonico upstream (intocado + secao caveman-ptbr aditiva)
    SKILL.pt-br.md           # PT-BR canonico fork
```

Detalhes adicionais de sync CI em ADR-006.

### 6. Default: PT-BR. Override: CAVEMAN_LANG ou --lang

Comportamento explicito esperado:

| Contexto | CAVEMAN_LANG | --lang | Locale ativo |
|----------|--------------|--------|--------------|
| Padrao fork | (unset) | (n/a) | pt-br |
| Env override | en | (n/a) | en |
| CLI override | (qualquer) | en | en |
| Invalido | xx | (n/a) | pt-br (fallback) |

## Alternatives Considered

### Usar $LANG ou $LC_ALL do sistema
- **Pros**: zero config explicita
- **Cons**: nao-deterministico em CI/docker/agentes; pode nao refletir intencao do dev
- **Why not chosen**: ADR-001 ja rejeitou.

### Introduzir biblioteca i18n (ex: i18next para JS, gettext para Python)
- **Pros**: features avancadas (pluralization, ICU)
- **Cons**: viola P-001 (zero dep) e quebra distribuicao zero-install dos hooks
- **Why not chosen**: nao ha necessidade funcional que justifique.

### Compilar locales em tempo de install
- **Pros**: runtime mais rapido
- **Cons**: introduz step de build que nao existe
- **Why not chosen**: JSON parse em startup de hook e O(ms); nao ha problema de performance.

## Consequences

### Positive
- Padrao identico em JS e Python facilita cognitivamente
- Cascade fallback garante robustez
- Zero dependencias novas

### Negative
- Mais dois arquivos (i18n.js, i18n.py) para manter
- Precisa coordenar required_keys entre stacks

### Risks
- **Falha de leitura JSON**: envolto em try/catch; silent-fail com literal key como ultimo recurso
- **Cache staleness**: cache de locale e por processo (hook/CLI sao short-lived). Nao ha risco pratico.
- **Path resolution em standalone install**: testado via fallback duplo (plugin root OU diretorio do hook).

## Protected Areas

- `hooks/caveman-i18n.js:silent-fail` — obrigatoriedade de try/catch em todo I/O
- `caveman-compress/scripts/i18n.py` idem

Ver `protected_areas.json`: `hooks/caveman-activate.js:silent-fail-behavior`.

## Related Decisions

- ADR-001: estrategia geral
- ADR-003: contrato (required_keys, placeholders)
- ADR-006: integracao com CI
