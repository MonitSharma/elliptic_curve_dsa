from pathlib import Path
import subprocess,json,hashlib,re
root=Path(__file__).resolve().parent
src=root.parent/'trace-value-20261015/observer-b3'
dst=root/'observer-b3'
assert not dst.exists()
rev=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],text=True).strip()
subprocess.run(['git','-C',str(root.parent/'toffoli'),'worktree','add','--detach',str(dst),rev],check=True)
files=subprocess.check_output(['git','-C',str(src),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()
for rel in files:
 assert rel.startswith('src/point_add/'),rel
 (dst/rel).parent.mkdir(parents=True,exist_ok=True)
 (dst/rel).write_bytes((src/rel).read_bytes())
base=dst/'src/point_add'
(base/'payload_trace.rs').write_bytes((root/'payload_trace.rs').read_bytes())
p=base/'mod.rs';s=p.read_text();s='mod payload_trace;\n'+s;s=s.replace('        value_trace::run(circ.rail_observation_ops());','        payload_trace::run(circ.rail_observation_ops());');p.write_text(s)
p=base/'leapfrog.rs';s=p.read_text()
for name,revflag in [('pay_fwd_tick','false'),('pay_rev_tick','true')]:
 sig=f'fn {name}(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {{'
 assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_unobserved'))
 s+=f'\n{sig}\nlet id=super::payload_trace::begin(c.op_count(),c.current_phase(),t,{revflag},p);\n{name}_unobserved(c,t,letter,p);\nsuper::payload_trace::end(id,c.op_count(),p,letter,false);\n}}\n'
for name,revflag in [('fwd_tick','false'),('rev_tick','true')]:
 sig=f'fn {name}(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {{'
 assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_payload_unobserved'))
 letter='wk.tape.last().unwrap()' if name=='fwd_tick' else '&letter'
 save='' if name=='fwd_tick' else 'let letter=wk.tape[t].clone();'
 s+=f'\n{sig}\n{save}\nlet id=pay.as_deref().map(|p|super::payload_trace::begin(c.op_count(),c.current_phase(),t,{revflag},p));\n{name}_payload_unobserved(c,wk,t,pay.as_deref_mut());\nif let Some(id)=id{{super::payload_trace::end(id,c.op_count(),pay.as_deref().unwrap(),{letter},false);}}\n}}\n'
# Terminal forward intentionally leaves the controlled rotation for the endpoint.
for name,signature,args,revflag,skip in [
 ('n2_pay_fwd_last','c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2], skip_rot: bool','c,letter,p,skip_rot','false','skip_rot'),
 ('n2_pay_rev_last','c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]','c,letter,p','true','false')]:
 sig=f'fn {name}({signature}) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_unobserved'))
 s+=f'\n{sig}\nlet id=super::payload_trace::begin(c.op_count(),c.current_phase(),rounds()-1,{revflag},p);\n{name}_unobserved({args});\nsuper::payload_trace::end(id,c.op_count(),p,letter,{skip});\n}}\n'
p.write_text(s)
pack=root/'packets';pack.mkdir()
lines=(root.parent/'trace-value-20261015/trace.log').read_text().splitlines()
ids=[int(re.search(r'shot=(\d+)',l)[1]) for l in lines if l.startswith('TRACE family=valuefail186 ') and 'events=0' in l]
assert len(ids)==31,len(ids)
allrows=(root.parent/'trace-value-20261015/packets/valuefail186.tsv').read_text().splitlines()
(pack/'floor31.tsv').write_text('\n'.join(allrows[i] for i in ids)+'\n')
(pack/'independent.tsv').write_bytes((root.parent/'trace-value-20261015/packets/independent.tsv').read_bytes())
patch=subprocess.check_output(['git','-C',str(dst),'diff','--binary'])
(root/'observer.patch').write_bytes(patch)
# Include untracked observer files in an independent source manifest too.
manifest={'base':rev,'source':str(src),'source_files':{str(p.relative_to(dst)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (dst/'src/point_add').rglob('*') if p.is_file()},'floor_parent_shots':ids,'qualified_score':None}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('prepared',len(ids),'floor failures')
