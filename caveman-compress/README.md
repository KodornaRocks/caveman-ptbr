<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="80" />
</p>

<h1 align="center">caveman-compress</h1>

<p align="center">
  <strong>shrink memory file. save token every session.</strong>
</p>

<p align="center">
  🇧🇷 <a href="README.pt-br.md"><strong>Versão em português</strong></a> •
  📖 <a href="../README.md"><strong>README principal</strong></a>
</p>

---

Compresses project memory files into caveman format. Same instructions. ~46% fewer tokens. Every session.

## Usage

```bash
/caveman:compress CLAUDE.md
```

Compressed → `CLAUDE.md`. Original → `CLAUDE.original.md` (always kept).

**Files:** `.md`, `.txt`, `.rst` ✅ | Code/config ❌ | Backups ❌

**Requires:** Python 3.10+

## How It Works

Claude compresses. Validates. Fixes errors if needed. Retries 2x max. Code blocks, URLs, headings, tables never touched.

## Why

`CLAUDE.md` loads every session. 1000-token file = 100,000 tokens overhead over 100 sessions. Caveman cuts ~46%. Same instructions. Same accuracy. Less waste.

---

See [README.pt-br.md](README.pt-br.md) for full PT-BR docs. For complete guide, see [README.md](../README.md) (Portuguese) or [README.en.md](../README.en.md) (English). Part of [caveman](https://github.com/JuliusBrussee/caveman) toolkit.

Security note: [SECURITY.md](./SECURITY.md)
