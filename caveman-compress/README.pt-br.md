<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="80" />
</p>

<h1 align="center">caveman-compress</h1>

<p align="center">
  <strong>encolhe file memória. economiza token cada sessão.</strong>
</p>

<p align="center">
  🇺🇸 <a href="README.md"><strong>English version</strong></a>
</p>

---

Skill Claude Code que comprime project memory files (`CLAUDE.md`, todos, preferences) em formato caveman — cada sessão carrega menos tokens auto.

Claude lê `CLAUDE.md` em cada session start. File grande = custo grande. Caveman faz file pequeno. Custo desce para sempre.

## O Que Faz

```
/caveman:compress CLAUDE.md
```

```
CLAUDE.md          ← comprimido (Claude lê isto — menos tokens cada sessão)
CLAUDE.original.md ← backup humanamente legível (você edita isto)
```

Original nunca se perde. Pode ler e editar `.original.md`. Roda skill de novo para re-comprimir após edits.

## Benchmarks

Resultados reais em files projeto reais:

| File | Original | Comprimido | Economizado |
|------|----------:|----------:|------:|
| `claude-md-preferences.md` | 706 | 285 | **59.6%** |
| `project-notes.md` | 1145 | 535 | **53.3%** |
| `claude-md-project.md` | 1122 | 636 | **43.3%** |
| `todo-list.md` | 627 | 388 | **38.1%** |
| `mixed-with-code.md` | 888 | 560 | **36.9%** |
| **Média** | **898** | **481** | **46%** |

Todas validações passaram — headings, code blocks, URLs, file paths preservados exatamente.

## Antes / Depois

<table>
<tr>
<td width="50%">

### 📄 Original (706 tokens)

> "Prefiro fortemente TypeScript com strict mode ligado para todo novo código. Não use tipo `any` a menos que verdadeiramente sem jeito, e se usar, deixe comentário explicando razão. Acho que investir tempo tipando direito pega muitos bugs antes chegarem runtime."

</td>
<td width="50%">

### 🪨 Caveman (285 tokens)

> "Prefira TypeScript strict mode sempre. Sem `any` a menos que inevitável — comente por quê se usar. Tipos corretos pegam bugs cedo."

</td>
</tr>
</table>

**Mesmas instruções. 60% menos tokens. Cada. Sessão. Única.**

## Segurança

`caveman-compress` flagado como Snyk High Risk por subprocess e file I/O patterns detectados por análise estática. False positive — ver [SECURITY.md](./SECURITY.md) explicação completa do que skill faz e não faz.

## Install

Compress built-in com plugin `caveman`. Instala `caveman` uma vez, depois usa `/caveman:compress`.

Se precisa files local, compress skill vive em:

```bash
caveman-compress/
```

**Requer:** Python 3.10+

## Uso

```
/caveman:compress <filepath>
```

Exemplos:
```
/caveman:compress CLAUDE.md
/caveman:compress docs/preferences.md
/caveman:compress todos.md
```

### Quais files funcionam

| Tipo | Comprime? |
|------|-----------|
| `.md`, `.txt`, `.rst` | ✅ Sim |
| Linguagem natural extensionless | ✅ Sim |
| `.py`, `.js`, `.ts`, `.json`, `.yaml` | ❌ Pula (código/config) |
| `*.original.md` | ❌ Pula (backup files) |

## Como Funciona

```
/caveman:compress CLAUDE.md
        ↓
detecta tipo file           (sem tokens)
        ↓
Claude comprime             (tokens — um call)
        ↓
valida output               (sem tokens)
  checks: headings, code blocks, URLs, file paths, bullets
        ↓
se erros: Claude corrige cherry-picked issues só   (tokens — fix targeted)
  NÃO re-comprime — só patches partes quebradas
        ↓
retry até 2 vezes
        ↓
escreve comprimido → CLAUDE.md
escreve original   → CLAUDE.original.md
```

Só duas coisas usam tokens: compressão inicial + fix targeted se validation falha. Tudo mais é Python local.

## O Que Se Preserva

Caveman comprime linguagem natural. Nunca toca:

- Code blocks (` ``` ` fenced ou indented)
- Inline code (`` `backtick content` ``)
- URLs e links
- File paths (`/src/components/...`)
- Comandos (`npm install`, `git commit`)
- Termos técnicos, library names, API names
- Headings (texto exato preservado)
- Tables (estrutura preservada, texto célula comprimido)
- Dates, version numbers, valores numéricos

## Por Que Importa

`CLAUDE.md` carrega em **cada session start**. File memória projeto de 1000-tokens custa tokens toda vez que abre projeto. Sobre 100 sessões isso 100,000 tokens overhead — só por context que já escreveu.

Caveman corta isso ~46% na média. Mesmas instruções. Mesma accuracy. Menos desperdício.

```
┌────────────────────────────────────────────┐
│  ECONOMIAS TOKEN POR FILE      █████   46% │
│  SESSÕES QUE BENEFICIAM        ██████  100% │
│  INFORMAÇÃO PRESERVADA         ██████  100% │
│  TEMPO SETUP                   █        1x │
└────────────────────────────────────────────┘
```

## Parte de Caveman

Skill é parte do toolkit [caveman](https://github.com/JuliusBrussee/caveman) — fazendo Claude usar menos tokens sem perder accuracy.

- **caveman** — faz Claude *falar* como caveman (corta response tokens ~65%)
- **caveman-compress** — faz Claude *ler* menos (corta context tokens ~46%)
