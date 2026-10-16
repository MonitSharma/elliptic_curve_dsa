"""Prove the PLAIN67 operational tool = product25's operational tool + the PLAIN67 qualification bindings.

Every character-level edit between the qualified product25 filter (product-early-filter)
and the qualified PLAIN67 filter (product67-filter) is applied to product25's
operational tool source; the result must equal this experiment's operational tool
source byte for byte, and every other file must be identical.
"""
import difflib
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
ws = root.parent
qual_old, qual_new = ws / "product-early-filter-20261016/tool", ws / "product67-filter-20261016/tool"
op_old, op_new = ws / "product25-operational-20261016/tool", root / "tool"


def apply_edits(qa: str, qb: str, text: str, name: str) -> str:
    """Apply each changed qualification line to text: whole line if it occurs once,
    otherwise each character-level edit anchored by 40 characters on both sides."""
    for la, lb in zip(qa.splitlines(keepends=True), qb.splitlines(keepends=True)):
        if la == lb:
            continue
        if text.count(la) == 1:
            text = text.replace(la, lb)
            continue
        sm = difflib.SequenceMatcher(None, la, lb, autojunk=False)
        for tag, i1, i2, j1, j2 in reversed(sm.get_opcodes()):  # right-to-left keeps anchors unedited
            if tag == "equal":
                continue
            lo, hi = max(0, i1 - 40), min(len(la), i2 + 40)
            old, new = la[lo:hi], la[lo:i1] + lb[j1:j2] + la[i2:hi]
            assert text.count(old) == 1, (name, old[:80])
            text = text.replace(old, new)
    return text


report = {"files": {}}
ok = True
names = sorted({p.relative_to(op_new).as_posix() for p in op_new.rglob("*") if p.is_file() and "target" not in p.parts})
for name in names:
    if name.startswith("target/"):
        continue
    a = (op_old / name).read_text() if (op_old / name).exists() else None
    b = (op_new / name).read_text()
    qa = (qual_old / name).read_text() if (qual_old / name).exists() else None
    qb = (qual_new / name).read_text() if (qual_new / name).exists() else None
    if qa is not None and qb is not None and qa != qb:
        assert len(qa.splitlines()) == len(qb.splitlines()), name
        same = apply_edits(qa, qb, a, name) == b
        report["files"][name] = "QUALIFICATION_EDITS_APPLIED_EQUAL" if same else "MISMATCH"
    elif name == "src/search.rs":
        # The only intended operational edit: the accepted candidate stream binding.
        old, new = "180af069679ffa33b099b200d3337d6fc6c20a451a72508a40dea6617150dc64", "268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d"
        same = a.count(old) == 1 and a.replace(old, new) == b
        report["files"][name] = "CANDIDATE_BINDING_ONLY" if same else "MISMATCH"
    else:
        same = a == b
        report["files"][name] = "IDENTICAL" if same else "MISMATCH"
    ok &= same
report["status"] = "ONLY_PLAIN67_BINDINGS_DIFFER" if ok else "UNEXPLAINED_DIFFERENCE"
report["sha256"] = {n: hashlib.sha256((op_new / n).read_bytes()).hexdigest() for n in names}
(root / "TOOL_DIFF_AUDIT.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "sha256"}, indent=2))
assert ok
