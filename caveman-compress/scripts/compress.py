#!/usr/bin/env python3
"""
Caveman Memory Compression Orchestrator

Usage:
    python scripts/compress.py <filepath>
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List

from .i18n import t

OUTER_FENCE_REGEX = re.compile(
    r"\A\s*(`{3,}|~{3,})[^\n]*\n(.*)\n\1\s*\Z", re.DOTALL
)


def strip_llm_wrapper(text: str) -> str:
    """Strip outer ```markdown ... ``` fence when it wraps the entire output."""
    m = OUTER_FENCE_REGEX.match(text)
    if m:
        return m.group(2)
    return text

from .detect import should_compress
from .validate import validate

MAX_RETRIES = 2


# ---------- Claude Calls ----------


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model=os.environ.get("CAVEMAN_MODEL", "claude-sonnet-4-5"),
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            return strip_llm_wrapper(msg.content[0].text.strip())
        except ImportError:
            pass  # anthropic not installed, fall back to CLI
    # Fallback: use claude CLI (handles desktop auth)
    try:
        result = subprocess.run(
            ["claude", "--print"],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
        )
        return strip_llm_wrapper(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Claude call failed:\n{e.stderr}")


def build_compress_prompt(original: str) -> str:
    return f"""
Compress this markdown into caveman format.

STRICT RULES:
- Do NOT modify anything inside ``` code blocks
- Do NOT modify anything inside inline backticks
- Preserve ALL URLs exactly
- Preserve ALL headings exactly
- Preserve file paths and commands
- Return ONLY the compressed markdown body — do NOT wrap the entire output in a ```markdown fence or any other fence. Inner code blocks from the original stay as-is; do not add a new outer fence around the whole file.

Only compress natural language.

TEXT:
{original}
"""


_PT_BR_WORDS = frozenset([
    'de', 'da', 'do', 'das', 'dos', 'em', 'no', 'na', 'nos', 'nas',
    'com', 'por', 'para', 'pelo', 'pela', 'pelos', 'pelas',
    'que', 'uma', 'um', 'como', 'mais', 'mas', 'também', 'quando',
    'então', 'porque', 'isso', 'este', 'esta', 'esse', 'essa',
])

_PT_BR_ACCENT = re.compile(r'[àáâãäéêëíîïóôõöúûüçñÀÁÂÃÄÉÊËÍÎÏÓÔÕÖÚÛÜÇÑ]')


def _is_ptbr_input(text: str) -> bool:
    """Heuristic: return True if text appears to be Portuguese (BR)."""
    if _PT_BR_ACCENT.search(text):
        return True
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return False
    pt_count = sum(1 for w in words if w in _PT_BR_WORDS)
    return pt_count / len(words) >= 0.08


def build_compress_prompt_ptbr(original: str) -> str:
    return f"""Comprima este markdown para o formato caveman em português.

REGRAS OBRIGATÓRIAS:
- NÃO modificar nada dentro de blocos de código ```
- NÃO modificar nada dentro de backticks inline
- Preservar TODOS os URLs exatamente
- Preservar TODOS os títulos exatamente
- Preservar caminhos de arquivo e comandos
- Retornar APENAS o corpo markdown comprimido — NÃO envolver toda a saída em cerca ```markdown ou qualquer outra cerca. Blocos de código internos do original ficam como estão.

Regras de compressão PT-BR (estilo caveman):
- Verbos no infinitivo quando possível ("fazer" não "fazemos")
- Remover artigos desnecessários (o, a, os, as, um, uma)
- Remover palavras de enchimento (basicamente, realmente, simplesmente, na verdade)
- Remover gentilezas (claro, com certeza, ótimo, perfeito)
- Fragmentos permitidos. Sinônimos curtos.
- Termos técnicos exatos. Blocos de código intactos. Erros citados exatamente.

Apenas comprimir linguagem natural.

TEXTO:
{original}
"""


def build_fix_prompt_ptbr(original: str, compressed: str, errors: List[str]) -> str:
    errors_str = "\n".join(f"- {e}" for e in errors)
    return f"""Você está corrigindo um arquivo markdown comprimido no estilo caveman PT-BR. Erros específicos de validação foram encontrados.

