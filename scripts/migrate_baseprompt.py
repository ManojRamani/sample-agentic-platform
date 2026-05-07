"""Swap `from agentic_platform... import BasePrompt` → `LabsBasePrompt as BasePrompt`.

The platform's `BasePrompt` defaults `model_id` to a legacy Claude 3 Haiku ID
that Bedrock now rejects. `labs_common.LabsBasePrompt` is a subclass that pins
`model_id` to the lab-canonical Haiku ID.

This script rewrites every lab notebook's import so existing `class X(BasePrompt)`
subclasses inherit the corrected default without any other code changes.

Run from repo root:  uv run python scripts/migrate_baseprompt.py
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LABS_ROOT = REPO_ROOT / "labs"

OLD = "from agentic_platform.core.models.prompt_models import BasePrompt"
NEW = "from labs_common import LabsBasePrompt as BasePrompt"


def migrate_notebook(path: Path) -> int:
    nb = json.loads(path.read_text(encoding="utf-8"))
    cells_changed = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source")
        text = "".join(source) if isinstance(source, list) else source
        if OLD in text:
            text = text.replace(OLD, NEW)
            cell["source"] = text.splitlines(keepends=True)
            cells_changed += 1
    if cells_changed:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return cells_changed


def main() -> None:
    """Walk labs/ and rewrite BasePrompt imports."""
    total_files = 0
    total_cells = 0
    for nb_path in sorted(LABS_ROOT.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in nb_path.parts:
            continue
        changed = migrate_notebook(nb_path)
        if changed:
            total_files += 1
            total_cells += changed
            print(f"  {nb_path.relative_to(REPO_ROOT)}: {changed} cell(s)")
    print(f"\nRewrote {total_cells} import line(s) across {total_files} notebook(s).")


if __name__ == "__main__":
    main()
