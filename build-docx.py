#!/usr/bin/env python3
"""
Build script: convert Markdown files to DOCX using pandoc (via pypandoc).

Usage:
    python build-docx.py

Requirements:
    pip install pypandoc pypandoc_binary
    mmdc on PATH (npm install -g @mermaid-js/mermaid-cli)
        — optional; falls back to a code-block placeholder if unavailable

This script:
  - Converts every .md file in the repo EXCEPT README.md to .docx
  - Outputs to a release/ directory
  - Uses reference.docx as a style template (auto-generates one if missing)
  - Renders mermaid code blocks to PNG via mmdc and embeds them
"""

import os
import re
import sys
import shutil
import hashlib
import tempfile
import subprocess
from pathlib import Path

try:
    import pypandoc
except ImportError:
    print("[INFO] pypandoc not found -- installing pypandoc and pypandoc_binary ...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pypandoc", "pypandoc_binary"],
    )
    import pypandoc

print(f"[INFO] Using pandoc version: {pypandoc.get_pandoc_version()}")

REPO_DIR = Path(__file__).resolve().parent
RELEASE_DIR = REPO_DIR / "release"
BUILD_CACHE = REPO_DIR / ".build-cache"
REFERENCE_DOCX = REPO_DIR / "reference.docx"
PUPPETEER_CONFIG = BUILD_CACHE / "puppeteer-config.json"

SKIP_FILES = {"README.md"}

RELEASE_DIR.mkdir(exist_ok=True)
BUILD_CACHE.mkdir(exist_ok=True)
print(f"[INFO] Output directory: {RELEASE_DIR}")


def generate_reference_docx(path: Path) -> None:
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
# HTML <details> stripping
# ---------------------------------------------------------------------------
# <details> blocks are GitHub-only progressive disclosure (e.g. collapsible
# mermaid source). For DOCX delivery the rendered image is already inline,
# so the duplicate source is just clutter.
_DETAILS_RE = re.compile(r"<details>.*?</details>\s*", re.DOTALL | re.IGNORECASE)


def strip_details(md_text: str) -> str:
    return _DETAILS_RE.sub("", md_text)


# ---------------------------------------------------------------------------
# Mermaid rendering
# ---------------------------------------------------------------------------
_MERMAID_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)

MERMAID_PLACEHOLDER = (
    "\n\n---\n\n"
    "**[Diagram]** *Mermaid diagram — install mermaid-cli (mmdc) to embed "
    "rendered images. Source below.*\n\n"
    "```\n{code}\n```\n\n---\n\n"
)

_MMDC = shutil.which("mmdc")


def _autodetect_chrome() -> str | None:
    """Find a Chrome binary mmdc can use. Prefer env var, else common cache paths."""
    if os.environ.get("PUPPETEER_EXECUTABLE_PATH"):
        return os.environ["PUPPETEER_EXECUTABLE_PATH"]
    candidates = [
        Path.home() / ".cache" / "puppeteer" / "chrome-headless-shell",
        Path.home() / ".cache" / "puppeteer" / "chrome",
    ]
    for root in candidates:
        if not root.exists():
            continue
        for exe_name in ("chrome-headless-shell", "chrome"):
            hits = sorted(root.glob(f"linux-*/*/{exe_name}"))
            if hits:
                return str(hits[-1])
    return None


_CHROME = _autodetect_chrome() if _MMDC else None
if _MMDC:
    print(f"[INFO] Found mmdc at {_MMDC} — mermaid blocks will be rendered to PNG")
    if _CHROME:
        print(f"[INFO] Using Chrome at {_CHROME}")
    if not PUPPETEER_CONFIG.exists():
        PUPPETEER_CONFIG.write_text('{"args": ["--no-sandbox"]}\n', encoding="utf-8")
else:
    print("[WARN] mmdc not found on PATH — mermaid blocks will fall back to placeholder text")


def render_mermaid(code: str) -> Path | None:
    """Render mermaid source to PNG. Returns path on success, None on failure."""
    if not _MMDC:
        return None
    digest = hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]
    src = BUILD_CACHE / f"mermaid-{digest}.mmd"
    png = BUILD_CACHE / f"mermaid-{digest}.png"
    if png.exists():
        return png
    src.write_text(code, encoding="utf-8")
    cmd = [
        _MMDC,
        "-p", str(PUPPETEER_CONFIG),
        "-i", str(src),
        "-o", str(png),
        "-w", "1600",
        "--scale", "2",
        "-b", "white",
    ]
    env = os.environ.copy()
    if _CHROME:
        env["PUPPETEER_EXECUTABLE_PATH"] = _CHROME
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
        return png
    except subprocess.CalledProcessError as exc:
        print(f"[WARN] mmdc render failed: {exc.stderr.strip()[:200]}")
        return None


def preprocess_mermaid(md_text: str) -> str:
    """Replace ```mermaid blocks with rendered image, or placeholder on failure."""
    def _replace(m: re.Match) -> str:
        code = m.group(1).strip()
        png = render_mermaid(code)
        if png is None:
            return MERMAID_PLACEHOLDER.format(code=code)
        return f"\n\n![Diagram]({png})\n\n"
    return _MERMAID_RE.sub(_replace, md_text)


# ---------------------------------------------------------------------------
# Convert each Markdown file
# ---------------------------------------------------------------------------
md_files = sorted(p for p in REPO_DIR.glob("*.md") if p.name not in SKIP_FILES)

if not md_files:
    print("[WARN] No Markdown files found to convert.")
    sys.exit(0)

errors: list[str] = []

for md_path in md_files:
    docx_name = md_path.stem + ".docx"
    docx_path = RELEASE_DIR / docx_name
    print(f"[CONVERT] {md_path.name}  ->  release/{docx_name}")

    try:
        md_text = md_path.read_text(encoding="utf-8")
        md_text = strip_details(md_text)
        md_text = preprocess_mermaid(md_text)

        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".md", dir=REPO_DIR)
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(md_text)

            extra_args = [
                f"--reference-doc={REFERENCE_DOCX}",
                "--wrap=none",
                f"--resource-path={REPO_DIR}",
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

print()
print(f"[DONE] Converted {len(md_files) - len(errors)}/{len(md_files)} files.")
if errors:
    print("[ERRORS]")
    for e in errors:
        print(e)
    sys.exit(1)
