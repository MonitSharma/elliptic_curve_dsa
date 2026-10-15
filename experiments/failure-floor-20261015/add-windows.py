from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent;assert (root/'run.exit').read_text().strip()=='0'
old=root/'stage-observer';old.mkdir()
for name in ['generate.log','stream.sha256','binary.sha256','run.exit','run.pid','build.log','observer-tracked.patch','manifest.json']:
 p=root/name
 if p.exists():(old/name).write_bytes(p.read_bytes())
base=root/'observer-b3/src/point_add';(old/'payload_trace.rs').write_bytes((base/'payload_trace.rs').read_bytes());(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes())
p=base/'square.rs';s=p.read_text();start=s.index('fn window_add(');end=s.index('\n///',start);part=s[start:end];needle='    addsub_wide(circ, value, &out[shift..top], negate);';assert part.count(needle)==1;part=part.replace(needle,'    let observe_id=super::payload_trace::window_begin(circ.op_count(),negate,shift,value,out,None);\n'+needle+'\n    super::payload_trace::window_end(observe_id,circ.op_count());');s=s[:start]+part+s[end:]
start=s.index('fn wcin_windows(');end=s.index('\nfn wcin_finish(',start);part=s[start:end];needle='        let inv = negate ^ neg;';assert part.count(needle)==1;part=part.replace(needle,needle+'\n        let observe_id=super::payload_trace::window_begin(circ.op_count(),inv,shift,high,out,Some(c));')
needle='        if inv { circ.x_all(win); }';assert part.count(needle)==2;at=part.rindex(needle)+len(needle);part=part[:at]+'\n        super::payload_trace::window_end(observe_id,circ.op_count());'+part[at:];s=s[:start]+part+s[end:];p.write_text(s)
manifest=json.loads((root/'manifest.json').read_text());manifest['observer_revision']='fold internal wires and all payload kernels; stage boundaries; individual ordinary/merged square windows'
manifest['source_files']={str(p.relative_to(root/'observer-b3')):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()};(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
