# ADR-001: Estrategia dual-language — locale files JSON + runtime flag

**Status**: accepted
**Date**: 2026-04-14
**Deciders**: architect

## Context

O fork caveman-ptbr precisa suportar dois idiomas de interface: PT-BR (default) e EN (secundario). O projeto upstream e 100% EN e tem caracteristicas arquiteturais fortes:

- Zero dependencias de runtime em hooks JS (apenas Node.js stdlib)
- Zero dependencias de i18n em qualquer parte do codigo
- Sem package manager JS (nao ha package.json)
- Python CLI usa apenas stdlib + anthropic SDK opcional
- Conteudo e predominantemente Markdown (SKILL.md, README, docs)

Precisamos decidir COMO implementar dual-language sem violar esses principios e sem dificultar rebases contra upstream.

## Decision

Adotar **opcao (a) modificada: locale files JSON + runtime flag, com arquivos Markdown paralelos**.

Estrutura:

1. **Strings curtas (hooks JS, CLI Python)**: duas dict files em `locales/pt-br.json` e `locales/en.json`, com chaves namespaced (`hooks.activate.banner`, `cli.compress.starting`). Lidas via `JSON.parse` nativo e `json.load` stdlib.

2. **Documentos longos (Markdown)**: arquivos paralelos com sufixo de locale. `README.pt-br.md` (canonico do fork) e `README.md` (EN simplificado upstream-compat). `skills/caveman/SKILL.pt-br.md` canonico paralelo, `SKILL.md` preservado EN.

3. **Runtime flag**: variavel de ambiente `CAVEMAN_LANG` (valores `pt-br` | `en`). Ausente ou invalida = `pt-br` (default do fork). CLI aceita `--lang=en` como override adicional.

4. **Build nao-separado**: mesmo codigo serve ambos locales. Sem forks de build, sem artefatos separados por idioma.

## Alternatives Considered

### Opcao (a) pura: locale files + runtime flag apenas para strings
- **Pros**: minimalista, zero-dep
- **Cons**: nao cobre documentos longos (README, SKILL.md) que nao cabem em JSON dict
- **Why not chosen**: subespecificada. Precisa ser complementada para Markdown.

### Opcao (b): builds separados por idioma
- **Pros**: cada build e 100% monolingue, simples em runtime
- **Cons**: exige infra de build que nao existe, dobra superficie de CI, dobra custo de manutencao, complica distribuicao (`npx skills`, plugin install)
- **Why not chosen**: viola P-001 (zero-dependency) e multiplica trabalho de manutencao. Fork ficaria impossivel de rebasear.

### Opcao (c): flag runtime com conteudo bilingue inline
- **Pros**: um arquivo so, escolha por condicional no runtime
- **Cons**: polui Markdown com marcadores, inviavel para textos longos como README (403 linhas), dificulta revisao de paridade
- **Why not chosen**: ilegivel em escala e hostil a contribuidores.

### Opcao (d): locale files apenas, sem flag runtime (detectar por LANG do sistema)
- **Pros**: zero config pro usuario
- **Cons**: em hooks rodando em agentes, `$LANG` pode nao refletir preferencia do desenvolvedor. Comportamento nao-deterministico em CI e docker.
- **Why not chosen**: nao-deterministico. Flag explicita + default sensato e preferivel.

## Consequences

### Positive
- Paridade entre stacks (JS e Python usam mesmo padrao de dict + resolver com fallback)
- Zero-dep mantido; alinha com P-001 e filosofia upstream
- Rebase com upstream tranquilo: arquivos EN originais permanecem no lugar, PT-BR vive em arquivos paralelos
- Usuario pode alternar via `CAVEMAN_LANG=en` sem reinstalar

### Negative
- Duplicacao de conteudo Markdown (README e README.pt-br). Gerenciavel via checklist de review e required_keys (ver ADR-003)
- CI de sync (sync-skill.yml) precisa de steps adicionais para propagar SKILL.pt-br.md (ver ADR-006)

### Risks
- **Drift entre locales**: paridade de chaves JSON pode divergir. **Mitigacao**: script de verificacao em `tests/verify_locales.py` que compara chaves entre pt-br.json e en.json e falha em keys EN ausentes se listadas em required_keys (ADR-003).
- **Falha ao carregar locale em runtime**: mitigada pelo cascade fallback (ADR-004) e principio P-004.

## Protected Areas

Esta decisao estabelece o formato canonico. Ver `protected_areas.json` para as guardrails relacionadas.

## Related Decisions

- ADR-002: define o que entra nos arquivos de locale vs o que fica preservado
- ADR-003: contrato de paridade e required_keys
- ADR-004: mecanismo tecnico de resolucao
- ADR-006: organizacao de arquivos e integracao com CI
