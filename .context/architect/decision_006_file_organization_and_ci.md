# ADR-006: Organizacao de arquivos, docs paralelos e sync CI

**Status**: accepted
**Date**: 2026-04-14
**Deciders**: architect

## Context

ADRs 001-005 definem o QUE. Este ADR consolida o COMO sob a perspectiva de organizacao fisica do repo e adapta o workflow `sync-skill.yml` para suportar PT-BR sem quebrar o sync EN upstream-compat.

## Decision

### 1. Layout final do repositorio (apos fork)

```
caveman-ptbr/
  locales/
    pt-br.json
    en.json
    required_keys.json
  hooks/
    caveman-i18n.js              # NOVO
    caveman-activate.js          # ATUALIZADO (usa i18n)
    caveman-mode-tracker.js      # ATUALIZADO (caveman-ptbr + i18n)
    caveman-statusline.sh        # ATUALIZADO (badges PTBR-*)
    caveman-statusline.ps1       # ATUALIZADO
    caveman-config.js            # INTOCADO
    install.sh / install.ps1     # ATUALIZADO (copiar locales/)
    uninstall.sh / uninstall.ps1 # ATUALIZADO
    README.md                    # EN reduzido
    README.pt-br.md              # NOVO canonico
  caveman-compress/
    scripts/
      i18n.py                    # NOVO
      cli.py                     # ATUALIZADO
      compress.py                # ATUALIZADO (prompts detectam idioma input)
      validate.py                # INTOCADO
      detect.py                  # INTOCADO
    SKILL.md                     # INTOCADO upstream-compat
    SKILL.pt-br.md               # NOVO canonico
    README.md                    # EN reduzido
    README.pt-br.md              # NOVO canonico
    SECURITY.md                  # INTOCADO
    SECURITY.pt-br.md            # NOVO
  skills/
    caveman/
      SKILL.md                   # ATUALIZADO: + secao caveman-ptbr (aditiva)
      SKILL.pt-br.md             # NOVO canonico editorial PT-BR
    caveman-commit/
      SKILL.md                   # INTOCADO
      SKILL.pt-br.md             # NOVO
    caveman-review/
      SKILL.md                   # INTOCADO
      SKILL.pt-br.md             # NOVO
    caveman-help/
      SKILL.md                   # INTOCADO
      SKILL.pt-br.md             # NOVO
  rules/
    caveman-activate.md          # INTOCADO
    caveman-activate.pt-br.md    # NOVO (opcional; ativar se houver demanda por regras BR em cursor/cline)
  evals/
    prompts/
      en.txt                     # INTOCADO
      pt-br.txt                  # NOVO
    llm_run.py                   # ATUALIZADO (aceita --lang, usa prompts correspondentes)
    measure.py                   # ATUALIZADO (reporta por lang)
    snapshots/
      results.json               # EN (existente)
      results-pt-br.json         # NOVO (snapshots do fork)
    README.md                    # EN reduzido
    README.pt-br.md              # NOVO
  benchmarks/
    prompts.json                 # INTOCADO
    prompts.pt-br.json           # NOVO
    run.py                       # ATUALIZADO (aceita --lang)
    results/                     # contem resultados EN + pt-br (prefixo no nome do arquivo)
  tests/
    test_hooks.py                # ATUALIZADO (cobre i18n e modo caveman-ptbr)
    verify_repo.py               # ATUALIZADO (checa existencia de arquivos .pt-br.md paralelos)
    verify_locales.py            # NOVO (ADR-003 item 5)
    caveman-compress/
      *.original.md              # INTOCADO (EN)
      *.md                       # INTOCADO
      pt-br/
        *.original.md            # NOVO (5 pares)
        *.md                     # NOVO
  README.md                      # EN reduzido (aponta para README.pt-br.md)
  README.pt-br.md                # NOVO canonico
  CONTRIBUTING.md                # EN reduzido
  CONTRIBUTING.pt-br.md          # NOVO
  CLAUDE.md                      # INTOCADO (instrucoes para agente trabalhando no repo; EN)
  CLAUDE.pt-br.md                # NOVO (equivalente PT-BR)
  GEMINI.md                      # INTOCADO
  AGENTS.md                      # INTOCADO (apenas referencias @path)
  docs/
    index.html                   # EN reduzido OU redirect
    index.pt-br.html             # NOVO canonico
  plugins/
    caveman/                     # auto-synced (ver CI abaixo)
  .cursor/, .windsurf/, .clinerules/, .github/copilot-instructions.md
                                 # auto-synced
```

### 2. Convencao de sufixo `.pt-br.md`

- Sufixo escolhido: `.pt-br.md` (BCP 47 language tag, lowercase).
- Motivos: case consistente com `CAVEMAN_LANG=pt-br`, legivel em file listing, facil glob (`*.pt-br.md`).
- Rejeitadas: `.pt_BR.md` (underscore/case confusos para filesystems case-insensitive), `-pt-br.md` sem ponto (mistura com nomes de feature), diretorio `pt-br/` para cada doc (excesso de aninhamento para um fork com ~15 arquivos).
- EXCECAO: `tests/caveman-compress/pt-br/` usa diretorio porque sao FIXTURES multiplas agrupaveis, nao documentos.

