# ADR-005: Modo caveman-ptbr — portugues de caverna como modo adicional

**Status**: superseded (por ADR-007 em 2026-04-14)
**Date**: 2026-04-14
**Deciders**: architect
**Superseded By**: ADR-007

> **Nota historica**: Este ADR propunha PT-BR de caverna como modo **adicional** (analogo ao wenyan), preservando modos base em EN. ADR-007 inverte a premissa: PT-BR de caverna vira o **default dos modos base** (`full`/`lite`/`ultra`), sufixos `ptbr-*` sao removidos por redundancia, e wenyan sai do escopo do fork. As regras linguisticas de "portugues de caverna" definidas na secao 2 deste ADR permanecem validas — apenas passam a ser aplicadas ao modo base em vez de um modo separado. Conteudo preservado abaixo para historico.


## Context

Usuarios BR que quiserem output comprimido em PT-BR (nao so interface) precisam de um modo. Traduzir o output core padrao para PT-BR descaracteriza o produto (ADR-002). A solucao arquitetural elegante ja existe no upstream: o modo **wenyan** (chines classico) e uma feature multi-idioma adicional, nao substitutiva.

Vamos aplicar o mesmo padrao: adicionar modo **caveman-ptbr** analogo ao wenyan, preservando todos os modos existentes.

## Decision

### 1. Novo modo: `caveman-ptbr` (e variantes)

Seguindo o template wenyan que ja tem `wenyan-lite`, `wenyan-full`, `wenyan-ultra`:

- `caveman-ptbr` (alias: `ptbr`) -> equivalente a `full` em PT-BR de caverna
- `caveman-ptbr-lite` (alias: `ptbr-lite`) -> equivalente a `lite`
- `caveman-ptbr-ultra` (alias: `ptbr-ultra`) -> equivalente a `ultra`

Ativacao:
- `/caveman ptbr` -> modo caveman-ptbr (full)
- `/caveman ptbr-lite`
- `/caveman ptbr-ultra`
- Aliases longos aceitos: `/caveman caveman-ptbr` etc.

Flag file `~/.claude/.caveman-active` passa a aceitar novos valores: `caveman-ptbr`, `caveman-ptbr-lite`, `caveman-ptbr-ultra`.

### 2. Regras linguisticas de "portugues de caverna"

Analogas a caveman-speak EN, adaptadas ao PT:

- **Verbos no infinitivo ou imperativo curto**: "configurar servidor" em vez de "voce precisa configurar o servidor"
- **Artigos removidos**: "rodar comando" em vez de "rodar o comando"
- **Flexao de numero elidida quando obvia**: "3 user logar" (nao "3 usuarios logaram")
- **Concordancia verbal simplificada**: verbo fica no infinitivo
- **Preposicoes reduzidas**: "arquivo src" em vez de "arquivo em src"
- **Padroes Sim/Nao**: "Sim: X. Nao: Y." analogo a "Yes:/Not:"
- **Codigo, URLs, paths, nomes proprios**: preservados literalmente (idem caveman-speak EN)
- **Auto-clarity rule**: mesmas excecoes (security warnings, irreversible actions, multi-step sequences, user confuso) caem para PT-BR formal normal

Ratio de compressao alvo: paridade com caveman-speak EN (~65-75%). Confirmar com benchmarks PT-BR novos (ver ADR-002 categoria 6 / ADR-006).

### 3. Documentacao das regras

- **Secao canonica (upstream-compat)**: adicionada a `skills/caveman/SKILL.md` como novo bloco apos `wenyan-*`. Permite sync CI para todos os destinos (Cursor, Windsurf, Cline, plugin/, etc.) e mantem SSOT upstream.
- **Detalhes editoriais e exemplos amplos**: em `skills/caveman/SKILL.pt-br.md` (arquivo paralelo PT-BR do fork).
- Exemplos devem incluir pelo menos 2 cenarios com before/after equivalentes aos exemplos EN (React/DB) mas em contexto PT-BR natural.

### 4. Hooks atualizados

- **`hooks/caveman-mode-tracker.js`**: adicionar regex/match para `/caveman ptbr`, `/caveman ptbr-lite`, `/caveman ptbr-ultra`, `/caveman caveman-ptbr`, etc. Escrever valor correspondente no flag file.
- **`hooks/caveman-statusline.sh` e `.ps1`**: adicionar cases para renderizar badge `[CAVEMAN:PTBR]`, `[CAVEMAN:PTBR-LITE]`, `[CAVEMAN:PTBR-ULTRA]`.
- **`hooks/caveman-activate.js`**: sem mudanca estrutural (apenas consome banner via i18n de ADR-004).

### 5. Escopo do modo

Modo caveman-ptbr AFETA:
- Output do agente Claude/LLM (o que o usuario ve como resposta)

Modo caveman-ptbr NAO AFETA:
- Interface do CLI (que e governada por CAVEMAN_LANG)
- Documentacao (idem)
- Algoritmos internos (validate.py, detect.py, etc.)

Combinacao valida: usuario pode ter `CAVEMAN_LANG=en` (CLI/docs em EN) E estar em modo `caveman-ptbr` (output do agente em portugues de caverna). As duas dimensoes sao ortogonais.

## Alternatives Considered

### Substituir modo `full` por caveman-ptbr quando CAVEMAN_LANG=pt-br
- **Pros**: automatico, menos config para usuario
- **Cons**: viola P-002 (preserve upstream behavior). Quebra expectativa do usuario upstream. Benchmarks deixam de ser comparaveis.
- **Why not chosen**: fere principio central.

### Fazer caveman-ptbr um fork separado (skill nova skills/caveman-ptbr/)
- **Pros**: isolamento total
- **Cons**: multiplica superficie de sync CI; perde-se a vantagem do modo ser "mais um" do arsenal; quebra o padrao wenyan que ja provou funcionar
- **Why not chosen**: padrao wenyan e melhor precedente.

### Nao adicionar modo, apenas traduzir interface
- **Pros**: minimo esforco
- **Cons**: usuario BR que quer output em PT fica sem opcao; fork perde diferencial
- **Why not chosen**: fork ficaria raso demais; principal valor e oferecer experiencia completa BR.

## Consequences

### Positive
- Paridade estrutural com wenyan (feature pattern reconhecivel)
- Preservacao total de modos existentes
- Ortogonalidade entre lingua de interface e lingua de output
- Novo diferencial do fork sem quebrar upstream

### Negative
- Mais 3 entries no flag file e no tracker
- Regras linguisticas PT-BR de caverna precisam validacao empirica (benchmarks)

### Risks
- **Regra de auto-clarity mal calibrada em PT-BR**: mitigar com evals PT-BR (ADR-002 cat 6)
- **Ratio de compressao PT-BR diferente de EN**: PT e linguisticamente mais verboso que EN. Aceito como resultado de benchmark; reportar honestamente nos numbers (P-002 reforca "never invent or round").

## Protected Areas

- `skills/caveman/SKILL.md#wenyan-*` — template intocado (nao modificar secao wenyan; apenas adicionar secao caveman-ptbr irmã)
- `~/.claude/.caveman-active` — flag file agora tem schema expandido; qualquer mudanca adicional requer migration plan

## Related Decisions

- ADR-001: dual-language (contexto)
- ADR-002: escopo (justificativa de por que isto e modo adicional)
- ADR-004: i18n mecanico (o modo vive ortogonal ao CAVEMAN_LANG)
