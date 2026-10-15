"""Prepare a private, gate-inert observer copy of the wide (cap1536) B3 circuit.

Source: /home/hclau/ecdsa_research/dynamic-pool-20261015/wide-b3 (read only).
Destination: /home/hclau/ecdsa_research/trace-value-20261015/observer-b3.
Diagnostic only; score=NONE.
"""
from pathlib import Path
import hashlib, json, subprocess

import sys
# Usage: prepare.py [ROOT SRC FAILS_TSV EXPECTED_STREAM]; defaults reproduce the first (wide-b3) trace.
root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/hclau/ecdsa_research/trace-value-20261015")
src = Path(sys.argv[2] if len(sys.argv) > 2 else "/home/hclau/ecdsa_research/dynamic-pool-20261015/wide-b3")
fails_tsv = Path(sys.argv[3]) if len(sys.argv) > 3 else None
expected = sys.argv[4] if len(sys.argv) > 4 else "95e771bae57bd96e75c11b569faf2f87cd7dfa52b227b40dd16e40a301d8e122"
census = Path("/home/hclau/ecdsa_research/failure-census-20261015")
dest = root / "observer-b3"
assert not dest.exists()
dest.mkdir()
subprocess.run(f"cd {src} && tar cf - --exclude=./ops.bin --exclude=./target . | (cd {dest} && tar xf -)", shell=True, check=True)
base = dest / "src/point_add"
(base / "value_trace.rs").write_bytes((root / "value_trace.rs").read_bytes())
(base / "observed_sim.rs").write_bytes(Path("/home/hclau/ecdsa_research/rail-repair-20261015/diagnostic-rails-pre-y33-b3/src/point_add/observed_sim.rs").read_bytes())

def edit(path, needle, new, count=1):
    s = path.read_text()
    assert s.count(needle) == count, (path, needle, s.count(needle))
    path.write_text(s.replace(needle, new))

p = base / "mod.rs"
p.write_text("mod value_trace;\nmod observed_sim;\n" + p.read_text())
edit(p, "        circ.y33_clears();", "        value_trace::run(circ.rail_observation_ops());\n        circ.y33_clears();")
edit(base / "builder.rs", "    pub(crate) fn y33_clears(&mut self) {",
     "    pub(crate) fn rail_observation_ops(&self) -> &[Op] { &self.ops }\n    pub(crate) fn y33_clears(&mut self) {")
p = base / "leapfrog.rs"
fwd = "fn fwd_tick(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {"
rev = "fn rev_tick(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {"
edit(p, fwd, fwd.replace("fwd_tick(", "fwd_tick_inner("))
edit(p, rev, rev.replace("rev_tick(", "rev_tick_inner("))
p.write_text(p.read_text() + "\n" + fwd + """
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::FwdBefore,&wk.r,&[],lowrel());
    fwd_tick_inner(c,wk,t,pay.as_deref_mut());
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::FwdAfter,&wk.r,wk.tape.last().unwrap(),lowrel());
}
""" + rev + """
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::RevBefore,&wk.r,&[],lowrel());
    rev_tick_inner(c,wk,t,pay.as_deref_mut());
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::RevAfter,&wk.r,&[],lowrel());
}
""")

# Packets: 186 deterministic value failures from the wide census, plus the independent256 control.
packets = root / "packets"
packets.mkdir()
if fails_tsv is None:
    rows = [json.loads(l) for l in (census / "results/wide-replay.jsonl").read_text().splitlines() if l.strip()]
    fails = [r for r in rows if r["value"]]
    assert len(fails) == 186, len(fails)
    text = "".join(f"{i} {r['px']} {r['py']} {r['ax']} {r['ay']} {r['exp_x']} {r['exp_y']}\n" for i, r in enumerate(fails))
else:
    text = fails_tsv.read_text()  # rows already "i px py ax ay ex ey"
    assert text.strip(), "empty failure list"
# The family name "valuefail186" is kept because value_trace.rs reads it; the row count may differ.
(packets / "valuefail186.tsv").write_text(text)
(packets / "independent.tsv").write_bytes(Path("/home/hclau/ecdsa_research/arithmetic-repair-20261015/packets/independent.tsv").read_bytes())

diff = subprocess.run(["diff", "-ruN", "-x", "target", "-x", "ops.bin", "-x", ".git", str(src / "src"), str(dest / "src")],
                      capture_output=True).stdout
(root / "observer.patch").write_bytes(diff)
manifest = {
    "source": str(src), "destination": str(dest), "qualified_score": None,
    "patch_sha256": hashlib.sha256(diff).hexdigest(),
    "packets": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(packets.iterdir())},
    "expected_final_stream": expected,
}
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print("prepared", manifest["patch_sha256"])
