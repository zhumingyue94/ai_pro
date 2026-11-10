import ast
import pathlib
import py_compile
import sys

ROOT = pathlib.Path(r"D:\02test_pro\ui_test\projects\industry_chain_scheduling\phase-1")
FILES = [
    "07_ui_automation/config/settings.py",
    "07_ui_automation/pages/common/login_page.py",
    "07_ui_automation/pages/common/portal_navigation.py",
    "../../scripts/build_module_case_map.py",
    "../../scripts/login_zentao.py",
    ]

ok = True
for rel in FILES:
    p = ROOT / rel
    try:
        py_compile.compile(str(p), doraise=True)
    except py_compile.PyCompileError as exc:
        print(f"COMPILE_FAIL {rel}: {exc}")
        ok = False

total = 0
covered = 0
missing = []
for rel in FILES:
    p = ROOT / rel
    tree = ast.parse(p.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            total += 1
            if ast.get_docstring(node):
                covered += 1
            else:
                missing.append(f"{rel}:{node.lineno}:{node.name}")

print(f"TOTAL={total} COVERED={covered} MISSING={len(missing)}")
for m in missing:
    print("MISS", m)
if missing or not ok:
    sys.exit(1)
print("ALL_OK")
