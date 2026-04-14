# ADR-007: PT-BR nativo como output default; remocao de wenyan e sufixos ptbr-*

**Status**: accepted
**Date**: 2026-04-14
**Deciders**: architect
**Supersedes**: ADR-005 (modo caveman-ptbr separado); revoga parcialmente ADR-002 (categoria 3 e 7)

## Context

ADRs anteriores (002, 005) foram escritos sob a premissa de que o fork caveman-ptbr seria uma **camada de i18n aditiva** sobre o upstream caveman, preservando o output caveman-speak em ingles quebrado como feature core e oferecendo PT-BR apenas como modo adicional (analogo ao wenyan).

O usuario definiu uma nova direcao de produto que invalida essa premissa:

1. Este fork e **PT-BR-first nativo**, nao um upstream com camada BR opcional.
2. Os modos base (`/caveman`, `/caveman lite`, `/caveman ultra`) devem emitir output em **portugues de caverna** nativamente. Nao ha mais "broken EN" como default.
3. Os sufixos `ptbr-*` tornam-se redundantes (eram atalhos para um modo que agora e o default).
4. O modo **wenyan (chines classico)** nao e objetivo deste fork e deve ser **removido completamente**.

P-002 ("Preserve Upstream Behavior") era a justificativa para manter o output EN; fazia sentido quando EN era o default e PT-BR um adicional. Com a inversao, preservar o output EN deixa de servir ao produto.

## Decision

### 1. Output default nos modos base = PT-BR de caverna

- `/caveman` -> output em portugues de caverna (full)
- `/caveman lite` -> output em portugues de caverna (lite)
- `/caveman ultra` -> output em portugues de caverna (ultra)

Regras linguisticas de "portugues de caverna" (ja definidas em ADR-005 secao 2) passam a ser as regras **unicas e canonicas** nos modos base:
- Verbos no infinitivo ou imperativo curto
- Artigos removidos
- Flexao de numero elidida quando obvia
- Concordancia verbal simplificada
- Preposicoes reduzidas
- Padroes Sim/Nao (em vez de Yes/Not)
- Codigo, URLs, paths, nomes proprios preservados literalmente
- Auto-clarity rule preservada (security warnings, irreversible actions, etc. caem para PT formal)

### 2. Sufixos `ptbr-*` removidos

`caveman-ptbr`, `caveman-ptbr-lite`, `caveman-ptbr-ultra`, `ptbr`, `ptbr-lite`, `ptbr-ultra` deixam de ser modos reconhecidos. `hooks/caveman-mode-tracker.js` nao deve ter patterns para eles. O flag file nao deve aceitar esses valores.

Motivo: sao redundantes com o default novo.

### 3. Wenyan removido completamente

Toda referencia a `wenyan`, `wenyan-lite`, `wenyan-full`, `wenyan-ultra` deve ser **extirpada** do fork:
- Remover secao wenyan de `skills/caveman/SKILL.md` (e SKILL.pt-br.md se houver)
- Remover patterns wenyan de `hooks/caveman-mode-tracker.js`
- Remover badges wenyan de `hooks/caveman-statusline.sh` e `.ps1`
- Remover mencoes em README, README.pt-br, CLAUDE.md, docs/, rules/
- Remover de qualquer manifest/plugin.json

Motivo: chines classico nao e escopo deste fork. Carregar a feature apenas aumenta superficie de manutencao sem servir ao publico-alvo (comunidade BR).

### 4. Comandos continuam em EN (nomes de comando)

Os comandos `/caveman`, `/caveman lite`, `/caveman ultra`, `/caveman-commit`, `/caveman-review`, `/caveman-compress` mantem seus **nomes em EN**. O que muda e o **output** que produzem.

Motivo: compatibilidade com ecossistema upstream e com muscle memory de usuarios. E um fork PT-BR, mas a superficie de comando continua sendo caveman.

### 5. Interface (CLI/hooks/docs) continua PT-BR-first com EN disponivel

ADR-003 (paridade EN) e ADR-004 (mecanismo locale via CAVEMAN_LANG) continuam validos. A novidade e que o **output do agente** tambem e PT-BR default, alinhando com a interface.

### 6. Benchmarks e evals

- Benchmarks PT-BR passam a ser os numeros principais do fork (ja nao ha "output EN default" para comparar contra).
- `evals/prompts/en.txt` pode ser preservado como fixture historica, mas deixa de ser o benchmark canonico. `evals/prompts/pt-br.txt` torna-se canonico.
- Fixtures `tests/caveman-compress/*.original.md` em EN podem ser preservadas para regressao estrutural, mas os pares golden canonicos passam a ser PT-BR.

## Migration Plan

### Arquivos a modificar

1. **`skills/caveman/SKILL.md`**:
   - Reescrever regras caveman-speak em PT-BR (portugues de caverna)
   - Remover secao wenyan-*
   - Remover secao caveman-ptbr (deixa de ser modo separado; suas regras sao agora as regras do modo base)
   - Manter estrutura de intensidades: lite / full / ultra
   - Exemplos before/after em PT-BR natural

2. **`hooks/caveman-mode-tracker.js`**:
   - Remover patterns `/caveman wenyan*`, `/caveman ptbr*`, `/caveman caveman-ptbr*`
   - Manter apenas: `/caveman`, `/caveman lite`, `/caveman ultra`, `/caveman-commit`, `/caveman-review`, `/caveman-compress`
   - Flag file aceita apenas: `full`, `lite`, `ultra`, `commit`, `review`, `compress`

