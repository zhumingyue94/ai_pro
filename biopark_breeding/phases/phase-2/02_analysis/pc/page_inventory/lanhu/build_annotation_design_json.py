"""蓝湖标注模式解析脚本：通过本地 MCP HTTP 端点获取完整标注数据并生成 design.json。

用途：MCP 客户端传输层会把约 28 万字符的标注响应截断为 20 万字符，
导致「图层精确 CSS 标注」清单缺失尾部内容。本脚本直接与
localhost:8000 的 streamable HTTP MCP 服务器完成 JSON-RPC 握手，
把完整响应写入本地文件后解析，生成符合 design.schema.json 的产物。
适用于 DDS Schema 不可用、仅返回标注模式（annotation fallback）的设计图。
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

IMAGE_ID = "096f881a-bda8-4d38-9418-e25389e66ea7"
DESIGN_NAME = "发货执行-栋舍视图-空"
PROJECT_URL = (
    "https://lanhuapp.com/web/#/item/project/stage"
    "?tid=fa376857-ec69-426d-a28b-c2490b28b31a"
    "&pid=f9b0f9c2-896f-4601-ae62-611f9cd2e567"
    f"&image_id={IMAGE_ID}"
)
# 本脚本位于 二期/02_analysis/pc/page_inventory/lanhu/，上溯 4 层到 二期 根
ROOT = Path(__file__).resolve().parents[4]
RAW_OUTPUT = Path(__file__).resolve().parent / "lanhu_annotation_096f881a.txt"
SCHEMA_PATH = ROOT.parent.parent.parent / "schemas" / "design.schema.json"
OUTPUT = Path(__file__).resolve().parent / f"{DESIGN_NAME}_design.json"

MCP_ENDPOINT = "http://localhost:8000/mcp?role=Developer&name=YourName"
PROTOCOL_VERSION = "2024-11-05"


def jsonrpc_post(session_id: str | None, payload: dict[str, Any]) -> tuple[Any, str | None]:
    """发送一次 JSON-RPC 请求并返回 (结果, 新会话ID)。"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    request = Request(MCP_ENDPOINT, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urlopen(request, timeout=600) as response:  # noqa: S310 本地受信端点
        new_session = response.headers.get("Mcp-Session-Id") or session_id
        content_type = response.headers.get("Content-Type", "")
        body = response.read().decode("utf-8")
    if not body.strip():
        return None, new_session  # 通知类请求（如 notifications/initialized）无响应体
    if "text/event-stream" in content_type:
        for line in body.splitlines():
            if line.startswith("data:"):
                event = json.loads(line[5:].strip())
                return event.get("result", event), new_session
        return None, new_session
    return json.loads(body).get("result"), new_session


def call_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """初始化 MCP 会话并调用指定工具，返回拼接后的文本内容。"""
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "design-inventory-fetcher", "version": "1.0"},
        },
    }
    _, session_id = jsonrpc_post(None, init_payload)
    jsonrpc_post(session_id, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    result, _ = jsonrpc_post(
        session_id,
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        },
    )
    chunks: list[str] = []
    for item in (result or {}).get("content", []):
        if isinstance(item, dict) and item.get("type") == "text":
            chunks.append(str(item.get("text", "")))
    return "\n".join(chunks)


def parse_css(css: str) -> dict[str, Any]:
    """把 data-css 字符串解析为键值对象。"""
    props: dict[str, Any] = {}
    for part in css.split(";"):
        part = part.strip()
        if not part or ":" not in part:
            continue
        key, _, value = part.partition(":")
        key = key.strip()
        value = value.strip()
        if key in ("left", "top", "width", "height"):
            match = re.fullmatch(r"(-?\d+(?:\.\d+)?)px", value)
            props[key] = float(match.group(1)) if match else None
        else:
            props[key] = value
    return props


def classify(layer_type: str, css: dict[str, Any]) -> str:
    """按标注通道的图层类型与尺寸推断节点分类。"""
    if layer_type == "textLayer":
        return "text"
    if layer_type == "artboard":
        return "image"
    if layer_type == "symbolInstence":
        return "icon"
    width = css.get("width")
    if layer_type == "symbolMaster":
        return "container"
    height = css.get("height")
    max_side = max(side for side in (width, height) if side is not None) if width or height else 0.0
    return "icon" if max_side <= 20.0 else "shape"


