#!/usr/bin/env python3
"""
Build script: convert Markdown files to DOCX using pandoc (via pypandoc).

Usage:
    python build-docx.py

Requirements:
    pip install pypandoc pypandoc_binary

This script:
  - Converts every .md file in the repo EXCEPT README.md to .docx
  - Outputs to a release/ directory
  - Uses reference.docx as a style template (auto-generates one if missing)
  - Replaces mermaid code blocks with a placeholder note
"""

import os
import re
import sys
import shutil
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# 1. Ensure pypandoc (and bundled pandoc) is available
# ---------------------------------------------------------------------------
try:
    import pypandoc
except ImportError:
    print("[INFO] pypandoc not found -- installing pypandoc and pypandoc_binary ...")
    import subprocess
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pypandoc", "pypandoc_binary"],
    )
    import pypandoc

print(f"[INFO] Using pandoc version: {pypandoc.get_pandoc_version()}")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_DIR = Path(__file__).resolve().parent
RELEASE_DIR = REPO_DIR / "release"
REFERENCE_DOCX = REPO_DIR / "reference.docx"

# Files to skip
SKIP_FILES = {"README.md"}

# ---------------------------------------------------------------------------
# 2. Ensure the release/ directory exists
# ---------------------------------------------------------------------------
RELEASE_DIR.mkdir(exist_ok=True)
print(f"[INFO] Output directory: {RELEASE_DIR}")

# ---------------------------------------------------------------------------
# 3. Ensure a reference.docx template exists
# ---------------------------------------------------------------------------
def generate_reference_docx(path: Path) -> None:
    """Generate a default reference.docx from pandoc so users can customise it."""
    print("[INFO] Generating default reference.docx template ...")
    pypandoc.convert_text(
        "# Reference template\n\nCustomise this file to change output styling.",
        "docx",
        format="md",
        outputfile=str(path),
    )
    print(f"[INFO] Created {path}")


if not REFERENCE_DOCX.exists():
    generate_reference_docx(REFERENCE_DOCX)
else:
    print(f"[INFO] Using existing reference template: {REFERENCE_DOCX}")

# ---------------------------------------------------------------------------
# 4. Pre-process Markdown: handle mermaid blocks
# ---------------------------------------------------------------------------
_MERMAID_RE = re.compile(
    r"```mermaid\s*\n(.*?)```",
    re.DOTALL,
)

MERMAID_PLACEHOLDER = (
    "\n\n---\n\n"
    "**[Diagram]** *This section contains a Mermaid diagram that cannot be "
    "rendered in DOCX format. Please see the original .md file for the "
    "interactive diagram.*\n\n"
    "```\n{code}\n```\n\n---\n\n"
)


def preprocess_mermaid(md_text: str) -> str:
    """Replace ```mermaid blocks with a readable placeholder + raw code."""
    def _replace(m: re.Match) -> str:
        code = m.group(1).strip()
        return MERMAID_PLACEHOLDER.format(code=code)
    return _MERMAID_RE.sub(_replace, md_text)


# ---------------------------------------------------------------------------
# 5. Convert each Markdown file
# ---------------------------------------------------------------------------
md_files = sorted(
    p for p in REPO_DIR.glob("*.md")
    if p.name not in SKIP_FILES
)

if not md_files:
    print("[WARN] No Markdown files found to convert.")
    sys.exit(0)

errors: list[str] = []

for md_path in md_files:
    docx_name = md_path.stem + ".docx"
    docx_path = RELEASE_DIR / docx_name
    print(f"[CONVERT] {md_path.name}  ->  release/{docx_name}")

    try:
        # Read and pre-process
        md_text = md_path.read_text(encoding="utf-8")
        md_text = preprocess_mermaid(md_text)

        # Write processed markdown to a temp file so pandoc can read it
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".md")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(md_text)

            extra_args = [
                f"--reference-doc={REFERENCE_DOCX}",
                "--wrap=none",
            ]
            pypandoc.convert_file(
                tmp_path,
                "docx",
                format="markdown",
                outputfile=str(docx_path),
                extra_args=extra_args,
            )
        finally:
            os.unlink(tmp_path)

        print(f"         OK  ({docx_path.stat().st_size:,} bytes)")

    except Exception as exc:
        msg = f"  ERROR converting {md_path.name}: {exc}"
        print(msg)
        errors.append(msg)

# ---------------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------------
print()
print(f"[DONE] Converted {len(md_files) - len(errors)}/{len(md_files)} files.")
if errors:
    print("[ERRORS]")
    for e in errors:
        print(e)
    sys.exit(1)
