# Contribuindo

🇺🇸 [English version](CONTRIBUTING.md) · 📖 [README EN](README.en.md)

Melhorias em SKILL.md, prompt caveman, modo PT-BR, evals, docs — bem-vindo. Abre PR com antes/depois exemplos mostrando mudança.

## Como

1. Fork repo
2. Edita arquivo certo (ver abaixo)
3. Abre PR com:
   - **Antes:** o que era antes
   - **Depois:** o que mudou
   - Uma frase por quê melhor

## Arquivo por tipo mudança

| Tipo | Edita |
|------|-------|
| Comportamento caveman EN | `skills/caveman/SKILL.md` |
| Comportamento caveman PT-BR | `skills/caveman/SKILL.pt-br.md` |
| Modo compressão | `caveman-compress/SKILL.md` |
| Auto-activation rules | `rules/caveman-activate.md` |
| Interface mensagens | `locales/en.json`, `locales/pt-br.json` |
| Docs README | `README.pt-br.md`, `README.md` (reduzido) |
| Docs sub-pastas | `{pasta}/README.pt-br.md`, `{pasta}/README.md` |
| Evals prompts PT-BR | `evals/prompts/pt-br.txt` |

> **Nota:** Arquivos auto-sincronizados por CI após merge:
> - `caveman/SKILL.md` ← `skills/caveman/SKILL.md`
> - `plugins/caveman/skills/caveman/SKILL.md` ← `skills/caveman/SKILL.md`
> - `.cursor/skills/caveman/SKILL.md` ← `skills/caveman/SKILL.md`
> - `caveman.skill` ← `skills/caveman/`
> - Não edita direto — CI sobrescreve.

Mudança simples focused > rewrite grande. Caveman gusta simples.

## Ideias

Ver [issues labeled `good first issue`](../../issues?q=label%3A%22good+first+issue%22) para starter tasks.

## Polyglot Skills

Se edita modo PT-BR (`SKILL.pt-br.md`), lembrar:
- Voz caveman preservada em português (não tradução EN)
- Exemplos PT-BR, não tradução literal
- Referencia output EN caveman como canonical (feature original)
- Modo PT-BR = nova variante, não substitui EN

## Testing PT-BR

Se mexe em `locales/pt-br.json` ou modo PT-BR:

```bash
# Verify locale paridade (chaves + placeholders)
python tests/verify_locales.py

# Testar compress PT-BR (se implementado)
uv run python caveman-compress/scripts/compress.py <arquivo_pt-br.md>
```

## Evals PT-BR

Se ad prompt em `evals/prompts/pt-br.txt`:

```bash
# Roda eval com PT-BR prompts
CAVEMAN_EVAL_MODEL=claude-haiku-4-5 uv run python evals/llm_run.py

# Lê resultados
uv run --with tiktoken python evals/measure.py
```

---

Agradeço contribuições. Caveman bom porque comunidade.
