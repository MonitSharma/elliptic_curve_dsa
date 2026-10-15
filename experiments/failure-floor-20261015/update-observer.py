from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parent
assert (root/'run.exit').read_text().strip()=='0'
old=root/'superseded-reverse-tape';old.mkdir()
for name in ['generate.log','stream.sha256','binary.sha256','run.exit','run.pid','build.log','observer-tracked.patch']:
 p=root/name
 if p.exists():p.rename(old/name)
base=root/'observer-b3/src/point_add'
(old/'payload_trace.rs').write_bytes((base/'payload_trace.rs').read_bytes())
(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes())
p=base/'leapfrog.rs';s=p.read_text()
for name,end in [('pay_rev_tick','letter'),('n2_pay_rev_last','letter')]:
 start=s.rindex('fn '+name+'(');where=s.index('\n'+name+'_unobserved',start)
 s=s[:where]+f'\nsuper::payload_trace::set_letter(id,{end});'+s[where:]
start=s.rindex('fn rev_tick(');where=s.index('\nrev_tick_payload_unobserved',start)
s=s[:where]+'\nif let Some(id)=id{super::payload_trace::set_letter(id,&letter);}'+s[where:]
p.write_text(s)
manifest=json.loads((root/'manifest.json').read_text())
manifest['source_files']={str(p.relative_to(root/'observer-b3')):hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob('*') if p.is_file()}
manifest['observer_revision']='reverse tape sampled at entry'
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
