# ADR-003: Contrato de paridade EN simplificado

**Status**: accepted
**Date**: 2026-04-14
**Deciders**: architect

## Context

Com PT-BR como locale default do fork e EN como secundario (ADR-001, ADR-002), precisamos um contrato explicito de:

- O que EN OBRIGATORIAMENTE deve ter (required_keys)
- O que pode faltar em EN e fazer fallback
- Como placeholders (`{mode}`, `{file}`, `{count}`) se mantem consistentes entre locales
- Como se previne drift

Sem contrato, ha risco de (a) regressao silenciosa de usuarios EN, (b) crash em runtime por chave ausente, (c) incoerencia de placeholders entre locales.

## Decision

### 1. Lista de required_keys (EN OBRIGATORIO)

Um arquivo `locales/required_keys.json` enumera as chaves que DEVEM existir em ambos `pt-br.json` e `en.json`. Categorias cobertas (prefixos namespaced):

```
hooks.activate.banner
hooks.activate.banner_with_mode
hooks.activate.statusline_nudge
hooks.activate.fallback_ruleset
hooks.mode_tracker.mode_set
hooks.mode_tracker.mode_cleared
cli.usage
cli.file_not_found
cli.not_a_file
cli.detected
cli.skipping_not_natural
cli.compress.starting
cli.compress.success
cli.compress.error
cli.compress.interrupted
cli.compress.processing
cli.compress.validating
cli.compress.validation_passed
cli.compress.validation_failed
cli.compress.fixing
cli.compress.failed_after_retries
cli.compress.original
cli.compress.compressed
```

Total: ~22 chaves minimas. Lista concreta final vive em `locales/required_keys.json` e e mantida junto com mudancas de codigo.

### 2. O que pode faltar em EN (fallback permitido)

- Chaves introduzidas por features EXCLUSIVAS do fork PT-BR que nao fazem sentido em EN (ex: mensagens do modo caveman-ptbr exibidas so quando CAVEMAN_LANG=pt-br + modo=caveman-ptbr). Estas sao OPTATIVAS em en.json.
- Exemplos didaticos muito especificos de PT-BR (tom/regionalismo) podem ter versao EN simplificada ou generica.
- Texto longo de docs (README completo em PT-BR) NAO precisa de equivalente 1:1 em EN — README EN e INTENCIONALMENTE reduzido e aponta para README.pt-br.md como fonte completa.

Fallback cascade em runtime:
1. Chave no locale requisitado (`en.json` se `CAVEMAN_LANG=en`)
2. Chave em `pt-br.json` (default do fork)
3. Literal EN hardcoded em codigo (silent-fail salvaguarda)

### 3. Politica de placeholders

- Placeholders usam sintaxe `{name}` (chaves em snake_case ou camelCase; preferir snake_case para consistencia).
- **Mesmos placeholders em todos os locales para a mesma chave**. Se `hooks.activate.banner_with_mode` usa `{mode}` em pt-br.json, DEVE usar `{mode}` em en.json. Troca de nome e breaking change.
- Placeholders nunca sao traduzidos (ex: `{file}` nunca vira `{arquivo}`).
- Ordem dos placeholders pode variar entre locales (naturalidade linguistica) — o resolver usa substituicao por nome, nao por posicao.
- Validador de paridade (ver item 5) checa que o conjunto de placeholders por chave e IDENTICO entre locales.

### 4. README EN: essencial apenas

README.md EN mantem:
- **Badge/hero section**: 1 paragrafo caveman-voice EN
- **Before/After example**: 1 par (o mais impactante)
- **Install quick table**: todas as linhas, mas sem detail blocks (detail blocks vao em `<details>` no PT-BR)
- **Pointer explicito**: "This fork is PT-BR first. See [README.pt-br.md](README.pt-br.md) for full content."
- **Link para upstream**: reconhecimento do projeto original

README.md EN **nao mantem**:
- Feature matrix completa (vai so no PT-BR)
- Benchmark table detalhada (sumariza em 1 linha + link)
- Per-agent detail blocks (omitidos)

Meta: README EN cabe em <120 linhas. README PT-BR expande para ~400+ conforme necessario.

### 5. Verificacao automatizada de paridade

Criar `tests/verify_locales.py` (Python stdlib unittest, alinhado com estilo de verify_repo.py):

- Carrega `locales/en.json`, `locales/pt-br.json`, `locales/required_keys.json`
- Assert: toda chave em required_keys existe em ambos locales
- Assert: para cada chave presente em ambos, o conjunto de placeholders `{xxx}` e identico
- Assert: JSON valido e sem chaves duplicadas
- Rodado manualmente (`python tests/verify_locales.py`) e como step opcional no CI (se/quando CI passar a rodar testes — hoje nao roda).

Falha no verificador e BREAKING; nao-negociavel para introducao de nova chave.

## Alternatives Considered

### Paridade estrita 100% (toda chave PT-BR deve ter EN)
- **Pros**: zero fallback necessario
- **Cons**: obriga traduzir EN para mensagens que so fazem sentido em modo PT-BR, polui en.json com textos redundantes
- **Why not chosen**: rigido demais e contra filosofia "EN simplificado".

### Sem contrato (best-effort)
- **Pros**: zero trabalho de verificacao
- **Cons**: drift garantido, regressoes silenciosas, experiencia EN pode colapsar sem ninguem notar
- **Why not chosen**: incompativel com quality bar do upstream.

### Paridade por tiers (S/A/B)
- **Pros**: granularidade
- **Cons**: overhead de categorizacao para projeto pequeno
- **Why not chosen**: required_keys binario (obrigatorio sim/nao) + fallback cobre os casos com complexidade menor.

## Consequences

### Positive
- EN permanece funcional com esforco minimo de manutencao
- Validador automatizado previne regressao
- Placeholders consistentes eliminam classe de bugs

### Negative
- Mais um arquivo (`required_keys.json`) e um script de verificacao para manter
- Contrato explicito exige disciplina ao adicionar chave nova

### Risks
- **Desenvolvedor adiciona chave em pt-br.json e esquece en.json**: verify_locales.py detecta. Mitigacao concreta.
- **Placeholder diverge entre locales**: verify_locales.py detecta.

## Protected Areas

- `locales/required_keys.json` requer architect-approval para mudar (e o contrato publico do fork).

## Related Decisions

- ADR-001: estrategia dual-language (contexto geral)
- ADR-004: mecanismo de resolucao implementa o fallback cascade
- ADR-006: organizacao de arquivos
