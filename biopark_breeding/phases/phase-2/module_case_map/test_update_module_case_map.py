import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI_TEST_ROOT = ROOT.parents[3]
if str(UI_TEST_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_TEST_ROOT))

from scripts.update_module_case_map import apply_operation, load_json


ROOT = Path(__file__).resolve().parent


class RegistryOperationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_json(ROOT / "module_case_map.json")

    def test_grouped_registry_integrity(self):
        self.assertEqual(self.registry["schema_version"], "2.0")
        self.assertEqual(sum(len(m["cases"]) for m in self.registry["modules_by_req_id"].values()), 626)
        self.assertEqual(len(self.registry["modules_by_req_id"]["REQ-APP-024"]["cases"]), 52)

    def test_update_case_isolated(self):
        before = copy.deepcopy(self.registry)
        case = copy.deepcopy(before["modules_by_req_id"]["REQ-APP-024"]["cases"]["TC-APP-024-001"])
        after, _ = apply_operation(before, "update-case", "REQ-APP-024", "TC-APP-024-001", {"case": case}, False)
        self.assertEqual(after["modules_by_req_id"]["REQ-APP-023"], before["modules_by_req_id"]["REQ-APP-023"])

    def test_unknown_case_rejected(self):
        with self.assertRaises(ValueError):
            apply_operation(copy.deepcopy(self.registry), "delete-case", "REQ-APP-024", "TC-APP-024-999", {}, False)


if __name__ == "__main__":
    unittest.main()
