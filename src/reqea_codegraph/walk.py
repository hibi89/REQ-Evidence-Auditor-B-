"""Deterministic, read-only, bounded source-tree enumeration (B-01)."""
from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LIMITS = {
    "max_files": 10_000,
    "max_file_bytes": 2_000_000,
    "max_total_bytes": 50_000_000,
    "max_depth": 32,
}
SOURCE_EXTENSIONS = frozenset({
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts",
    ".tsx", ".mts", ".cts", ".json", ".md", ".txt", ".toml",
    ".yaml", ".yml", ".html", ".css", ".sql", ".sh", ".ps1",
})
SKIP_DIRS = frozenset({
    ".git", ".hg", ".svn", ".ssh", ".gnupg", ".cache", ".venv",
    "venv", "env", "node_modules", "__pycache__", "dist", "build",
    "target", ".next", ".tox", ".mypy_cache", ".pytest_cache",
    "site-packages", "coverage", ".idea", ".vscode",
})
SKIP_NAMES = frozenset({
    "id_rsa", "id_dsa", "id_ed25519", "id_ecdsa", "known_hosts",
    "authorized_keys", "credentials", "credentials.json", "secrets.json",
    "secrets.yaml", "secrets.yml", "config.json", "kubeconfig",
})
SKIP_SUFFIXES = (".pem", ".p12", ".pfx", ".key", ".jks", ".keystore")


@dataclass(frozen=True)
class WalkFile:
    path: str  # POSIX root-relative; never absolute
    size: int
    device: int
    inode: int


@dataclass
class WalkResult:
    root: Path
    files: list[WalkFile]
    warnings: list[str]
    truncated: bool
    skipped_files: int


def safe_relative(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return bool(parts) and all(p not in ("", ".", "..") for p in parts) and not path.startswith(("/", "\\")) and ":" not in parts[0]


def _excluded(name: str, directory: bool) -> bool:
    lower = name.casefold()
    if lower.startswith(".") or lower.startswith(".env"):
        return True
    if directory:
        return lower in SKIP_DIRS
    if lower in SKIP_NAMES or lower.startswith(("secret", "credential")):
        return True
    return lower.endswith(SKIP_SUFFIXES) or Path(lower).suffix not in SOURCE_EXTENSIONS


def _is_reparse(st: os.stat_result) -> bool:
    return bool(getattr(st, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def validated_root(root: str) -> Path:
    if not isinstance(root, str) or not root or not os.path.isabs(root):
        raise ValueError("root_must_be_absolute")
    if root.startswith(("\\\\", "//")):
        raise ValueError("unc_root_disallowed")
    p = Path(root)
    try:
        st = p.lstat()
    except OSError as exc:
        raise ValueError("root_unavailable") from exc
    if not stat.S_ISDIR(st.st_mode) or _is_reparse(st) or p.is_symlink():
        raise ValueError("root_not_regular_directory")
    # Symlink ancestors and junctions are not accepted as a selected root.
    if os.path.normcase(os.path.realpath(p)) != os.path.normcase(os.path.abspath(p)):
        raise ValueError("root_through_symlink_disallowed")
    return p


def scan_tree(root: str, options: dict) -> WalkResult:
    p = validated_root(root)
    if not isinstance(options, dict):
        raise ValueError("options_must_be_dict")
    limits = dict(DEFAULT_LIMITS)
    for key in limits:
        if key in options:
            v = options[key]
            if isinstance(v, bool) or not isinstance(v, int) or v < (0 if key == "max_depth" else 1) or v > 1_000_000_000:
                raise ValueError("invalid_" + key)
            limits[key] = v
    result = WalkResult(p, [], [], False, 0)
    remaining = limits["max_total_bytes"]
    # Iterative DFS; sorting at each directory and final result makes order stable.
    stack = [(p, "", 0)]
    while stack:
        directory, prefix, depth = stack.pop()
        try:
            entries = sorted(os.scandir(directory), key=lambda e: e.name)
        except OSError:
            result.truncated = True
            result.warnings.append("directory_unreadable:" + (prefix or "."))
            continue
        subdirs = []
        for entry in entries:
            relative = prefix + entry.name
            if not safe_relative(relative):
                result.skipped_files += 1
                continue
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError:
                result.skipped_files += 1
                result.truncated = True
                result.warnings.append("entry_unreadable:" + relative)
                continue
            if stat.S_ISLNK(info.st_mode) or _is_reparse(info):
                result.skipped_files += 1
                result.warnings.append("link_skipped:" + relative)
                continue
            if stat.S_ISDIR(info.st_mode):
                if _excluded(entry.name, True):
                    result.skipped_files += 1
                elif depth >= limits["max_depth"]:
                    result.skipped_files += 1
                    result.truncated = True
                    result.warnings.append("max_depth_exceeded:" + relative)
                else:
                    subdirs.append((Path(entry.path), relative + "/", depth + 1))
                continue
            if not stat.S_ISREG(info.st_mode) or info.st_nlink > 1 or _excluded(entry.name, False):
                result.skipped_files += 1
                continue
            if len(result.files) >= limits["max_files"]:
                result.skipped_files += 1
                result.truncated = True
                result.warnings.append("max_files_exceeded")
                continue
            if info.st_size > limits["max_file_bytes"]:
                result.skipped_files += 1
                result.truncated = True
                result.warnings.append("max_file_bytes_exceeded:" + relative)
                continue
            if info.st_size > remaining:
                result.skipped_files += 1
                result.truncated = True
                result.warnings.append("max_total_bytes_exceeded")
                continue
            remaining -= info.st_size
            result.files.append(WalkFile(relative, info.st_size, info.st_dev, info.st_ino))
        stack.extend(reversed(subdirs))
    result.files.sort(key=lambda f: f.path)
    result.warnings = sorted(set(result.warnings))
    return result