def build_document(layers: list[dict[str, Any]]) -> dict[str, Any]:
    """把标注图层列表转换为符合 design.schema.json 的文档。"""
    nodes: list[dict[str, Any]] = []
    for index, layer in enumerate(layers):
        layer_type = str(layer["layer_type"])
        css = layer["css"]
        rect: dict[str, float | None] | None = None
        if any(css.get(key) is not None for key in ("left", "top", "width", "height")):
            rect = {
                "x": css.get("left"),
                "y": css.get("top"),
                "width": css.get("width"),
                "height": css.get("height"),
            }
        element_id = f"lanhu-{IMAGE_ID}-ann-{index}"
        nodes.append(
            {
                "element_id": element_id,
                "kind": classify(layer_type, css),
                "name": layer["name"],
                "original_type": layer_type,
                "classification": classify(layer_type, css),
                "tag": None,
                "role": None,
                "text": layer.get("text"),
                "rect": rect,
                "rect_source": "annotation.css",
                "style": {key: value for key, value in css.items() if key not in ("left", "top", "width", "height")} or None,
                "class": None,
                "image_ref": layer.get("slice"),
                "parent_element_id": None,
                "child_element_ids": [],
                "depth": 1,
                "path": str(index),
                "raw_node": {"layer_type": layer_type, "css": layer["css_raw"]},
            }
        )
    return {
        "schema_version": "1.0",
        "design_id": IMAGE_ID,
        "design_name": DESIGN_NAME,
        "source": {
            "source_file": PROJECT_URL,
            "source_format": "Lanhu annotation fallback (DDS Schema unavailable: store_schema_revise failed)",
            "slice_scale": None,
            "is_figma": True,
            "coordinate_policy": (
                "标注模式：坐标取自图层 CSS 标注 left/top/width/height；"
                "蓝湖 DDS Schema 版本数据不存在，图层父子层级不可得，"
                "parent_element_id 置空、child_element_ids 置空，不推断层级。"
            ),
        },
        "capture": {
            "collector": "lanhu mcp annotation fallback parser",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "source_node_count": len(nodes),
        },
        "pages": [
            {
                "page_id": f"lanhu-{IMAGE_ID}",
                "title": DESIGN_NAME,
                "roots": [node["element_id"] for node in nodes],
                "node_count": len(nodes),
                "max_depth": 1,
                "nodes": nodes,
            }
        ],
    }


def extract_layers(markdown_text: str) -> list[dict[str, Any]]:
    """从响应文本的「图层精确 CSS 标注」段解析结构化图层行。"""
    layers: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^\s*\[(?P<type>textLayer|shapeLayer|artboard|symbolInstence|symbolMaster)\]\s+(?P<name>.+?):\s+"
        r"(?P<css>position: absolute;[^\n|]+?)"
        r"(?:\s*\|\s*text=\"(?P<text>[^\"]*)\")?"
        r"(?:\s*\|\s*slice=(?P<slice>\S+))?"
        r"(?:\s*\|\s*[A-Za-z]+=\S+)*\s*$"
    )
    for line in markdown_text.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        css_raw = re.sub(r"\s+", " ", match.group("css").strip())
        layers.append(
            {
                "layer_type": match.group("type"),
                "name": match.group("name").strip(),
                "text": match.group("text"),
                "slice": match.group("slice"),
                "css": parse_css(css_raw),
                "css_raw": css_raw,
            }
        )
    return layers


def main() -> None:
    """获取完整标注响应、解析图层并写出经 schema 校验的 design.json。"""
    import jsonschema

    markdown_text = call_tool(
        "lanhu_get_ai_analyze_design_result",
        {"url": PROJECT_URL, "design_names": DESIGN_NAME},
    )
    RAW_OUTPUT.write_text(markdown_text, encoding="utf-8")
    layers = extract_layers(markdown_text)
    if not layers:
        raise SystemExit("未解析到任何图层标注行，请人工检查原始响应格式")
    document = build_document(layers)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(document)
    OUTPUT.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    kinds: dict[str, int] = {}
    for node in document["pages"][0]["nodes"]:
        kinds[node["kind"]] = kinds.get(node["kind"], 0) + 1
    print(f"generated {OUTPUT}")
    print(f"layers={len(layers)} kinds={kinds}")


if __name__ == "__main__":
    main()
