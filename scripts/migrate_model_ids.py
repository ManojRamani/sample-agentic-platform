"""One-off migration: replace hardcoded Claude model IDs in lab notebooks with
imports from `labs_common`.

Run from repo root:  uv run python scripts/migrate_model_ids.py

After this runs, a drift-check (`scripts/bump_models.py` — future) should find
zero remaining hardcoded legacy IDs in labs/**/*.ipynb code cells.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LABS_ROOT = REPO_ROOT / "labs"

# Ordered by specificity — longer/prefixed patterns first so they match before
# the bare "anthropic.claude-3-sonnet-..." catchall.
REPLACEMENTS: list[tuple[str, str]] = [
    # (literal string to find, constant name to substitute + import)
    ('"bedrock/anthropic.claude-3-haiku-20240307-v1:0"', "HAIKU_LITELLM_ID"),
    ("'bedrock:us.anthropic.claude-3-sonnet-20240229-v1:0'", "SONNET_STRANDS_ID"),
    ("'bedrock:anthropic.claude-3-sonnet-20240229-v1:0'", "SONNET_STRANDS_ID"),
    ("'bedrock:us.anthropic.claude-3-5-haiku-20241022-v1:0'", "HAIKU_STRANDS_ID"),
    ('"us.anthropic.claude-3-5-haiku-20241022-v1:0"', "HAIKU_MODEL_ID"),
    ("'us.anthropic.claude-3-5-haiku-20241022-v1:0'", "HAIKU_MODEL_ID"),
    ('"us.anthropic.claude-3-5-sonnet-20240620-v1:0"', "SONNET_MODEL_ID"),
    ('"us.anthropic.claude-3-sonnet-20240229-v1:0"', "SONNET_MODEL_ID"),
    ("'us.anthropic.claude-3-sonnet-20240229-v1:0'", "SONNET_MODEL_ID"),
    ('"anthropic.claude-3-sonnet-20240229-v1:0"', "SONNET_MODEL_ID"),
    ('"anthropic.claude-3-haiku-20240307-v1:0"', "HAIKU_MODEL_ID"),
]

# Regex matching any still-hardcoded claude ID (for final audit).
LEGACY_ID_REGEX = re.compile(r"anthropic\.claude-[34]-")


def migrate_cell(source_lines: list[str]) -> tuple[list[str], set[str]]:
    """Return (new_source_lines, constants_imported_by_this_cell)."""
    text = "".join(source_lines)
    used: set[str] = set()

    for literal, constant in REPLACEMENTS:
        if literal in text:
            text = text.replace(literal, constant)
            used.add(constant)

    if not used:
        return source_lines, set()

    # Inject the import if not already present.
    existing = set(re.findall(r"^from labs_common import ([^\n]+)$", text, re.MULTILINE))
    already_imported: set[str] = set()
    for line in existing:
        for name in (n.strip() for n in line.split(",")):
            already_imported.add(name)

    to_add = used - already_imported
    if to_add:
        import_line = f"from labs_common import {', '.join(sorted(used | already_imported))}\n"
        if "from labs_common import" in text:
            text = re.sub(
                r"^from labs_common import [^\n]+\n",
                import_line,
                text,
                count=1,
                flags=re.MULTILINE,
            )
        else:
            text = import_line + text

    return text.splitlines(keepends=True), used


def migrate_notebook(path: Path) -> tuple[int, set[str]]:
    """Return (num_cells_changed, all_constants_used_in_file)."""
    nb = json.loads(path.read_text(encoding="utf-8"))
    cells_changed = 0
    all_used: set[str] = set()

    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source")
        if isinstance(source, str):
            source_lines = source.splitlines(keepends=True)
        else:
            source_lines = source

        new_lines, used = migrate_cell(source_lines)
        if used:
            cell["source"] = new_lines
            cells_changed += 1
            all_used |= used

    if cells_changed:
        path.write_text(
            json.dumps(nb, indent=1, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return cells_changed, all_used


def audit_remaining() -> list[tuple[Path, int, str]]:
    """Find any hardcoded legacy IDs still present in code cells."""
    hits: list[tuple[Path, int, str]] = []
    for nb_path in sorted(LABS_ROOT.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in nb_path.parts:
            continue
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        for cell_idx, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            source = cell.get("source")
            text = "".join(source) if isinstance(source, list) else source
            for m in LEGACY_ID_REGEX.finditer(text):
                line_no = text[: m.start()].count("\n") + 1
                snippet = text.splitlines()[line_no - 1].strip()
                hits.append((nb_path, cell_idx, f"L{line_no}: {snippet}"))
                break  # one hit per cell is enough signal
    return hits


def main() -> None:
    """Migrate every lab notebook and print an audit of remaining legacy IDs."""
    total_cells = 0
    total_files = 0
    for nb_path in sorted(LABS_ROOT.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in nb_path.parts:
            continue
        # Skip pilot — already migrated.
        if nb_path.name == "1_setup_and_basics.ipynb":
            continue
        cells_changed, used = migrate_notebook(nb_path)
        if cells_changed:
            total_files += 1
            total_cells += cells_changed
            rel = nb_path.relative_to(REPO_ROOT)
            print(f"  {rel}: {cells_changed} cell(s) — {', '.join(sorted(used))}")

    print(f"\nMigrated {total_cells} cell(s) across {total_files} notebook(s).\n")

    print("Auditing for remaining legacy IDs...")
    remaining = audit_remaining()
    if remaining:
        print(f"  {len(remaining)} cell(s) still contain a legacy ID:")
        for path, cell_idx, snippet in remaining:
            print(f"    {path.relative_to(REPO_ROOT)}  cell[{cell_idx}]  {snippet}")
    else:
        print("  OK: no legacy IDs remain in code cells.")


if __name__ == "__main__":
    main()
