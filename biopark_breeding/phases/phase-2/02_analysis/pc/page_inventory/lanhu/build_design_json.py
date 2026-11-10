from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

IMAGE_ID = "266dfcdc-e7f4-4eed-b4dc-71cf052515d9"
DESIGN_NAME = "首页"
# 本脚本位于 二期/02_analysis/pc/page_inventory/lanhu/，上溯 4 层到二期根
ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "page" / "lanhu-mcp-assets" / "designs" / f"{IMAGE_ID}.json"
OUTPUT = Path(__file__).resolve().parent / f"{DESIGN_NAME}_design.json"


def parse_class_size(value: Any) -> dict[str, float]:
    if not isinstance(value, str):
        return {}
    result: dict[str, float] = {}
    for key, number in re.findall(r"\b([wh])-(\d+(?:\.\d+)?)px\b", value):
        result[{"w": "width", "h": "height"}[key]] = float(number)
    return result


def frame_to_rect(frame: Any) -> dict[str, float] | None:
    if not isinstance(frame, dict):
        return None
    keys = {"left": "x", "top": "y", "width": "width", "height": "height"}
    rect = {target: frame[source] for source, target in keys.items() if isinstance(frame.get(source), (int, float))}
    return rect or None


def extract_rect(node: dict[str, Any]) -> tuple[dict[str, float] | None, str]:
    for key in ("rect", "frame"):
        rect = frame_to_rect(node.get(key))
        if rect:
            return rect, f"node.{key}"
    text = node.get("text")
    if isinstance(text, dict):
        rect = frame_to_rect(text.get("frame"))
        if rect:
            return rect, "node.text.frame"
    size = parse_class_size(node.get("class"))
    if size:
        return size, "node.class"
    return None, "missing_in_source"


def extract_text(node: dict[str, Any]) -> str | None:
    text = node.get("text")
    if not isinstance(text, dict):
        return None
    for value in (text.get("value"), (text.get("style") or {}).get("content")):
        if isinstance(value, str):
            return value
    styles = text.get("styles")
    if isinstance(styles, list):
        for style in styles:
            if isinstance(style, dict) and isinstance(style.get("content"), str):
                return style["content"]
    return None


def classify(node: dict[str, Any], text: str | None) -> str:
    node_type = str(node.get("type", "")).lower()
    name = str(node.get("name", "")).lower()
    if node_type == "text" or isinstance(node.get("text"), dict) or text is not None:
        return "text"
    image_keys = ("imageRef", "image", "src", "url")
    if node_type == "image" or any(node.get(key) for key in image_keys):
        return "image"
    icon_words = ("icon", "logo", "arrow", "close", "search", "refresh", "menu", "路径", "图标")
    if node_type == "icon" or any(word in name for word in icon_words):
        return "icon"
    if node_type == "shape":
        return "shape"
    if node_type == "container" or isinstance(node.get("children"), list):
        return "container"
    return "unknown"


def build(source: dict[str, Any]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    roots: list[str] = []

    def visit(node: dict[str, Any], path: str, parent_id: str | None, depth: int) -> str:
        element_id = f"lanhu-{IMAGE_ID}-node-{path.replace('.', '-') }"
        children = node.get("children") if isinstance(node.get("children"), list) else []
        text = extract_text(node)
        rect, rect_source = extract_rect(node)
        record = {
            "element_id": element_id,
            "kind": classify(node, text),
            "name": node.get("name"),
            "original_type": node.get("type"),
            "classification": classify(node, text),
            "tag": None,
            "role": None,
            "text": text,
            "rect": rect,
            "rect_source": rect_source,
            "style": node.get("text", {}).get("style") if isinstance(node.get("text"), dict) else None,
            "class": node.get("class"),
            "image_ref": node.get("imageRef"),
            "parent_element_id": parent_id,
            "child_element_ids": [],
            "depth": depth,
            "path": path,
            "raw_node": node,
        }
        nodes.append(record)
        if parent_id is None:
            roots.append(element_id)
        for index, child in enumerate(children):
            if isinstance(child, dict):
                child_id = visit(child, f"{path}.{index}", element_id, depth + 1)
                record["child_element_ids"].append(child_id)
        return element_id

    for index, node in enumerate(source.get("nodes", [])):
        if isinstance(node, dict):
            visit(node, str(index), None, 1)

    ids = {node["element_id"] for node in nodes}
    for node in nodes:
        assert node["parent_element_id"] is None or node["parent_element_id"] in ids
        assert all(child_id in ids for child_id in node["child_element_ids"])

    return {
        "schema_version": "1.0",
        "design_id": IMAGE_ID,
        "design_name": DESIGN_NAME,
        "source": {
            "source_file": str(SOURCE.relative_to(ROOT)).replace("\\", "/"),
            "source_format": "Lanhu/Figma node tree",
            "slice_scale": source.get("sliceScale"),
            "is_figma": source.get("isFigma"),
            "coordinate_policy": "优先使用节点 rect/frame 或 text.frame；否则使用 class 中的宽高；缺失时为 null，不臆造坐标。",
        },
        "capture": {
            "collector": "local lanhu design parser",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source_node_count": len(nodes),
        },
        "pages": [{
            "page_id": f"lanhu-{IMAGE_ID}",
            "title": DESIGN_NAME,
            "roots": roots,
            "node_count": len(nodes),
            "max_depth": max((node["depth"] for node in nodes), default=0),
            "nodes": nodes,
        }],
        "raw_design": source,
    }


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = build(source)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(OUTPUT.read_text(encoding="utf-8"))
    print(f"generated {OUTPUT} ({len(result['pages'][0]['nodes'])} nodes)")


if __name__ == "__main__":
    main()
