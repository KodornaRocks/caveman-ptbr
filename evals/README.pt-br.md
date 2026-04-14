# Evals PT-BR

Mede compressão token real de skills caveman rodando mesmas prompts em três condições e comparando generated output token counts.

## Três braços

| Braço | System prompt |
|-------|--------------|
| `__baseline__` | nada |
| `__terse__` | `Answer concisely.` |
| `<skill>` | `Answer concisely.\n\n{SKILL.md}` |

Delta honesto qualquer skill é **`<skill>` vs `__terse__`** — quanto skill mesmo add em cima de plain "be terse" instrução.

Comparar skill com baseline sem-system-prompt conflate skill com generic terseness ask.

## Design por quê

- **Real LLM output**, não exemplos hand-written (sem circularidade)
- **Mesmo Claude Code** que skills target — sem API key separada
- **Snapshot committed em git** então CI runs determinístico e free, qualquer mudança números reviewable
- **Control arm** isola skill contribution de generic "be terse" efeito

## Arquivos

- `prompts/en.txt` — lista fixa perguntas dev, uma por linha
- `prompts/pt-br.txt` — perguntas técnicas PT-BR equivalentes (novo)
- `llm_run.py` — roda `claude -p --system-prompt …` per (prompt, arm), captura real LLM output, escreve `snapshots/results.json`
- `measure.py` — lê snapshot, conta tokens com tiktoken `o200k_base`, printa markdown table
- `snapshots/results.json` — committed source of truth, regenerado só quando SKILL.md ou prompts mudam

## Refresh snapshot (requer `claude` CLI logged in)

```bash
uv run python evals/llm_run.py
```

Chama Claude uma vez per prompt × (N skills + 2 control arms). Use small model para manter barato:

```bash
CAVEMAN_EVAL_MODEL=claude-haiku-4-5 uv run python evals/llm_run.py
```

## Lê snapshot (sem LLM, sem API key, roda em CI)

```bash
uv run --with tiktoken python evals/measure.py
```

## Add prompt

Append linha em `prompts/pt-br.txt`, depois refresh snapshot.

## Add skill

Drop `skills/<name>/SKILL.md`, depois refresh snapshot. `llm_run.py` pega todo skill directory auto.

## O Que NÃO mede

- **Fidelity** — resposta comprimida preserva claims técnicos?
- **Latency ou cost** — out of scope
- **Cross-model behavior** — só modelo usado mede
- **Exact Claude tokens** — tiktoken é aproximação só
- **Statistical significance** — single run per (prompt, arm)

---

🇺🇸 [English version](README.md)
