"""Batch parser: Split combined MCP output by design, parse each, output JSON files.

Usage:
    python batch_parse.py <mcp_output_path> <designs_json_path>

designs_json_path: JSON file with list of {image_id, name} objects.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import from the single-design parser
from parse_lanhu_design import (
    PROJECT_URL,
    SCRIPT_DIR,
    SCHEMA_PATH,
    build_tree,
    extract_mcp_text,
    parse_mcp_output,
    validate_schema,
)
from collections import Counter

DESIGN_HEADER_RE = re.compile(r'^---\s+(.+?)\s+---$')

SKIP_SECTIONS = {
    "Layer Structure", "Design Tokens", "Layout Summary (sketch)",
    "Layout Summary (dds)", "CSS annotations", "Component annotations",
    "Layout warnings", "Sketch Annotations",
}


def split_by_design(text: str, design_names: list[str]) -> list[tuple[str, str]]:
    """Split the combined MCP text by design sections.
    
    Returns list of (design_name, section_text) tuples.
    Only returns designs whose names are in design_names list.
    """
    lines = text.split("\n")
    sections: list[tuple[str, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        m = DESIGN_HEADER_RE.match(stripped)
        if m:
            name = m.group(1)
            if name in SKIP_SECTIONS:
                # This is a sub-section header within a design, not a new design
                if current_name is not None:
                    current_lines.append(line)
                continue
            
            # Save previous section
            if current_name is not None:
                sections.append((current_name, current_lines))
            
            current_name = name
            current_lines = [line]
        else:
            if current_name is not None:
                current_lines.append(line)

    # Save last section
    if current_name is not None:
        sections.append((current_name, current_lines))

    # Filter to only requested designs
    result = []
    for name, lines_list in sections:
        if name in design_names:
            result.append((name, "\n".join(lines_list)))

    return result


def wrap_as_mcp_response(section_text: str) -> str:
    """Wrap a design section text as a fake MCP JSON response."""
    escaped = section_text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'[{{"type":"text","text":"{escaped}"}}]'


def process_design(
    design_name: str,
    image_id: str,
    section_text: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Process a single design section and return (result_dict, errors)."""
    # Wrap as MCP response and parse
    fake_mcp = wrap_as_mcp_response(section_text)
    
    try:
        parsed, layer_lines, artboard_size, layout_items = parse_mcp_output(fake_mcp)
    except Exception as e:
        return None, [f"Parse error: {e}"]

    if not parsed:
        return None, ["No layer lines parsed"]

    # Build tree
    nodes, roots, max_depth = build_tree(parsed, image_id)

    source_file = f"{PROJECT_URL}&image_id={image_id}"
    result = {
        "schema_version": "1.0",
        "design_id": image_id,
        "design_name": design_name,
        "source": {
            "source_file": source_file,
            "source_format": "Lanhu MCP layer tree (Sketch fallback; DDS Schema unavailable)",
            "slice_scale": None,
            "is_figma": True,
            "coordinate_policy": (
                "坐标取自 MCP 层级树文本标注 (width x height @x,y)；"
                "父子层级通过缩进推断；fill 来自 [fill:rgba(...)] 标注。"
            ),
        },
        "capture": {
            "collector": "lanhu mcp layer tree parser",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source_node_count": len(nodes),
        },
        "pages": [
            {
                "page_id": f"lanhu-{image_id}",
                "title": design_name,
                "roots": roots,
                "node_count": len(nodes),
                "max_depth": max_depth,
                "nodes": nodes,
            }
        ],
    }
    return result, []


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python batch_parse.py <mcp_output_path> <designs_json_path>")
        return 1

    mcp_output_path = Path(sys.argv[1])
    designs_json_path = Path(sys.argv[2])

    # Read designs list
    designs = json.loads(designs_json_path.read_text(encoding="utf-8"))
    print(f"Designs to process: {len(designs)}")

    # Read MCP output
    raw_text = mcp_output_path.read_text(encoding="utf-8")
    text = extract_mcp_text(raw_text)
    print(f"MCP text length: {len(text)} chars")

    # Split by design
    design_names = [d["name"] for d in designs]
    # Also need to handle duplicates - use index-based matching
    sections = split_by_design(text, design_names)
    print(f"Found {len(sections)} design sections")

    # Match sections to designs (handling duplicates)
    # For duplicate names, match in order
    name_to_designs: dict[str, list[dict]] = {}
    for d in designs:
        name_to_designs.setdefault(d["name"], []).append(d)

    name_to_sections: dict[str, list[str]] = {}
    for name, section_text in sections:
        name_to_sections.setdefault(name, []).append(section_text)

    # Detect duplicate design names for file naming
    name_counts = Counter(d["name"] for d in designs)
    dup_names = {n for n, c in name_counts.items() if c > 1}

    # Process each design
    success_count = 0
    fail_count = 0

    for design in designs:
        name = design["name"]
        image_id = design["image_id"]

        # Get the next section for this name (handles duplicates)
        section_list = name_to_sections.get(name, [])
        if not section_list:
            print(f"\n[SKIP] {name} ({image_id}) - no section found")
            fail_count += 1
            continue

        section_text = section_list.pop(0)  # Take first remaining section

        result, errors = process_design(name, image_id, section_text)
        if result is None:
            print(f"\n[FAIL] {name} ({image_id}): {errors}")
            fail_count += 1
            continue

        # Write output (append image_id suffix for duplicate names)
        if name in dup_names:
            short_id = image_id[:8]
            output_path = SCRIPT_DIR / f"{name}_{short_id}_design.json"
        else:
            output_path = SCRIPT_DIR / f"{name}_design.json"
        output_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        # Validate
        validation_errors = validate_schema(result, SCHEMA_PATH)
        if validation_errors:
            print(f"\n[VALIDATION FAIL] {name} ({image_id}): {len(validation_errors)} errors")
            for e in validation_errors[:5]:
                print(f"  - {e}")
            fail_count += 1
            continue

        # Stats
        nodes = result["pages"][0]["nodes"]
        c = Counter(n["classification"] for n in nodes)
        print(f"\n[OK] {name} ({image_id})")
        print(f"  Nodes: {len(nodes)}, Roots: {len(result['pages'][0]['roots'])}, "
              f"Max depth: {result['pages'][0]['max_depth']}")
        print(f"  Classification: {dict(c)}")
        print(f"  File: {output_path.name} ({output_path.stat().st_size} bytes)")
        success_count += 1

    print(f"\n=== Summary ===")
    print(f"Success: {success_count}/{len(designs)}")
    print(f"Failed: {fail_count}/{len(designs)}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
