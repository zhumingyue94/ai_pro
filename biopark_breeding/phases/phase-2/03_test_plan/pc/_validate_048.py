# -*- coding: utf-8 -*-
import sys, json, glob, os
import yaml, jsonschema

base = r"D:/02test_pro/biopark_breeding/phase-2"
plan = os.path.join(base, "03_test_plan", "pc", "TEST_PLAN_REQ-PC-048.yaml")
schema = r"D:/02test_pro/ui_test/.agents/references/test-plan.schema.json"

with open(plan, encoding="utf-8") as f:
    doc = yaml.safe_load(f)
with open(schema, encoding="utf-8") as f:
    sch = json.load(f)

jsonschema.validate(doc, sch)

# 检查不允许的字段
def walk(node, path="root"):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("tp", "tp_id"):
                print("FORBIDDEN FIELD:", path + "." + k)
                sys.exit(1)
            walk(v, path + "." + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]")

walk(doc)
print("VALID")
