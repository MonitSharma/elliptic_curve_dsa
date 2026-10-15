from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='0'
old=root/'transition-observer';old.mkdir()
for name in ['generate.log','stream.sha256','binary.sha256','run.exit','run.pid','build.log','observer-tracked.patch','manifest.json']:
 p=root/name
 if p.exists():(old/name).write_bytes(p.read_bytes())
base=root/'observer-b3/src/point_add'
(old/'payload_trace.rs').write_bytes((base/'payload_trace.rs').read_bytes())
(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes())
p=base/'y15_onefold.rs';s=p.read_text();start=s.index('fn fold_fwd_v2(');end=s.index('\n/// The borrow',start);part=s[start:end]
needle='    let mw = acc.len();';assert part.count(needle)==1;part=part.replace(needle,needle+'\n    let observe_id=super::super::payload_trace::fold_begin(c.op_count(),acc,e,nm,k1,k2);')
needle='    plan\n}';assert part.count(needle)==1;part=part.replace(needle,'    super::super::payload_trace::fold_end(observe_id,c.op_count());\n'+needle)
s=s[:start]+part+s[end:];p.write_text(s)
manifest=json.loads((root/'manifest.json').read_text());manifest['observer_revision']='direct forward-fold entry and exit wires plus saved reverse tape'
manifest['source_files']={str(p.relative_to(root/'observer-b3')):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
