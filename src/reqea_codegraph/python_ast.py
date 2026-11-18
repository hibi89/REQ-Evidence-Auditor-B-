"""Side-effect-free Python symbol/import extraction using the standard AST (B-03)."""
from __future__ import annotations

import ast


def parse_python(source: str) -> tuple[ast.AST, list[dict], list[str], list[str]]:
    """Parse text without importing or executing it. Invalid Python raises SyntaxError."""
    tree = ast.parse(source)
    symbols: list[dict] = []
    imports: set[str] = set()
    warnings: set[str] = set()

    class Collect(ast.NodeVisitor):
        def __init__(self) -> None:
            self.stack: list[tuple[str, str]] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            name = ".".join([n for n, _ in self.stack] + [node.name])
            symbols.append({"name": name, "kind": "class", "line": node.lineno})
            self.stack.append((node.name, "class"))
            self.generic_visit(node)
            self.stack.pop()

        def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            name = ".".join([n for n, _ in self.stack] + [node.name])
            kind = "method" if self.stack and self.stack[-1][1] == "class" else "function"
            symbols.append({"name": name, "kind": kind, "line": node.lineno})
            self.stack.append((node.name, "function"))
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._function(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._function(node)

        def visit_Import(self, node: ast.Import) -> None:
            imports.update(alias.name for alias in node.names)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            module = "." * node.level + (node.module or "")
            if module:
                imports.add(module)
            if node.level:
                warnings.add("relative_import_resolution_unverified")
            if any(alias.name == "*" for alias in node.names):
                warnings.add("wildcard_import_unresolved")

    Collect().visit(tree)
    symbols.sort(key=lambda s: (s["name"], s["line"], s["kind"]))
    return tree, symbols, sorted(imports), sorted(warnings)
