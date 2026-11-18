"""Small, offline acceptance smoke for B-01..B-05; not a P2 audit."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from reqea_codegraph import build_code_index
from reqea_codegraph.walk import scan_tree


class CodegraphSmoke(unittest.TestCase):
    def test_index_and_repeatability(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            source = "import json\nclass Task:\n    def run(self):\n        return self.go()\n    def go(self):\n        return 1\ndef main():\n    return json.dumps(1)\n"
            (root / "app.py").write_text(source, encoding="utf8")
            (root / "web.ts").write_text('import { foo } from "./util";\nexport function hi() { return 1 }\nimport("dynamic");\n', encoding="utf8")
            (root / ".env.production").write_text("SHOULD_NOT_SHOW=123")
            (root / "key.pem").write_text("secret")
            options = {"source_sha": "a" * 40}
            one = build_code_index(d, options)
            two = build_code_index(d, options)
            self.assertEqual(json.dumps(one, sort_keys=True), json.dumps(two, sort_keys=True))
            self.assertEqual(one["schema_version"], "reqea.v1")
            self.assertEqual(one["source_sha"], "a" * 40)
            self.assertEqual([f["path"] for f in one["files"]], ["app.py", "web.ts"])
            app = one["files"][0]
            self.assertEqual(app["sha256"], hashlib.sha256(source.encode()).hexdigest())
            self.assertEqual(app["imports"], ["json"])
            self.assertIn({"name": "Task.run", "kind": "method", "line": 3}, app["symbols"])
            self.assertIn({"src": "app.py:Task.run", "dst": "app.py:Task.go", "kind": "call_candidate"}, one["edges"])
            self.assertIn({"src": "web.ts:module", "dst": "./util", "kind": "import_candidate"}, one["edges"])
            self.assertTrue(any("dynamic_js_ts_import_or_eval_unresolved" in x for x in one["warnings"]))
            self.assertFalse(one["limits"]["truncated"])
            self.assertNotIn("SHOULD_NOT_SHOW", str(one))

    def test_limit_symlink_invalid_root_and_parse_failure(self):
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as other:
            root = Path(d)
            (root / "broken.py").write_text("def bad(: pass")
            (root / "big.py").write_text("x = '" + "a" * 100 + "'")
            (root / "nested").mkdir()
            (root / "nested" / "inner.py").write_text("x=1")
            try:
                (root / "jump.py").symlink_to(Path(other) / "outside.py")
            except (OSError, NotImplementedError):
                pass
            o = build_code_index(d, {"max_file_bytes": 20, "max_depth": 0})
            self.assertTrue(o["limits"]["truncated"])
            self.assertEqual([f["path"] for f in o["files"]], ["broken.py"])
            self.assertTrue(any("static_parse_failed" in x for x in o["warnings"]))
            self.assertTrue(any("max_depth_exceeded" in x for x in o["warnings"]))
            self.assertTrue(any("max_file_bytes_exceeded" in x for x in o["warnings"]))
            if (root / "jump.py").is_symlink():
                self.assertTrue(any("link_skipped" in x for x in o["warnings"]))
            with self.assertRaises(ValueError):
                build_code_index("relative", {})
            with self.assertRaises(ValueError):
                build_code_index(d, {"source_sha": "fake"})
            with self.assertRaises(ValueError):
                scan_tree(d, {"max_files": True})

    def test_total_and_count_bounds(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "a.py").write_text("a=1")
            (Path(d) / "b.py").write_text("b=2")
            r = build_code_index(d, {"max_files": 1})
            self.assertTrue(r["limits"]["truncated"])
            self.assertEqual(r["limits"]["scanned_files"], 1)
            r2 = build_code_index(d, {"max_total_bytes": 3})
            self.assertTrue(r2["limits"]["truncated"])
            self.assertEqual(r2["limits"]["scanned_files"], 1)


if __name__ == "__main__":
    unittest.main()
