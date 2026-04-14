<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">caveman</h1>

<p align="center">
  <strong>por que usar muita palavra quando pouca resolve</strong>
</p>

<p align="center">
  <a href="https://github.com/KodornaRocks/caveman-ptbr/stargazers"><img src="https://img.shields.io/github/stars/KodornaRocks/caveman-ptbr?style=flat&color=yellow" alt="Estrelas"></a>
  <a href="https://github.com/KodornaRocks/caveman-ptbr/commits/main"><img src="https://img.shields.io/github/last-commit/KodornaRocks/caveman-ptbr?style=flat" alt="Último Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/KodornaRocks/caveman-ptbr?style=flat" alt="Licença"></a>
</p>

---

**Créditos:** Fork nativo PT-BR de [caveman original](https://github.com/JuliusBrussee/caveman) por Julius Brussee — adaptação cultural completa para português, não tradução.

## O que é

Cérebro ainda grande. Palavra pequena. Técnica intacta.

Plugin/skill para agentes de IA que faz resposta em **português de caverna** — corta **~65-75% de tokens output**, mantém 100% precisão técnica. Output PT-BR nativo por padrão. Inclui compressão de memory files, commits terse, e code review de uma linha.

## Motivação

Caveman original é excelente mas output em inglês. Comunidade PT-BR grande merecia experiência caveman nativa — não tradução, adaptação. Português quebrado tipo "de caverna" é **natural** em PT-BR (sinônimo de telegráfico), não forçado como em inglês.

Vem com:
- Português de caverna como output padrão (`/caveman`, `/caveman lite`, `/caveman ultra`)
- caveman-compress: reduz `CLAUDE.md` em ~46% input tokens
- Commits terse, code review uma linha, quick-reference card

## Antes / Depois

<table>
<tr>
<td width="50%">

### 🗣️ Claude Normal (77 tokens)

> "O motivo do seu componente React estar re-renderizando é provavelmente porque você está criando uma nova referência de objeto a cada ciclo de render. Quando você passa um objeto inline como prop, a comparação superficial do React vê isso como um objeto diferente toda vez, o que dispara um re-render. Recomendo usar `useMemo` para memoizar o objeto."

</td>
<td width="50%">

### 🪨 Claude Caveman (21 tokens)

> "Nova ref objeto cada render. Prop objeto inline = nova ref = re-render. Envolver em `useMemo`."

</td>
</tr>
<tr>
<td>

### 🗣️ Claude Normal (59 tokens)

> "Claro! Fico feliz em ajudar com isso. O problema que você está enfrentando provavelmente é causado pelo seu middleware de autenticação não validar corretamente a expiração do token. Deixa eu dar uma olhada e sugerir uma correção."

</td>
<td>

### 🪨 Claude Caveman (18 tokens)

> "Bug middleware auth. Check expiração token usa `<` não `<=`. Corrigir:"

</td>
</tr>
</table>

**Mesma solução. ~70% menos token. Cérebro ainda grande.**

**Escolha seu nível de grunhido:**

<table>
<tr>
<td width="33%">

#### 🪶 Lite (38 tokens)

> "Seu componente re-renderiza porque você cria uma nova referência de objeto a cada render. Props de objeto inline falham na comparação superficial toda vez. Envolver em `useMemo`."

</td>
<td width="33%">

#### 🪨 Full (21 tokens)

> "Nova ref objeto cada render. Prop objeto inline = nova ref = re-render. Envolver em `useMemo`."

</td>
<td width="33%">

#### 🔥 Ultra (12 tokens)

> "Prop obj inline → nova ref → re-render. `useMemo`."

</td>
</tr>
</table>

## Instalação

| Agente | Comando |
|--------|---------|
| **Claude Code** | `claude plugin marketplace add KodornaRocks/caveman-ptbr && claude plugin install caveman@caveman-ptbr` |
| **Cursor / Windsurf / Cline / Copilot** | `npx skills add KodornaRocks/caveman-ptbr -a cursor` (substitua `cursor` pelo seu agente) |
| **Gemini CLI** | `gemini extensions install https://github.com/KodornaRocks/caveman-ptbr` |
| **Codex / Outros 40+ agentes** | `npx skills add KodornaRocks/caveman-ptbr` |

**Standalone (sem plugin system):**

```bash
# macOS / Linux / WSL
bash <(curl -s https://raw.githubusercontent.com/KodornaRocks/caveman-ptbr/main/hooks/install.sh)

# Windows (PowerShell)
irm https://raw.githubusercontent.com/KodornaRocks/caveman-ptbr/main/hooks/install.ps1 | iex
```

Instala uma vez. Auto-ativa cada sessão em Claude Code e Codex. Gemini CLI usa instalação própria (linha acima). Outros agentes: use `/caveman` a cada sessão ou add snippet ao system prompt.

## Uso

### Modos

```
/caveman            → Full (padrão — português de caverna)
/caveman lite       → Sem fluff, grammar intacta, PT-BR formal
/caveman ultra      → Telegráfico máximo
```

**Parar:** "parar caveman" ou "modo normal"

### caveman-compress

Comprime `CLAUDE.md`, `notas.md`, etc. em ~46% sem perder legibilidade:

```bash
/caveman:compress CLAUDE.md
```

Cria `CLAUDE.md` (comprimido) + `CLAUDE.original.md` (backup legível). Economiza input tokens cada sessão.

### Skills extras

| Skill | Ativa com |
|-------|-----------|
| **caveman-commit** | `/caveman-commit` — Commits terse. Conventional Commits. ≤50 char subject. |
| **caveman-review** | `/caveman-review` — Code review uma linha: `L42: bug: user null. Add guard.` |
| **caveman-help** | `/caveman-help` — Quick-reference de todos modos e commands. |

## Benchmarks

> [!NOTE]
> Estes números vêm do [caveman original](https://github.com/JuliusBrussee/caveman) e **não foram re-executados neste fork PT-BR**. Servem como referência do comportamento esperado.
>
> **Rodou em PT-BR?** Abre um PR com os resultados — queremos os números reais. Ver [`evals/`](evals/) e [`benchmarks/`](benchmarks/).

Token counts reais da Claude API:

| Tarefa | Normal | Caveman | Economizado |
|--------|-------:|--------:|------:|
| Explicar re-render bug React | 1180 | 159 | 87% |
| Corrigir token expiry auth middleware | 704 | 121 | 83% |
| Setup PostgreSQL connection pool | 2347 | 380 | 84% |
| Explicar git rebase vs merge | 702 | 292 | 58% |
| Refatorar callback para async/await | 387 | 301 | 22% |
| Arquitetura: microservices vs monolith | 446 | 310 | 30% |
| Review PR para security issues | 678 | 398 | 41% |
| Docker multi-stage build | 1042 | 290 | 72% |
| Debug PostgreSQL race condition | 1200 | 232 | 81% |
| Implementar React error boundary | 3454 | 456 | 87% |
| **Média** | **1214** | **294** | **65%** |

Caveman afeta só output tokens — thinking/reasoning não mexido. Principal ganho: **legibilidade, velocidade, redução custo**. Estudo março 2026 ["Brevity Constraints Reverse Performance Hierarchies"](https://arxiv.org/abs/2604.00025) achou que restringir modelos grandes a respostas breves **melhorou accuracy em 26 pontos percentuais** em certos benchmarks.

## Evals

Diretório `evals/` tem harness que mede real token compression. `evals/prompts/pt-br.txt` tem 10 questões técnicas em PT-BR. Roda com:

```bash
uv run python evals/llm_run.py   # Executa evals (precisa claude CLI)
uv run python evals/measure.py   # Lê resultados (offline, sem API key)
```

Rodou em PT-BR? Abre PR com os snapshots — queremos dados reais.

## Contribuir

Quer melhorar caveman PT-BR? Dois passos:

1. Roda evals ou benchmarks sua máquina (`evals/llm_run.py` ou `benchmarks/run.py`)
2. Abre PR com mudança + snapshots novos

Isso. Pronto. Merecia.

## Licença

MIT — livre como mamute em massa em planície aberta.

---

**Fork PT-BR nativo.** Voz caveman preservada. Output padrão: português de caverna. Comandos em inglês do upstream mantidos para compatibilidade de muscle memory.