3. **`hooks/caveman-statusline.sh` e `.ps1`**:
   - Remover cases para wenyan e ptbr
   - Manter apenas `[CAVEMAN]`, `[CAVEMAN:LITE]`, `[CAVEMAN:ULTRA]`, `[CAVEMAN:COMMIT]`, `[CAVEMAN:REVIEW]`, `[CAVEMAN:COMPRESS]`

4. **`hooks/caveman-activate.js`**:
   - Fallback ruleset hardcoded reescrito em PT-BR (ou via locale)

5. **README.md / README.pt-br.md / CLAUDE.md**:
   - Remover mencoes a wenyan
   - Remover mencoes a ptbr-* como modo separado
   - Ajustar tabela de intensidades: apenas lite/full/ultra
   - Documentar que output e PT-BR nativo

6. **`rules/caveman-activate.md`**:
   - Reescrever corpo em PT-BR (portugues de caverna) ou ajustar para refletir output PT-BR
   - Remover mencoes a wenyan

7. **Plugins/manifests** (`plugins/caveman/`, `.cursor/`, `.windsurf/`, `.clinerules/`, `AGENTS.md`, `.github/copilot-instructions.md`):
   - Ressincronizar apos edicoes em SSOT via CI

8. **`evals/` e `benchmarks/`**:
   - PT-BR prompts tornam-se canonicos
   - Regenerar snapshots

### Ordem sugerida de execucao

1. Editar SSOT (`skills/caveman/SKILL.md`, `rules/caveman-activate.md`)
2. Editar hooks (mode-tracker, statusline, activate)
3. Editar docs (README, CLAUDE.md)
4. Deixar CI sincronizar copies
5. Regenerar evals/benchmarks PT-BR
6. Atualizar testes

## Alternatives Considered

### Manter output EN default e PT-BR apenas como modo opcional (status quo ADR-005)
- **Pros**: minimo impacto, rebase upstream trivial
- **Cons**: usuario definiu que fork e PT-BR-first. Default EN nao reflete o produto.
- **Why not chosen**: decisao de produto explicita do usuario.

### Manter sufixos `ptbr-*` como aliases do default
- **Pros**: tolerancia a usuarios que digitarem o sufixo
- **Cons**: ruido de manutencao; os sufixos apontam para o mesmo modo; cria impressao falsa de que ha diferenca
- **Why not chosen**: redundancia confunde mais do que ajuda. Se desejado, aceitacao lenient pode ser adicionada no tracker como alias silencioso, mas nao documentado.

### Manter wenyan "porque ja estava la"
- **Pros**: esforco zero
- **Cons**: codigo morto no fork; confunde usuarios BR; aumenta superficie de teste
- **Why not chosen**: fork tem escopo definido; feature fora do escopo sai.

## Consequences

### Positive
- Produto alinhado com identidade do fork (PT-BR-first de verdade, nao aditivo)
- Superficie menor: 3 modos (lite/full/ultra) + 3 skills (commit/review/compress), sem wenyan nem ptbr-*
- Benchmarks PT-BR deixam de ser "numeros secundarios" e passam a ser os numeros do produto
- Mensagens de hook, CLI, docs, output — tudo coerente em PT-BR

### Negative
- Rebase com upstream fica mais dificil (output core divergiu)
- Perda de comparabilidade direta com benchmarks upstream EN (mitigacao: documentar que sao produtos diferentes agora)
- Usuarios EN que usassem este fork perdem caveman-speak EN (solucao: apontar para upstream original)

### Risks
- **Ratio de compressao PT-BR diferente do upstream EN**: aceito. Reportar honestamente (P-002 relaxado mas "never invent or round" continua valido).
- **Regras PT-BR de caverna mal calibradas**: mitigar com evals PT-BR como canonicos.
- **Rebase futuro com upstream sofre**: aceito como custo da escolha de produto. Documentar em CONTRIBUTING.pt-br.md que rebase e cherry-pick, nao merge direto.

## Protected Areas (atualizacao)

Remover do protected_areas.json:
- `skills/caveman/SKILL.md#wenyan-*` (feature removida)
- `skills/caveman/SKILL.md#caveman-speak-rules` (regras EN substituidas por PT-BR; nao ha mais regra EN para proteger)

Manter (com notas revisadas):
- `skills/caveman/SKILL.md` continua protegido como SSOT, mas agora SSOT do comportamento PT-BR-first. Nao ha mais "upstream-compat byte-a-byte".
- Algoritmos idioma-agnosticos (`validate.py`, `detect.py`) continuam protegidos.
- Flag file continua protegido, mas schema reduz (sem wenyan, sem ptbr-*).

## Related Decisions

- ADR-001: dual-language (ainda valido; pt-br default reforcado)
- ADR-002: parcialmente revogado — categoria 3 (preservar output EN) e categoria 7 (wenyan intocado) invalidadas
- ADR-003: paridade EN (ainda valido para interface)
- ADR-004: i18n mecanico (ainda valido para interface)
- ADR-005: **superseded por esta decisao** — modo caveman-ptbr deixa de existir como modo separado; suas regras viram default
- ADR-006: organizacao de arquivos e CI (ainda valido, ajustar steps de sync para remover wenyan)
