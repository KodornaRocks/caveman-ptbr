<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">caveman</h1>

<p align="center">
  <strong>why use many token when few do trick</strong>
</p>

<p align="center">
  <a href="https://github.com/KodornaRocks/caveman-ptbr/stargazers"><img src="https://img.shields.io/github/stars/KodornaRocks/caveman-ptbr?style=flat&color=yellow" alt="Stars"></a>
  <a href="https://github.com/KodornaRocks/caveman-ptbr/commits/main"><img src="https://img.shields.io/github/last-commit/KodornaRocks/caveman-ptbr?style=flat" alt="Last Commit"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/KodornaRocks/caveman-ptbr?style=flat" alt="License"></a>
</p>

<p align="center">
  🇧🇷 <a href="README.md"><strong>Versão em português (completa)</strong></a>
</p>

<p align="center">
  <a href="#before--after">Before/After</a> •
  <a href="#install">Install</a> •
  <a href="#intensity-levels">Levels</a> •
  <a href="#caveman-skills">Skills</a> •
  <a href="#benchmarks">Benchmarks</a> •
  <a href="#evals">Evals</a>
</p>

---

Brain still big. Token small. Caveman mode cuts **~75% output tokens** keeping full technical accuracy. Works: Claude Code, Codex, Gemini, Cursor, Windsurf, Cline, Copilot, 40+ agents. This fork outputs PT-BR by default — all modes speak Portuguese caveman.

## Before / After

<table>
<tr>
<td width="50%">

### 🗣️ Normal Claude (69 tokens)

> "The reason your React component is re-rendering is likely because you're creating a new object reference on each render cycle. When you pass an inline object as a prop, React's shallow comparison sees it as a different object every time, which triggers a re-render. I'd recommend using useMemo to memoize the object."

</td>
<td width="50%">

### 🪨 Caveman Claude (19 tokens)

> "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

</td>
</tr>
<tr>
<td>

### 🗣️ Normal Claude

> "Sure! I'd be happy to help you with that. The issue you're experiencing is most likely caused by your authentication middleware not properly validating the token expiry. Let me take a look and suggest a fix."

</td>
<td>

### 🪨 Caveman Claude

> "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

</td>
</tr>
</table>

**Same fix. 75% less word. Brain still big.**

**Intensity levels:** Lite (professional, no fluff) → Full (caveman) → Ultra (telegraphic). Pick yours. Stick until you change it.

```
┌──────────────────────────┐
│  TOKENS SAVED    ████ 75% │
│  ACCURACY        ████ 100%│
│  SPEED           ████ ~3x │
│  VIBES           ████ OOG │
└──────────────────────────┘
```

## Install

Pick your agent. One command. Done.

| Agent | Install |
|-------|---------|
| **Claude Code** | `claude plugin marketplace add KodornaRocks/caveman-ptbr && claude plugin install caveman@caveman-ptbr` |
| **Codex** | Clone repo → `/plugins` → Search "Caveman" → Install |
| **Gemini CLI** | `gemini extensions install https://github.com/KodornaRocks/caveman-ptbr` |
| **Cursor** | `npx skills add KodornaRocks/caveman-ptbr -a cursor` |
| **Windsurf** | `npx skills add KodornaRocks/caveman-ptbr -a windsurf` |
| **Copilot** | `npx skills add KodornaRocks/caveman-ptbr -a github-copilot` |
| **Cline** | `npx skills add KodornaRocks/caveman-ptbr -a cline` |
| **Any other** | `npx skills add KodornaRocks/caveman-ptbr` |

Install once. One rock. That it.

See [README.md](README.md) for full install details per agent.

## Usage

Trigger: `/caveman` · Stop: "stop caveman" or "normal mode"

**Modes:** `/caveman lite|full|ultra`

- **Lite** — professional, no fluff (PT-BR)
- **Full** — caveman default (PT-BR)
- **Ultra** — telegraphic max compression (PT-BR)

**Skills:**
- `/caveman-commit` — terse commits (Conventional, ≤50 chars)
- `/caveman-review` — one-line PR comments
- `/caveman:compress FILE` — compress input tokens in memory files

## Benchmarks

Real token counts from Claude API. Caveman cuts ~65% output tokens on average (range 22–87%). See [benchmarks/](benchmarks/) to reproduce.

> [!NOTE]
> Caveman affects **output tokens only**. Thinking/reasoning untouched. Biggest win: readability + speed. Cost savings = bonus.

Research: [Brevity Constraints Reverse Performance Hierarchies in Language Models](https://arxiv.org/abs/2604.00025) (March 2026) found constraining models to brief responses **improved accuracy 26 percentage points** on some benchmarks. Less word = more correct.

## Evals

Three-arm harness in `evals/`. Measures real token compression (not "verbose vs skill" but "terse vs skill"). See [evals/](evals/) for PT-BR eval results.

## Links

- **PT-BR version:** [README.md](README.md) — full docs in Portuguese
- **Upstream:** [github.com/JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) (original)
- **This fork:** [github.com/KodornaRocks/caveman-ptbr](https://github.com/KodornaRocks/caveman-ptbr)
- **License:** MIT

---

**This is a PT-BR fork.** English version simplified. Full docs at [README.md](README.md).
