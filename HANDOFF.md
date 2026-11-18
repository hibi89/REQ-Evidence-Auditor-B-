# HANDOFF — REQEA B · P1 code candidate
**Date:** 2026-11-18 KST · **Work start:** 15:07 KST · **Code/test complete:** 15:19 KST
**Repo/branch:** `hibi89/REQ-Evidence-Auditor-B-@feature/reqea-b-codegraph-p1-20261118`
**P1 code snapshot commit (exact):** `4ffaa0e5c7278acd28f20813fe08d669f64753f0`
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
ac23a20f7122d61c8434401d1c5e54ad6451b6cf1168ccdfd3dd2342b78e487c  src/reqea_codegraph/__init__.py
707bd82d468fbae7926e496f7494cf5014ac2d66f4313b0a780dbf615beb858b  src/reqea_codegraph/files.py
527fc6c28346be19b3392c0947499abbc269309e4151569ab59a13684e6288b5  src/reqea_codegraph/python_ast.py
3fec0661c98c8cc932fb3e5956f584f77af598c2893e88d1fa3f85703e5a4957  src/reqea_codegraph/relations.py
f45c2408f0714eb040d0ddaf662e331196d02855e6238e23a5f277cf09c5a69a  src/reqea_codegraph/walk.py
e3f9caeb7ad8a9a032c8e11ee488ba32355ce5facabb5a7191dcfffd16a45c61  tests/b/test_codegraph.py
```

## Actual tests on isolated synthetic temp directories (Linux Python 3.11)
- `python -m compileall -q src`: **PASS**.
- `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/b -v`: **PASS 3/3**, deterministic JSON and real SHA, AST/import/call candidates, TS/dynamic warnings, secret exclusion, symlink, bounds, invalid inputs, syntax failure. Initial test expectation for total-byte budget was corrected before code commit.
- **P2 independent CI/security, Windows EXE/GUI, real Windows junction/race, very large inputs, A/C integration:** **NOT_RUN**.
- **Known limits:** JS/TS are regex candidates (comment/string false positives possible); dynamic imports/calls/TS types are explicitly not resolved; static absence must never mean verified GAP. Windows reparse/TOCTOU and resource-abuse corner cases remain P2 verification scope.
- **Safety:** no untrusted target source import, eval, exec, network, package install, or source modification. Public repo includes only authored implementation and synthetic tests, no customer code or keys.

## Integration
A owner copies **only** `src/reqea_codegraph/**` and `tests/b/**` from exact B code commit `4ffaa0e5c7278acd28f20813fe08d669f64753f0` to A's integration branch and verifies manifest/schema. Do not copy/overwrite B docs, AGENTS, STATUS, queue, README or A modules. A integration: **NOT_RUN**. B P1 5/5 SWU candidates; **official implementation completion UNASSESSED; P2 NOT_RUN; release HOLD**. The later documentation-only HANDOFF commit changes the branch HEAD but not the code commit or file hashes above; resolve current branch HEAD directly from GitHub. No main merge.

## 2026-11-18 KST B-01/B-05 boundary correction (15:31–15:36)
- **Actual defect reproduced:** 2,110 symlinks generated 2,110 warnings with `truncated=false` despite intended bounded output.
- **Code repair commit:** `4ffaa0e5c7278acd28f20813fe08d669f64753f0`; changed only B-owned `walk.py`, `__init__.py`, `tests/b/test_codegraph.py`; all 5 B SWUs remain `IMPLEMENTED_UNVERIFIED`.
- **Repair:** walker warnings capped at 1,024 + one explicit `warning_limit_exceeded` sentinel, and index-level file/parse warning fanout capped at 2,048 + sentinel. Surpassing either cap sets `limits.truncated=true`; original file paths/source bodies/keys are not published.
- **Actual local rechecks:** `python -m compileall -q src tests/b` **PASS**, `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests/b -v` **PASS 4/4** with 2,060 broken Python files and 1,100 synthetic symlinks; code snapshot matches recorded Git blob SHAs.
- **Code SHA256 (updated three files):** `ac23a20f7122d61c8434401d1c5e54ad6451b6cf1168ccdfd3dd2342b78e487c` (__init__.py), `f45c2408f0714eb040d0ddaf662e331196d02855e6238e23a5f277cf09c5a69a` (walk.py), `e3f9caeb7ad8a9a032c8e11ee488ba32355ce5facabb5a7191dcfffd16a45c61` (test_codegraph.py). Other three original file hashes unchanged.
- **A status at inspection:** `integration/reqea-p1-20261118@d423fea91668affd691c399918e3f16b06954501` held previous B files, all six old B Git blob SHAs identical; A needs to import the three changed files from the repair commit after checking current A HEAD. **No A write or A integration verification performed by B**.
- **P1 B implementation SWU count:** 5/5=100% SWU code candidates only; **official rate UNASSESSED**, P2 **NOT_RUN**, release **HOLD**.
