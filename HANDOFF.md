# HANDOFF — REQEA B · P1 code candidate
**Date:** 2026-11-18 KST · **Work start:** 15:07 KST · **Code/test complete:** 15:19 KST
**Repo/branch:** `hibi89/REQ-Evidence-Auditor-B-@feature/reqea-b-codegraph-p1-20261118`
**P1 code snapshot commit (exact):** `ff7741477727a42adb9a8db09019ebb1159834bf`
**A canonical design commit:** `e58e14ee4ef84dfc226d657cfe45b1d40cfb9ba9`
**A/B frozen contract blob:** `b39d8307662206472f2165b4bce3c0e10e2b62b6` · version `reqea.v1`
**Central policy checked:** `kmong-productization@77a0d978bb5676c3867b11806461e8a043e627a9` (at start)

## B SWU results (5 actual code candidates)
- **B-01 / REQ-011,012**: `src/reqea_codegraph/walk.py`; absolute root validation, deterministic bounded DFS, symlink/reparse/hardlink and secret/default hidden exclusions, file/count/depth/total-byte truncation warnings. Local PASS.
- **B-02 / REQ-013**: `src/reqea_codegraph/files.py`; recheck selected entries, regular file and identity guards, bounded read, language/bytes/real SHA256, UTF-8 decode, binary detection. Local PASS.
- **B-03 / REQ-014**: `src/reqea_codegraph/python_ast.py`; Python AST-only class/function/method/line/import extraction, including relative import uncertainty. Local PASS.
- **B-04 / REQ-015,016**: `src/reqea_codegraph/relations.py`; Python same-file call/import candidates, JS/TS restricted regexp import/symbol candidates, explicit warnings for unresolved/dynamic semantics. Local PASS.
- **B-05 / REQ-017,018**: `src/reqea_codegraph/__init__.py`; `build_code_index(root: str, options: dict) -> dict`, exact `reqea.v1` keys, deterministic sorting, per-file parse/read failure isolation and truncated flag. Local PASS.

## Immutable code/test SHA256 manifest (only these 6 whitelisted files to integrate)
```text
27aeadd93113d6ae7530a947b1dcfa8f1f9b6b1e84cdc1361565bee191e7d9ad  src/reqea_codegraph/__init__.py
707bd82d468fbae7926e496f7494cf5014ac2d66f4313b0a780dbf615beb858b  src/reqea_codegraph/files.py
527fc6c28346be19b3392c0947499abbc269309e4151569ab59a13684e6288b5  src/reqea_codegraph/python_ast.py
3fec0661c98c8cc932fb3e5956f584f77af598c2893e88d1fa3f85703e5a4957  src/reqea_codegraph/relations.py
8c3784ffc3f49b106830c7d1a98ce79e539675f07d42d1286928482e5afdd157  src/reqea_codegraph/walk.py
e0509f73e02902ca57e922a0494c03cb054dc3fbf3b550f1ba34ab4e0c6ff2b6  tests/b/test_codegraph.py
```

## Actual tests on isolated synthetic temp directories (Linux Python 3.11)
- `python -m compileall -q src`: **PASS**.
- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/b -v`: **PASS 3/3**, deterministic JSON and real SHA, AST/import/call candidates, TS/dynamic warnings, secret exclusion, symlink, bounds, invalid inputs, syntax failure. Initial test expectation for total-byte budget was corrected before code commit.
- **P2 independent CI/security, Windows EXE/GUI, real Windows junction/race, very large inputs, A/C integration:** **NOT_RUN**.
- **Known limits:** JS/TS are regex candidates (comment/string false positives possible); dynamic imports/calls/TS types are explicitly not resolved; static absence must never mean verified GAP. Windows reparse/TOCTOU and resource-abuse corner cases remain P2 verification scope.
- **Safety:** no untrusted target source import, eval, exec, network, package install, or source modification. Public repo includes only authored implementation and synthetic tests, no customer code or keys.

## Integration
A owner copies **only** `src/reqea_codegraph/**` and `tests/b/**` from exact B code commit `ff7741477727a42adb9a8db09019ebb1159834bf` to A's integration branch and verifies manifest/schema. Do not copy/overwrite B docs, AGENTS, STATUS, queue, README or A modules. A integration: **NOT_RUN**. B P1 5/5 SWU candidates; **official implementation completion UNASSESSED; P2 NOT_RUN; release HOLD**. The later documentation-only HANDOFF commit changes the branch HEAD but not the code commit or file hashes above; resolve current branch HEAD directly from GitHub. No main merge.
