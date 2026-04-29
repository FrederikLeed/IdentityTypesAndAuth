#!/usr/bin/env python3
"""
Build PDFs from the MkDocs source under docs/.

Outputs:
  release/identity-types.pdf            EN — index + full reference
  release/identity-types.da.pdf         DA — same
  release/identity-types-handout.pdf    EN — one-pager (lookup table only)
  release/identity-types-handout.da.pdf DA — one-pager

Usage:
    .venv/bin/python build-pdf.py

Requires: pandoc, weasyprint
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
DOCS = REPO / "docs"
RELEASE = REPO / "release"
RELEASE.mkdir(exist_ok=True)

# Strip <details> blocks (GitHub-only progressive disclosure)
DETAILS_RE = re.compile(r"<details>.*?</details>\s*", re.DOTALL | re.IGNORECASE)


BUILDS = [
    {
        "out": "identity-types.pdf",
        "title": "Identity Types & Authentication",
        "subtitle": "Microsoft Entra ID and Active Directory",
        "language": "en-US",
        "sources": ["index.md", "full-reference.md"],
    },
    {
        "out": "identity-types.da.pdf",
        "title": "Identitetstyper og autentificering",
        "subtitle": "Microsoft Entra ID og Active Directory",
        "language": "da-DK",
        "sources": ["index.da.md", "full-reference.da.md"],
    },
    {
        "out": "identity-types-handout.pdf",
        "title": "Identity Types — Quick Reference",
        "subtitle": "Lookup card",
        "language": "en-US",
        "sources": ["index.md"],
    },
    {
        "out": "identity-types-handout.da.pdf",
        "title": "Identitetstyper — Hurtig reference",
        "subtitle": "Opslagskort",
        "language": "da-DK",
        "sources": ["index.da.md"],
    },
]


def preprocess(text: str) -> str:
    return DETAILS_RE.sub("", text)


def build(spec: dict) -> None:
    out = RELEASE / spec["out"]
    print(f"[BUILD] {spec['out']}")

    front_matter = (
        "---\n"
        f"title: {spec['title']}\n"
        f"subtitle: {spec['subtitle']}\n"
        f"lang: {spec['language']}\n"
        "toc: true\n"
        "toc-depth: 2\n"
        "---\n"
    )

    parts = [front_matter]
    for src in spec["sources"]:
        text = (DOCS / src).read_text(encoding="utf-8")
        parts.append(preprocess(text))

    combined = "\n\n".join(parts)

    tmp = RELEASE / f".{spec['out']}.md"
    tmp.write_text(combined, encoding="utf-8")

    try:
        cmd = [
            PANDOC,
            str(tmp),
            "-o", str(out),
            "--pdf-engine=weasyprint",
            f"--resource-path={DOCS}",
            "--standalone",
            "--css", str(REPO / "build" / "pdf.css"),
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"        {out.stat().st_size:,} bytes")
    except subprocess.CalledProcessError as exc:
        print(f"        FAILED: {exc.stderr}", file=sys.stderr)
        raise
    finally:
        tmp.unlink(missing_ok=True)


def _find_pandoc() -> str:
    p = shutil.which("pandoc")
    if p:
        return p
    try:
        import pypandoc
        return pypandoc.get_pandoc_path()
    except Exception:
        return ""


PANDOC = _find_pandoc()


def main() -> int:
    if not PANDOC:
        print("[ERROR] pandoc not found (pip install pypandoc_binary, or apt-get install pandoc)", file=sys.stderr)
        return 1
    if not shutil.which("weasyprint"):
        print("[ERROR] weasyprint not found (pip install weasyprint)", file=sys.stderr)
        return 1

    for spec in BUILDS:
        build(spec)
    print()
    print(f"[DONE] {len(BUILDS)} PDFs in {RELEASE}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
