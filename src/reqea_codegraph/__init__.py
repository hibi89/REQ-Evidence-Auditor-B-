"""REQEA B code graph: offline-only, static, contract-frozen reqea.v1 (B-05)."""
from __future__ import annotations

import re

from .files import read_file
from .python_ast import parse_python
from .relations import javascript_index, python_edges
from .walk import DEFAULT_LIMITS, scan_tree

SCHEMA_VERSION = "reqea.v1"
_SHA = re.compile(r"(?:[0-9a-fA-F]{40}|UNVERIFIED)\Z")
MAX_SYMBOLS_PER_FILE = 10_000
MAX_EDGES_PER_FILE = 20_000
MAX_WARNINGS = 2_048


def build_code_index(root: str, options: dict) -> dict:
    """Return a deterministic JSON-compatible CodeIndex; never run the target."""
    if not isinstance(options, dict):
        raise ValueError("options_must_be_dict")
    source_sha = options.get("source_sha", "UNVERIFIED")
    if not isinstance(source_sha, str) or _SHA.fullmatch(source_sha) is None:
        raise ValueError("invalid_source_sha")
    scan = scan_tree(root, options)
    files: list[dict] = []
    edges: list[dict] = []
    warnings = set(scan.warnings)
    skipped = scan.skipped_files
    truncated = scan.truncated
    for entry in scan.files:
        try:
            item = read_file(scan.root, entry, options.get("max_file_bytes", DEFAULT_LIMITS["max_file_bytes"]))
        except (OSError, ValueError) as exc:
            skipped += 1
            truncated = True
            code = str(exc) if isinstance(exc, ValueError) and str(exc) in {
                "binary_file_skipped", "non_utf8_file_skipped", "file_changed_or_unsafe",
                "file_changed_during_read", "symlink_or_reparse_disallowed", "path_escape",
            } else "file_unreadable"
            warnings.add(code + ":" + entry.path)
            continue
        record = item.record
        local_edges: list[dict] = []
        local_warnings: list[str] = []
        try:
            if record["language"] == "python":
                tree, record["symbols"], record["imports"], local_warnings = parse_python(item.text)
                local_edges, more_warnings = python_edges(tree, entry.path, record["symbols"], record["imports"])
                local_warnings.extend(more_warnings)
            elif record["language"] in ("javascript", "typescript"):
                (record["symbols"], record["imports"], local_edges,
                 local_warnings) = javascript_index(item.text, entry.path)
        except (SyntaxError, ValueError, RecursionError, MemoryError):
            local_warnings.append("static_parse_failed")
            truncated = True
        if len(record["symbols"]) > MAX_SYMBOLS_PER_FILE:
            record["symbols"] = record["symbols"][:MAX_SYMBOLS_PER_FILE]
            local_warnings.append("symbol_limit_exceeded")
            truncated = True
        if len(local_edges) > MAX_EDGES_PER_FILE:
            local_edges = local_edges[:MAX_EDGES_PER_FILE]
            local_warnings.append("edge_limit_exceeded")
            truncated = True
        for warning in local_warnings:
            if len(warnings) < MAX_WARNINGS:
                warnings.add(warning + ":" + entry.path)
            else:
                warnings.add("warning_limit_exceeded")
                truncated = True
                break
        files.append(record)
        edges.extend(local_edges)
    files.sort(key=lambda f: f["path"])
    edges.sort(key=lambda e: (e["src"], e["dst"], e["kind"]))
    return {
        "schema_version": SCHEMA_VERSION, "source_sha": source_sha,
        "files": files, "edges": edges, "warnings": sorted(warnings),
        "limits": {"truncated": truncated, "scanned_files": len(files), "skipped_files": skipped},
    }
