"""File hashing and safe text extraction (B-02); no source text leaves the package."""
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from .walk import WalkFile, _is_reparse, safe_relative

LANGUAGES = {
    ".py": "python", ".pyi": "python", ".js": "javascript",
    ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".mts": "typescript",
    ".cts": "typescript",
}


@dataclass(frozen=True)
class FileData:
    record: dict
    text: str


def read_file(root: Path, entry: WalkFile, max_file_bytes: int) -> FileData:
    if not safe_relative(entry.path):
        raise ValueError("unsafe_relative_path")
    if not isinstance(max_file_bytes, int) or max_file_bytes < 1:
        raise ValueError("invalid_file_limit")
    path = root.joinpath(*entry.path.split("/"))
    # Recheck all components, including Windows junction/reparse-point directories.
    current = root
    for part in entry.path.split("/"):
        current = current / part
        st = current.lstat()
        if stat.S_ISLNK(st.st_mode) or _is_reparse(st):
            raise ValueError("symlink_or_reparse_disallowed")
    if os.path.commonpath((os.path.realpath(root), os.path.realpath(path))) != os.path.realpath(root):
        raise ValueError("path_escape")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if (not stat.S_ISREG(before.st_mode) or _is_reparse(before) or before.st_nlink > 1
                or (before.st_dev, before.st_ino) != (entry.device, entry.inode)
                or before.st_size != entry.size or before.st_size > max_file_bytes):
            raise ValueError("file_changed_or_unsafe")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            data = stream.read(max_file_bytes + 1)
        after = os.fstat(descriptor)
        if (len(data) > max_file_bytes or len(data) != entry.size
                or (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
                != (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)):
            raise ValueError("file_changed_during_read")
    finally:
        os.close(descriptor)
    if b"\0" in data:
        raise ValueError("binary_file_skipped")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeError as exc:
        raise ValueError("non_utf8_file_skipped") from exc
    return FileData(
        {"path": entry.path, "language": LANGUAGES.get(Path(entry.path).suffix.casefold(), "other"),
         "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
         "symbols": [], "imports": []},
        text,
    )
