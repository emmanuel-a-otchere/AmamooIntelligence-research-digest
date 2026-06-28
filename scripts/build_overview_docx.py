#!/usr/bin/env python3
"""Generate the DOCX version of OVERVIEW.md for the research-digest specialization.

Adapts the same approach as scripts/build_requirements_docx.py but pointed at
the specialization's docs/OVERVIEW.md.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Reuse the requirements docx builder machinery
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_requirements_docx import (  # type: ignore
    convert, setup_document,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC = REPO_ROOT / "specializations" / "research-digest" / "docs" / "OVERVIEW.md"
DST = REPO_ROOT / "specializations" / "research-digest" / "docs" / "OVERVIEW.docx"


def main() -> int:
    if not SRC.exists():
        print(f"ERROR: source not found: {SRC}", file=sys.stderr)
        return 1
    from docx import Document
    doc = Document()
    setup_document(doc)
    convert(SRC.read_text(encoding="utf-8"), doc)
    DST.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(DST))
    print(f"Wrote {DST} ({DST.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())