REGRAS CRÍTICAS:
- NÃO recomprimir ou reformular o arquivo
- Apenas corrigir os erros listados — deixar todo o resto exatamente como está
- O ORIGINAL é fornecido apenas como referência (para restaurar conteúdo ausente)
- Preservar o estilo caveman nas seções não tocadas

ERROS A CORRIGIR:
{errors_str}

COMO CORRIGIR:
- URL ausente: encontrar no ORIGINAL, restaurar exatamente onde pertence no COMPRIMIDO
- Incompatibilidade de bloco de código: encontrar o bloco exato no ORIGINAL, restaurar no COMPRIMIDO
- Incompatibilidade de título: restaurar o texto exato do título do ORIGINAL no COMPRIMIDO
- Não tocar em nenhuma seção não mencionada nos erros

ORIGINAL (apenas referência):
{original}

COMPRIMIDO (corrigir este):
{compressed}

Retornar APENAS o arquivo comprimido corrigido. Sem explicação.
"""


def build_fix_prompt(original: str, compressed: str, errors: List[str]) -> str:
    errors_str = "\n".join(f"- {e}" for e in errors)
    return f"""You are fixing a caveman-compressed markdown file. Specific validation errors were found.

CRITICAL RULES:
- DO NOT recompress or rephrase the file
- ONLY fix the listed errors — leave everything else exactly as-is
- The ORIGINAL is provided as reference only (to restore missing content)
- Preserve caveman style in all untouched sections

ERRORS TO FIX:
{errors_str}

HOW TO FIX:
- Missing URL: find it in ORIGINAL, restore it exactly where it belongs in COMPRESSED
- Code block mismatch: find the exact code block in ORIGINAL, restore it in COMPRESSED
- Heading mismatch: restore the exact heading text from ORIGINAL into COMPRESSED
- Do not touch any section not mentioned in the errors

ORIGINAL (reference only):
{original}

COMPRESSED (fix this):
{compressed}

Return ONLY the fixed compressed file. No explanation.
"""


# ---------- Core Logic ----------


def compress_file(filepath: Path) -> bool:
    # Resolve and validate path
    filepath = filepath.resolve()
    MAX_FILE_SIZE = 500_000  # 500KB
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    if filepath.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large to compress safely (max 500KB): {filepath}")

    print(t('cli.compress.processing', file=filepath))

    if not should_compress(filepath):
        print(t('cli.skipping_not_natural'))
        return False

    original_text = filepath.read_text(errors="ignore")
    backup_path = filepath.with_name(filepath.stem + ".original.md")

    # Check if backup already exists to prevent accidental overwriting
    if backup_path.exists():
        print(f"⚠️ Backup file already exists: {backup_path}")
        print("The original backup may contain important content.")
        print("Aborting to prevent data loss. Please remove or rename the backup file if you want to proceed.")
        return False

    # Step 1: Compress — detect input language and use appropriate prompt
    is_ptbr = _is_ptbr_input(original_text)
    print("Compressing with Claude...")
    if is_ptbr:
        compressed = call_claude(build_compress_prompt_ptbr(original_text))
    else:
        compressed = call_claude(build_compress_prompt(original_text))

    # Save original as backup, write compressed to original path
    backup_path.write_text(original_text)
    filepath.write_text(compressed)

    # Step 2: Validate + Retry
    for attempt in range(MAX_RETRIES):
        print("\n" + t('cli.compress.validating', attempt=attempt + 1))

        result = validate(backup_path, filepath)

        if result.is_valid:
            print(t('cli.compress.validation_passed'))
            break

        print("❌ " + t('cli.compress.validation_failed'))
        for err in result.errors:
            print(f"   - {err}")

        if attempt == MAX_RETRIES - 1:
            # Restore original on failure
            filepath.write_text(original_text)
            backup_path.unlink(missing_ok=True)
            print("❌ " + t('cli.compress.failed_after_retries'))
            return False

        print(t('cli.compress.fixing'))
        if is_ptbr:
            compressed = call_claude(
                build_fix_prompt_ptbr(original_text, compressed, result.errors)
            )
        else:
            compressed = call_claude(
                build_fix_prompt(original_text, compressed, result.errors)
            )
        filepath.write_text(compressed)

    return True
