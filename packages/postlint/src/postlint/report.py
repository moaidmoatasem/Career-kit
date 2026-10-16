from __future__ import annotations

import json
from collections.abc import Sequence

from postlint.finding import ERROR, WARNING, Finding


def exit_code(findings: Sequence[Finding]) -> int:
    return 1 if any(f.severity == ERROR for f in findings) else 0


def render_text(findings: Sequence[Finding]) -> str:
    if not findings:
        return "postlint: clean"
    lines = [f"{f.rule} {f.severity.upper():7} [{f.where}] {f.message}" for f in findings]
    errors = sum(f.severity == ERROR for f in findings)
    warns = sum(f.severity == WARNING for f in findings)
    lines.append(f"postlint: {errors} error(s), {warns} warning(s), {len(findings)} finding(s)")
    return "\n".join(lines)


def render_json(findings: Sequence[Finding]) -> str:
    return json.dumps(
        {"exit_code": exit_code(findings), "findings": [f.to_dict() for f in findings]},
        ensure_ascii=False,
        indent=2,
    )
