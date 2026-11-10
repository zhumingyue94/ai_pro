"""Parse Lanhu MCP layer-tree text output into design.schema.json-compliant JSON.

Reads the raw MCP response file (which wraps text in JSON), extracts the layer
tree text, parses indentation-based hierarchy + per-line metadata, and emits a
schema-valid design inventory file.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMAGE_ID = "1dd0ae6b-bb3d-439a-bb71-084e29252c71"
DESIGN_NAME = "发货执行-明细"
PROJECT_URL = (
    "https://lanhuapp.com/web/#/item/project/stage"
    "?tid=fa376857-ec69-426d-a28b-c2490b28b31a"
    "&pid=f9b0f9c2-896f-4601-ae62-611f9cd2e567"
)
SOURCE_FILE = f"{PROJECT_URL}&image_id={IMAGE_ID}"

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[3]  # phase-2 root
SCHEMA_PATH = PROJECT_ROOT / "reference" / "design.schema.json"
MCP_OUTPUT = Path(
    r"C:\Users\zhumi\AppData\Local\Temp\trae\toolcall-output"
    r"\d57e7489-91fe-4124-b7da-b993e87847d9.txt"
)
OUTPUT = SCRIPT_DIR / f"{DESIGN_NAME}_design.json"


# ---------------------------------------------------------------------------
# Regex patterns for parsing layer-tree text lines
# ---------------------------------------------------------------------------
# Line format examples:
#   artboard: 历史标签页 (1668x40 @236,76) [fill:rgba(255,255,255,1)] (3 children)
#     symbolInstence:  icon (16x16 @248,88) (2 children)
#       textLayer: 次要按钮 (28x20 @292,86) "首页" [fill:rgba(50,52,63,1)]
#       shapeLayer: 路径 (Stroke) (8x14 @249,89) [fill:rgba(197,200,206,1)]

# Capture: indent, type, name, optional (Stroke), size, coords, text, fill, children
# Text order in source: coords → "text"? → [fill]? → (children)?
LINE_RE = re.compile(
    r'^(?P<indent>\s*)'
    r'(?P<type>\w+):\s+'
    r'(?P<name>.+?)'
    r'(?:\s+\(Stroke\))?'
    r'\s+\((?P<w>[\d.]+)x(?P<h>[\d.]+)\s*@(?P<x>[\d.]+),(?P<y>[\d.]+)\)'
    r'(?:\s+"(?P<text>[^"]*)")?'
    r'(?:\s+\[fill:(?P<fill>[^\]]+)\])?'
    r'(?:\s+\((?P<children>\d+)\s+children\))?'
    r'\s*$'
)

# Artboard header line: "Artboard: 发货执行-明细 (1920x2084)"
ARTBOARD_RE = re.compile(
    r'^Artboard:\s+(?P<name>.+?)\s+\((?P<w>[\d.]+)x(?P<h>[\d.]+)\)\s*$'
)

# Layout summary lines: "[artboard] 表单区 left:118px top:66px width:834px height:984px"
LAYOUT_RE = re.compile(
    r'^\[artboard\]\s+(?P<name>.+?)\s+'
    r'left:(?P<x>[\d.]+)px\s+'
    r'top:(?P<y>[\d.]+)px\s+'
    r'width:(?P<w>[\d.]+)px\s+'
    r'height:(?P<h>[\d.]+)px'
)


def round1(val: Any) -> float | None:
    """Round to 1 decimal place, return None if not a number."""
    if val is None:
        return None
    try:
        return round(float(val), 1)
    except (TypeError, ValueError):
        return None


def classify(node_type: str, name: str, text: str | None, has_children: bool) -> str:
    """Classify a node into one of: text, image, icon, shape, container, unknown."""
    nt = (node_type or "").lower()
    nm = (name or "").lower()
    if nt == "textlayer" or text is not None:
        return "text"
    if nt == "bitmap" or "image" in nt:
        return "image"
    # Type-based classification takes priority over name-based
    if nt == "shapelayer":
        return "shape"
    icon_words = ("icon", "logo", "arrow", "close", "search", "refresh", "menu",
                  "图标", "chevron", "plus", "minus", "edit", "delete",
                  "filter", "sort", "more", "setting", "star", "check", "warning",
                  "calendar", "clock", "eye", "lock", "user", "bell")
    if nt == "symbolinstence" and "icon" in nm:
        return "icon"
    if any(w in nm for w in icon_words):
        return "icon"
    if nt in ("artboard", "group", "grouplayer", "slice", "symbolinstence") or has_children:
        return "container"
    return "unknown"


def parse_layer_line(line: str) -> dict[str, Any] | None:
    """Parse a single layer-tree line into a dict of extracted fields."""
    m = LINE_RE.match(line)
    if not m:
        return None
    indent = len(m.group("indent"))
    depth = indent // 2 + 1  # 0 indent = depth 1
    node_type = m.group("type")
    name = m.group("name").strip()
    children_count = int(m.group("children")) if m.group("children") else 0
    text = m.group("text") if m.group("text") is not None else None
    fill = m.group("fill")

    rect = {
        "x": round1(m.group("x")),
        "y": round1(m.group("y")),
        "width": round1(m.group("w")),
        "height": round1(m.group("h")),
    }

    style: dict[str, Any] = {}
    if fill:
        style["fill"] = fill

    classification = classify(node_type, name, text, children_count > 0)

    return {
        "depth": depth,
        "indent": indent,
        "original_type": node_type,
        "name": name,
        "rect": rect,
        "style": style if style else None,
        "fill": fill,
        "children_count": children_count,
        "text": text,
        "classification": classification,
    }


def build_tree(parsed_lines: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str], int]:
    """Build a flat node list with parent-child relationships from parsed lines.

    Uses indentation to determine hierarchy. Returns (nodes, root_ids, max_depth).
    """
    nodes: list[dict[str, Any]] = []
    roots: list[str] = []
    # Stack of (indent, element_id) for ancestor tracking
    stack: list[tuple[int, str]] = []
    counter = 0

    for parsed in parsed_lines:
        counter += 1
        element_id = f"lanhu-{IMAGE_ID}-node-{counter}"
        indent = parsed["indent"]

        # Pop stack until we find a parent with smaller indent
        while stack and stack[-1][0] >= indent:
            stack.pop()

        parent_id = stack[-1][1] if stack else None
        if parent_id is None:
            roots.append(element_id)

        path_parts = [str(s[1].split("-")[-1]) for s in stack]
        path_parts.append(str(counter))
        path = ".".join(path_parts)

        node = {
            "element_id": element_id,
            "kind": parsed["classification"],
            "name": parsed["name"],
            "original_type": parsed["original_type"],
            "classification": parsed["classification"],
            "tag": None,
            "role": None,
            "text": parsed["text"],
            "rect": parsed["rect"],
            "rect_source": "node.rect",
            "style": parsed["style"],
            "class": None,
            "image_ref": None,
            "parent_element_id": parent_id,
            "child_element_ids": [],
            "depth": parsed["depth"],
            "path": path,
            "raw_node": {
                "layer_type": parsed["original_type"],
                "name": parsed["name"],
                "rect": parsed["rect"],
                "fill": parsed["fill"],
                "children_count": parsed["children_count"],
            },
        }
        nodes.append(node)

        if parent_id is not None:
            for n in nodes:
                if n["element_id"] == parent_id:
                    n["child_element_ids"].append(element_id)
                    break

        stack.append((indent, element_id))

    max_depth = max((n["depth"] for n in nodes), default=0)
    return nodes, roots, max_depth


def extract_mcp_text(raw: str) -> str:
    """Extract the text content from the MCP JSON response wrapper.

    The file may start with 'The MCP server responded with: ' prefix,
    followed by a JSON array [{"type":"text","text":"..."}].
    """
    raw = raw.strip()

    # Strip the MCP response prefix if present
    prefix = "The MCP server responded with: "
    if raw.startswith(prefix):
        raw = raw[len(prefix):].strip()

    # Try JSON parsing first
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("type") == "text":
                    return item.get("text", "")
        if isinstance(data, dict) and data.get("type") == "text":
            return data.get("text", "")
    except json.JSONDecodeError:
        pass

    # Fallback: manually extract text between JSON string delimiters
    json_prefix = '[{"type":"text","text":"'
    json_suffix = '"}]'
    if json_prefix in raw:
        start = raw.index(json_prefix) + len(json_prefix)
        end = raw.rindex(json_suffix)
        inner = raw[start:end]
        # Unescape JSON string escapes
        inner = inner.replace("\\n", "\n")
        inner = inner.replace('\\"', '"')
        inner = inner.replace("\\\\", "\\")
        inner = inner.replace("\\t", "\t")
        return inner
    return raw


def parse_mcp_output(raw_text: str) -> tuple[list[dict[str, Any]], list[str], int, dict[str, Any]]:
    """Parse the full MCP text output and return (nodes, roots, max_depth, metadata)."""
    text = extract_mcp_text(raw_text)
    lines = text.split("\n")

    # Extract layout summary
    layout_items: list[dict[str, Any]] = []
    in_layer_section = False
    layer_lines: list[str] = []
    artboard_size: tuple[float, float] | None = None

    for line in lines:
        stripped = line.strip()

        # Track sections
        if "--- Layer Structure ---" in stripped:
            in_layer_section = True
            continue
        if "--- Design Tokens ---" in stripped:
            in_layer_section = False
            continue

        if not in_layer_section:
            # Parse layout summary
            m = LAYOUT_RE.match(stripped)
            if m:
                layout_items.append({
                    "name": m.group("name"),
                    "x": round1(m.group("x")),
                    "y": round1(m.group("y")),
                    "width": round1(m.group("w")),
                    "height": round1(m.group("h")),
                })
            # Parse artboard header
            m2 = ARTBOARD_RE.match(stripped)
            if m2:
                artboard_size = (float(m2.group("w")), float(m2.group("h")))
            continue

        # In layer section - collect layer lines (skip blank and header lines)
        if not stripped:
            continue
        if stripped.startswith("Artboard:"):
            m2 = ARTBOARD_RE.match(stripped)
            if m2:
                artboard_size = (float(m2.group("w")), float(m2.group("h")))
            continue
        if stripped.startswith("Total layers:"):
            continue
        if stripped.startswith("Layout warning:"):
            continue

        layer_lines.append(line)

    # Parse each layer line
    parsed = []
    for ll in layer_lines:
        result = parse_layer_line(ll)
        if result:
            parsed.append(result)

    # Build tree
    nodes, roots, max_depth = build_tree(parsed)

    metadata = {
        "layout_items": layout_items,
        "artboard_size": artboard_size,
        "total_layers": len(parsed),
    }
    return nodes, roots, max_depth, metadata


def validate_schema(data: dict[str, Any], schema_path: Path) -> list[str]:
    """Validate data against JSON schema. Returns list of error messages."""
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema module not available - skipping validation"]

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for error in sorted(validator.iter_errors(data), key=lambda e: e.path):
        path = ".".join(str(p) for p in error.path) or "(root)"
        errors.append(f"{path}: {error.message}")
    return errors


def main() -> None:
    print(f"Reading MCP output from: {MCP_OUTPUT}")
    raw_text = MCP_OUTPUT.read_text(encoding="utf-8")
    print(f"Raw text length: {len(raw_text)} chars")

    nodes, roots, max_depth, metadata = parse_mcp_output(raw_text)
    print(f"Parsed {len(nodes)} nodes, {len(roots)} roots, max depth {max_depth}")
    print(f"Artboard size: {metadata.get('artboard_size')}")
    print(f"Layout items: {len(metadata['layout_items'])}")

    result = {
        "schema_version": "1.0",
        "design_id": IMAGE_ID,
        "design_name": DESIGN_NAME,
        "source": {
            "source_file": SOURCE_FILE,
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
                "page_id": f"lanhu-{IMAGE_ID}",
                "title": DESIGN_NAME,
                "roots": roots,
                "node_count": len(nodes),
                "max_depth": max_depth,
                "nodes": nodes,
            }
        ],
    }

    # Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nGenerated: {OUTPUT}")
    print(f"File size: {OUTPUT.stat().st_size} bytes")

    # Validate
    print(f"\nValidating against: {SCHEMA_PATH}")
    errors = validate_schema(result, SCHEMA_PATH)
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} errors):")
        for e in errors[:20]:
            print(f"  - {e}")
    else:
        print("VALIDATION PASSED")


if __name__ == "__main__":
    main()
