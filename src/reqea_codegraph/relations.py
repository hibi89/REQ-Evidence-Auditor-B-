"""Conservative Python call candidates and explicitly limited JS/TS patterns (B-04)."""
from __future__ import annotations

import ast
import re

# Patterns deliberately restrict themselves to static, single-line candidates.
_JS_DECL = re.compile(r"\b(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(|\bclass\s+([A-Za-z_$][\w$]*)\b|\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^\n]{0,200}\)|[A-Za-z_$][\w$]*)\s*=>")
_JS_IMPORT = re.compile(r"\bimport\s+(?:[^\n;]{0,200}?\s+from\s+)?[\"']([^\n\"']+)[\"']|\brequire\s*\(\s*[\"']([^\n\"']+)[\"']\s*\)")
_JS_DYNAMIC = re.compile(r"\bimport\s*\(|\beval\s*\(|\bnew\s+Function\s*\(|\brequire\s*\(\s*[^\s\"']")


def python_edges(tree: ast.AST, path: str, symbols: list[dict], imports: list[str]) -> tuple[list[dict], list[str]]:
    edges = [{"src": f"{path}:module", "dst": name, "kind": "import_candidate"} for name in imports]
    names = {s["name"] for s in symbols if s["kind"] in ("function", "method")}
    warnings: set[str] = set()

    class Calls(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[str] = []
            self.class_stack: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.stack.append(node.name)
            self.class_stack.append(".".join(self.stack))
            self.generic_visit(node)
            self.class_stack.pop()
            self.stack.pop()

        def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        visit_FunctionDef = _function
        visit_AsyncFunctionDef = _function

        def visit_Call(self, node: ast.Call) -> None:
            src = f"{path}:{'.'.join(self.stack) if self.stack else 'module'}"
            target: str | None = None
            if isinstance(node.func, ast.Name):
                target = node.func.id if node.func.id in names else None
            elif (isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
                  and node.func.value.id in ("self", "cls") and self.class_stack):
                candidate = self.class_stack[-1] + "." + node.func.attr
                target = candidate if candidate in names else None
            if target is not None:
                edges.append({"src": src, "dst": f"{path}:{target}", "kind": "call_candidate"})
            if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "__import__"):
                warnings.add("dynamic_python_execution_reference_unresolved")
            self.generic_visit(node)

    Calls().visit(tree)
    if any(e["kind"] == "call_candidate" for e in edges):
        warnings.add("python_calls_static_candidates_only")
    return sorted({(e["src"], e["dst"], e["kind"]): e for e in edges}.values(), key=lambda e: (e["src"], e["dst"], e["kind"])), sorted(warnings)


def javascript_index(source: str, path: str) -> tuple[list[dict], list[str], list[dict], list[str]]:
    symbols: list[dict] = []
    imports: set[str] = set()
    warnings = {"js_ts_regex_candidates_unverified"}
    for match in _JS_DECL.finditer(source):
        name = match.group(1) or match.group(2) or match.group(3)
        kind = "class" if match.group(2) else "function"
        symbols.append({"name": name, "kind": kind, "line": source.count("\n", 0, match.start()) + 1})
    for match in _JS_IMPORT.finditer(source):
        imports.add(match.group(1) or match.group(2))
    if _JS_DYNAMIC.search(source):
        warnings.add("dynamic_js_ts_import_or_eval_unresolved")
    if path.endswith((".ts", ".tsx", ".mts", ".cts")):
        warnings.add("typescript_types_not_resolved")
    edges = [{"src": f"{path}:module", "dst": name, "kind": "import_candidate"} for name in sorted(imports)]
    symbols.sort(key=lambda s: (s["name"], s["line"], s["kind"]))
    return symbols, sorted(imports), edges, sorted(warnings)
