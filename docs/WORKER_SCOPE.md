# REQEA worker B — locked work unit boundaries

Mission: 정적 파일·심볼·의존성 인덱스 엔진. Frozen API: build_code_index(root: str, options: dict) -> dict.
A canonical final blueprint: https://github.com/hibi89/REQ-Evidence-Auditor-A-/blob/e58e14ee4ef84dfc226d657cfe45b1d40cfb9ba9/docs/FINAL_BLUEPRINT.md
Shared schema: docs/CONTRACT_V1.md (byte-for-byte copied from A).
Owned source and test paths: src/reqea_codegraph/**, tests/b/**.
Forbidden integration changes: src/reqea/**, other worker module, A pyproject, A CLI/GUI, shared contract, final product scope.

## Assigned SWUs and acceptance
- B-01 (REQ-011, REQ-012): 경로·symlink·제외 목록·depth/byte/files 제한 walker; depends none; path src/reqea_codegraph/walk.py; acceptance 경로이탈·민감 파일 기본 제외, 제한 초과 경고
- B-02 (REQ-013): 파일 메타/언어/SHA256 정규화; depends B-01; path src/reqea_codegraph/files.py; acceptance 같은 내용에 deterministic SHA256/path
- B-03 (REQ-014): Python AST 심볼/라인/임포트 인덱스; depends B-02; path src/reqea_codegraph/python_ast.py; acceptance 코드 실행 없이 함수/클래스/라인 출력
- B-04 (REQ-015, REQ-016): Python 관계 후보 + JS/TS 제한적 static parser; depends B-03; path src/reqea_codegraph/relations.py; acceptance 관계 후보와 동적 해석 미지원 경고
- B-05 (REQ-017, REQ-018): 정적 인덱스 엔트리 build_code_index + file-level 오류 복구; depends B-01, B-02, B-03, B-04; path src/reqea_codegraph/__init__.py; acceptance 계약 JSON, 개별 실패/scan truncate 표시

## Development and handoff
Implement actual functions and their core error paths, not stubs or test-only records. Static analysis must not execute the inspected target.
CLI and module return values MUST conform to reqea.v1. No network or file writes to input. Unsupported scope is UNASSESSED, not fabricated PASS/GAP.
At module completion hand off exact repo/branch/SHA, SHA256 manifest for whitelisted files, warnings, min tests PASS/FAIL/NOT_RUN. A manually copies only allowed module and tests to its integration branch.
Do not delete this repo or update main; preserve history until user separately approves deletion following verified archive.
Next READY: B-01
