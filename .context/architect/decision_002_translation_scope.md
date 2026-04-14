# ADR-002: Escopo — o que se traduz/adapta versus o que se preserva

**Status**: accepted (com revogacao parcial — ver Addendum 2026-04-14 #2)
**Date**: 2026-04-14
**Deciders**: architect

## Addendum 2026-04-14 #2 — Revogacao parcial por ADR-007

Apos mudanca de direcao do produto (fork PT-BR-first nativo), as seguintes categorias deste ADR foram **revogadas**:

- **Categoria 3 (PRESERVAR output caveman-speak EN)**: REVOGADA. O output caveman-speak nos modos base (`full`, `lite`, `ultra`) passa a ser **portugues de caverna** como default. Nao ha mais preservacao byte-a-byte do upstream para regras de compressao.
- **Categoria 4 (Modo adicional caveman-ptbr via ADR-005)**: REVOGADA. Nao ha mais "modo adicional" — PT-BR de caverna virou o **default dos modos base**. Sufixos `ptbr-*` nao existem mais.
- **Categoria 7 (Wenyan intocado)**: REVOGADA. Modo wenyan e **removido completamente** do fork — nao e escopo.

Categorias 1 (Interface), 2 (Documentacao), 5 (Prompts bilingue em compress), 6 (Fixtures aditivas EN+PT) **permanecem validas**.

Ver ADR-007 para justificativa completa, migration plan e consequences.


## Context

O fork caveman-ptbr precisa uma linha clara entre:
- **Interface** (o que o usuario le AO USAR o produto: mensagens, docs, exemplos)
- **Feature core** (o output caveman-speak em ingles quebrado, que E o produto)

Traduzir erroneamente o output core descaracteriza o produto. Preservar demais em EN descaracteriza o fork. Esta decisao define categoria por categoria.

## Decision

### Categoria 1 — Interface (TRADUZIR para PT-BR default, EN como secundario)

- **Mensagens de hooks JS** (`hooks/caveman-activate.js`, `caveman-mode-tracker.js`): banner "CAVEMAN MODE ACTIVE", nudge de statusline setup, mensagens de erro visiveis. Movidas para `locales/<lang>.json`.
- **Mensagens do CLI Python** (`caveman-compress/scripts/cli.py`, `compress.py`): "Processing:", "Compressing with Claude...", "Validation attempt N", "Failed after retries", etc. Movidas para `locales/<lang>.json` e resolvidas via `i18n.py`.
- **Statusline badge**: `[CAVEMAN]` permanece identico (brand/marca curta, nao e prosa). `[CAVEMAN:ULTRA]` idem. NAO traduzir — e identificador visual.
- **plugin.json / manifests**: campos `statusMessage` ("Loading caveman mode..."), `description` de plugin. PT-BR default + EN variants onde o schema permitir; caso contrario, PT-BR.
- **Fallback ruleset hardcoded** em `caveman-activate.js` (linhas 101-115): move para arquivo de locale.

### Categoria 2 — Documentacao (ADAPTAR culturalmente para PT-BR + versao EN simplificada)

- **README.md**: permanece EN, mas REDUZIDO ao essencial (install table, Before/After, pointer para README.pt-br.md). Voz caveman preservada em EN.
- **README.pt-br.md**: versao PT-BR COMPLETA e canonica do fork. Voz caveman adaptada para portugues ("Cerebro ainda grande.", "Uma pedra. So isso."). Cumpre funcao de product front door para comunidade BR.
- **CONTRIBUTING.md**: versao PT-BR canonica (`CONTRIBUTING.pt-br.md`) + EN reduzido.
- **caveman-compress/README.md**, **hooks/README.md**, **evals/README.md**: versoes PT-BR canonicas em `.pt-br.md` paralelos; EN mantidos reduzidos.
- **docs/index.html**: versao PT-BR em `docs/index.pt-br.html` ou `docs/pt-br/index.html`. EN mantido para GitHub Pages default (ou redirect baseado em Accept-Language — decisao de implementacao).
- **SKILL.md (skills/caveman/)**: ver categoria 3.

### Categoria 3 — Output caveman-speak e regras de compressao (PRESERVAR EN)

- **skills/caveman/SKILL.md**: PRESERVADO byte-a-byte do upstream. Este arquivo define o output caveman-speak (broken EN) que E a feature. Editar descaracteriza o produto e quebra SSOT com upstream.
- **skills/caveman/SKILL.pt-br.md**: arquivo paralelo NOVO do fork, com regras de interface em PT-BR mas preservando que o OUTPUT do agente continua broken EN quando modo = full/lite/ultra.
- **rules/caveman-activate.md**: preservado EN. Adicionar `rules/caveman-activate.pt-br.md` paralelo para uso em regras distribuidas (Cline PT, Cursor PT, etc.) se/quando pertinente.
- **skills/caveman-commit/SKILL.md**, **caveman-review/SKILL.md**, **caveman-help/SKILL.md**: preservados EN. Criar `.pt-br.md` paralelos.

### Categoria 4 — Modo adicional caveman-ptbr (NOVO — ver ADR-005)

- Modo novo "portugues de caverna" analogo ao wenyan. Regras em `skills/caveman/SKILL.md` (secao adicional, sim, incorporada ao upstream-compat file) e detalhadas em `SKILL.pt-br.md`.
- NAO substitui modos existentes. E ativado via `/caveman ptbr`.

### Categoria 5 — Prompts para o LLM em caveman-compress (BILINGUE CONDICIONAL)

- `compress.py:build_compress_prompt()` e `build_fix_prompt()` sao prompts enviados ao Claude. Devem detectar idioma do INPUT (ja ha `detect.py`) e usar prompt apropriado:
  - Input EN -> prompt em EN (como upstream, preservado)
  - Input PT-BR -> prompt novo em PT-BR que instrui compressao para "portugues de caverna" (regras PT-BR analogas: verbos no infinitivo, sem artigos, sem flexao de numero quando obvia)
- Prompt escolhido conforme detectado, nao conforme `CAVEMAN_LANG`. Input e fonte de verdade do idioma do conteudo.

### Categoria 6 — Fixtures de evals/benchmarks/tests (ADITIVO — NAO SUBSTITUIR)

- **evals/prompts/en.txt**: PRESERVADO. Nao remover. Nao traduzir em cima.
- **evals/prompts/pt-br.txt**: NOVO. 10 perguntas tecnicas equivalentes em PT-BR (nao traducao literal; adaptacao cultural de exemplos quando util).
- **benchmarks/prompts.json**: PRESERVADO. Criar `benchmarks/prompts.pt-br.json` paralelo OU estender schema com campo `lang` (decisao de implementacao; default primeiro: arquivo paralelo).
- **tests/caveman-compress/*.original.md**: PRESERVADOS. Criar pasta `tests/caveman-compress/pt-br/` com 5 novos pares canonicos para testar compressao de texto portugues.

### Categoria 7 — Wenyan (INTOCADO)

- Modo wenyan (chines classico) permanece exatamente como no upstream. Nao e escopo do fork.

## Alternatives Considered

### Traduzir tudo incluindo output caveman-speak para PT-BR
- **Pros**: consistencia linguistica total
- **Cons**: descaracteriza o produto. O output broken-EN e a feature vendida. Benchmarks de compressao nao seriam comparaveis.
- **Why not chosen**: quebra o produto.

### Traduzir apenas docs, deixar hooks/CLI em EN
- **Pros**: minimo esforco
- **Cons**: usuario BR le README PT e depois encontra hook gritando "CAVEMAN MODE ACTIVE" e CLI com "Compressing with Claude..." — experiencia rachada.
- **Why not chosen**: experiencia incoerente.

### Substituir fixtures EN por PT-BR
- **Pros**: menos arquivos
- **Cons**: quebra comparabilidade com upstream e com benchmarks publicos ja commitados
- **Why not chosen**: quebra honestidade de benchmark.

## Consequences

### Positive
- Linha clara: interface = PT-BR, feature = preservada EN
- Upstream rebase permanece trivial (arquivos EN originais intocados)
- Benchmarks BR novos nao competem com nem anulam benchmarks upstream EN
- Voz caveman preservada em ambos idiomas (P-007)

### Negative
- Duplicacao: cada doc longo existe em 2 versoes
- Fixtures duplicadas em 2 idiomas aumentam massa de teste

### Risks
- **Drift entre versao EN simplificada e PT-BR completa**: EN pode ficar desatualizada. **Mitigacao**: ADR-003 define required_keys minimos que EN deve conter; EN curto e intencional, nao bug.
- **Confusao do usuario BR ao ver output em broken-EN mesmo com CAVEMAN_LANG=pt-br**: **Mitigacao**: README.pt-br deixa claro que o OUTPUT caveman-speak e em ingles proposital (brand/feature); modo `caveman-ptbr` (ADR-005) e a opcao para quem quer output em portugues de caverna.

## Protected Areas

Ver `protected_areas.json`:
- `skills/caveman/SKILL.md#caveman-speak-rules` (allowedChanges: none)
- `skills/caveman/SKILL.md#wenyan-*` (allowedChanges: none)
- `caveman-compress/scripts/validate.py` e `detect.py` (idioma-agnosticos)
- `evals/prompts/en.txt` (allowedChanges: none — aditivo apenas)
- `benchmarks/prompts.json`
- `tests/caveman-compress/*.original.md`

## Related Decisions

- ADR-001: estrategia dual-language
- ADR-003: contrato de paridade EN
- ADR-005: modo caveman-ptbr
- ADR-006: organizacao de arquivos e CI
