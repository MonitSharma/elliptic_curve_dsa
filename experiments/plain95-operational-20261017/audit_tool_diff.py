"""Prove the PRODUCT95 operational tool = the PLAIN67 operational tool + PRODUCT95 bindings only.

Every source file of plain67-operational-20261016/tool, after applying exactly the
listed binding replacements, must equal the file of the same name in this tool, and
the two trees must hold the same set of files.
"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
ws = root.parent
old, new = ws / "plain67-operational-20261016/tool", root / "tool"
cert67 = ws / "product-exact-20261015/cache-certificate67-20261016"
cert95 = ws / "product-exact-20261015/cache-certificate95-20261017"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
reps = [
    ("268aefe234ede5eaab723e34e214b91f0bd8cac9b0f95d9ee90e3bf3ae8c951d", "ba87b9ceb0691ccfe8c509539cfc38e774ee02134363c19e3541c6e942723e84"),
    ("assert_eq!(n,17_891_821)", "assert_eq!(n,20_275_836)"),
    ("cache-certificate67-20261016", "cache-certificate95-20261017"),
    (sha(cert67 / "CACHE_EQUIVALENCE_CERTIFICATE.json"), sha(cert95 / "CACHE_EQUIVALENCE_CERTIFICATE.json")),
    (sha(cert67 / "PER_INPUT_MASK_TRANSFER.json"), sha(cert95 / "PER_INPUT_MASK_TRANSFER.json")),
    (sha(cert67 / "PER_INPUT_MASK_TRANSFER.md"), sha(cert95 / "PER_INPUT_MASK_TRANSFER.md")),
    ("candidate268aefe2 universal67stage", "candidateba87b9ce universal95stage"),
]
files = lambda t: sorted(str(p.relative_to(t)) for p in t.rglob("*") if p.is_file() and "target" not in p.relative_to(t).parts)
report = {"old_tool": str(old), "new_tool": str(new), "replacements": reps, "files": {}}
ok = files(old) == files(new)
report["same_file_set"] = ok
for rel in files(old):
    a = (old / rel).read_bytes()
    try:
        text = a.decode()
        for x, y in reps:
            text = text.replace(x, y)
        expect = text.encode()
    except UnicodeDecodeError:
        expect = a
    b = (new / rel).read_bytes() if (new / rel).exists() else None
    same = b == expect
    report["files"][rel] = {"equal_after_bindings": same, "changed": a != b, "sha256": hashlib.sha256(b).hexdigest() if b else None}
    ok &= same
report["status"] = "ONLY_PRODUCT95_BINDINGS_DIFFER" if ok else "UNEXPLAINED_DIFFERENCE"
(root / "TOOL_DIFF_AUDIT.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"status": report["status"], "changed": [k for k, v in report["files"].items() if v["changed"]]}, indent=2))
assert ok
