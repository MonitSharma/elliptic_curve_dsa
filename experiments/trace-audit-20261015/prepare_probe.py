"""Prepare an observation-only follow-up locally; no server launch or circuit build."""
import difflib
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
source = root.parent / "trace-value-20261015/value_trace.rs"
text = source.read_text(encoding="utf-8")
old = 'let diff=sub(vals[lane][ti],want,p);'
new = old + '\n                                    let diff_s=sub(vals[lane][si],source,p);'
assert text.count(old) == 1
modified = text.replace(old, new)
old = 'diff_t={:#x} log2diff={}",m.phase,m.tick,[m.rails[0].len(),m.rails[1].len()],diff,diff.bit_len())));'
new = ('diff_t={:#x} log2diff={} diff_s={:#x} got_t={:#x} want_t={:#x} got_s={:#x} want_s={:#x} low={}",'
       'm.phase,m.tick,[m.rails[0].len(),m.rails[1].len()],diff,diff.bit_len(),diff_s,vals[lane][ti],want,vals[lane][si],source,m.low)));')
assert modified.count(old) == 1
modified = modified.replace(old, new)
output = root / "value_trace_probe.rs"
output.write_text(modified, encoding="utf-8", newline="\n")
patch = "".join(difflib.unified_diff(text.splitlines(True), modified.splitlines(True),
                                  fromfile="a/src/point_add/value_trace.rs", tofile="b/src/point_add/value_trace.rs"))
(root / "observer-detail.patch").write_text(patch, encoding="utf-8", newline="\n")
manifest = {"status": "prepared locally; not compiled or run", "score": None,
            "source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "patch_sha256": hashlib.sha256((root / "observer-detail.patch").read_bytes()).hexdigest(),
            "changes": "Only event serialization and source-delta calculation; no circuit gates changed.",
            "required_validation": ["Apply only in a new isolated observer copy.",
                "Compile and rerun the unchanged valuefail186 and independent packets.",
                "Check protected simulator equality, final stream hash, completion, and family-aware analysis.",
                "Expected value not representable establishes an encoding-width obstruction; representable values require further diagnosis."]}
(root / "probe-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest, indent=2))