### 3. Atualizacao do CI (`.github/workflows/sync-skill.yml`)

Mudancas incrementais (preservando steps existentes):

**Trigger** (adicionar paths):
```
  - skills/caveman/SKILL.pt-br.md
  - skills/caveman-commit/SKILL.pt-br.md
  - skills/caveman-review/SKILL.pt-br.md
  - skills/caveman-help/SKILL.pt-br.md
  - caveman-compress/SKILL.pt-br.md
  - rules/caveman-activate.pt-br.md
  - locales/**
```

**Steps adicionados**:
1. Sync `skills/caveman/SKILL.pt-br.md` para destinos paralelos:
   - `caveman/SKILL.pt-br.md`
   - `plugins/caveman/skills/caveman/SKILL.pt-br.md`
   - `.cursor/skills/caveman/SKILL.pt-br.md`
   - `.windsurf/skills/caveman/SKILL.pt-br.md`
2. Sync `locales/*.json` para `plugins/caveman/locales/` (se plugin precisar em runtime)
3. Rebuild `caveman.skill` ZIP incluindo `SKILL.pt-br.md` e `locales/`
4. Rebuild dos agent rule files mantendo EN (default) — versoes PT-BR dos rule files ficam como arquivos paralelos se/quando `rules/caveman-activate.pt-br.md` existir, com mesmo pattern frontmatter
5. (Opcional) Rodar `python tests/verify_locales.py` como gate

**Commit message pattern** mantido: `sync: update skill files [skip ci]`.

### 4. Install/uninstall scripts

`hooks/install.sh` e `install.ps1` atualizados para:
1. Copiar `hooks/caveman-*.js` para `~/.claude/hooks/` (como hoje)
2. Copiar `hooks/caveman-i18n.js` (novo)
3. Copiar `locales/` inteiro para `~/.claude/locales/` OU `~/.claude/hooks/locales/` (resolver JS tentara ambos via fallback do ADR-004)
4. Patchear `settings.json` (como hoje) + opcionalmente setar `CAVEMAN_LANG` se variavel nao existir (ou apenas documentar no output do install)

`uninstall.sh/ps1` atualizados para remover tambem `locales/` e `caveman-i18n.js`.

### 5. Links cruzados em docs

Todo doc EN reduzido inclui no topo:
```
> PT-BR speakers: see [README.pt-br.md](./README.pt-br.md) for the full content.
```

Todo doc PT-BR canonico inclui no topo:
```
> English version (simplified): see [README.md](./README.md)
```

### 6. Merge/rebase strategy com upstream

- EN files (SKILL.md, README.md reduzido, prompts EN, fixtures EN) ficam alinhados com upstream -> rebase sem conflito na maioria dos casos.
- PT-BR files sao 100% fork-only -> zero conflito com upstream.
- SKILL.md tera secao `caveman-ptbr` NOVA adicionada. Conflito potencial se upstream alterar secoes adjacentes; resolve-se mantendo ambas.
- Scripts JS/Python sofrem edits no fork (para consumir i18n). Esses SAO pontos de conflito de rebase; documentar padrao "envolva string com `t('key')` em vez de literal" para minimizar churn.

## Alternatives Considered

### Diretorio por locale (ex: `locales/pt-br/README.md`, `locales/en/README.md`)
- **Pros**: agrupa tudo por locale
- **Cons**: afasta docs do contexto (hooks/README.pt-br.md perto de hooks/ faz mais sentido que locales/pt-br/hooks/README.md); hostil ao GitHub Pages e a ferramentas que esperam README.md no root
- **Why not chosen**: sufixo co-localizado e mais idiomatico.

### Gerar EN automaticamente do PT-BR (LLM translation no CI)
- **Pros**: uma fonte so
- **Cons**: adiciona dep de CI na Anthropic/LLM, quebra determinismo, custo recorrente, risco de drift silencioso
- **Why not chosen**: viola zero-dep e nao-determinismo. Humano cura EN reduzido manualmente.

### Manter sync-skill.yml intocado; sync PT-BR em workflow separado
- **Pros**: isolamento
- **Cons**: dois workflows sobre mesmos paths -> race conditions e duplo commit
- **Why not chosen**: estender o existente e mais simples.

## Consequences

### Positive
- Estrutura previsivel e googlavel
- CI continua idempotente e faz commit unico por mudanca
- Install scripts cobrem locales automaticamente
- Rebase upstream viavel

### Negative
- sync-skill.yml fica maior (mais steps)
- Install scripts tem um passo extra (copiar locales/)
- Gestao de ~15 pares de arquivos paralelos

### Risks
- **CI comitta PT-BR antes que todos os paralelos estejam prontos**: mitigado por trigger path-specific; PRs devem passar verify_locales/verify_repo antes de merge
- **Symlinks/case-insensitive filesystems (macOS/Windows)**: sufixo `.pt-br` em lowercase evita conflito com `.PT-BR`

## Protected Areas

- `.github/workflows/sync-skill.yml` (allowedChanges: with-architect-approval)
- convencao de sufixo `.pt-br.md` — mudar exige migration plan (renomear todos os arquivos, atualizar CI, atualizar links)

## Related Decisions

- ADR-001..005 (todas as demais)
