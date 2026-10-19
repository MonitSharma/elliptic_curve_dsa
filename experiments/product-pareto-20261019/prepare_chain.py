"""Compose exact source-bound passes into an isolated native candidate.

Usage: prepare_chain.py NAME SOURCE_CHECKOUT MANIFEST_PREFIX [PREFIX...]
No statistical gate, nonce search, or submission is performed.
"""
import ctypes, ctypes.util, hashlib, json, shutil, struct, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parent
name,source,*prefixes=sys.argv[1:]
source=Path(source).resolve();candidate=root/('candidate-'+name)
assert not candidate.exists()
no=(1<<64)-1
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
z.ZSTD_decompress.restype=ctypes.c_size_t
def raw_stream(path):
    data=Path(path).read_bytes();assert data[:8]==b'QECCOPSZ'
    n=struct.unpack_from('<Q',data,8)[0];buf=ctypes.create_string_buffer(n*56)
    assert z.ZSTD_decompress(buf,n*56,data[16:],len(data)-16)==n*56
    return buf.raw
stages=[];receipts=[];previous_output=None
for prefix in prefixes:
    m=json.loads((root/(prefix+'.json')).read_text())
    p=Path(m['input']);p=p if p.is_absolute() else root/p
    raw=raw_stream(p);assert len(raw)==m['input_count']*56
    h=hashlib.sha3_256(raw).hexdigest();assert h==m['input_sha3_256']
    if previous_output is not None: assert h==previous_output,'Stage order/identity mismatch'
    assert m['peak_qubits']==1234
    tail=list(struct.iter_unpack('<7Q',raw[-96*56:]))
    for a,b in zip(tail[::2],tail[1::2]):
        assert a==b and a[0]==6 and a[3] in (0,1) and all(a[k]==no for k in (1,2,4,5,6))
    count=m['input_count']-96;digest=hashlib.sha3_256(raw[:count*56]).hexdigest()
    del raw
    deletes=list(m.get('zero_products',[]));replacements=[]
    for u in m.get('unwrappings',[]):
        deletes.extend([u['fill'],u['hmr'],u['phase']]);replacements.append([u['read']]+u['replacement'])
    linear=sorted((int(k),v) for k,v in m.get('linear_products',{}).items())
    assert all(i<count for i in deletes)
    assert all(r[0]<count for r in replacements)
    leases=m['leases'];assert all(s[0]<s[1]<count for s in leases)
    stages.append('Stage{count:%d,hash:"%s",scratch:%d,leases:&%s,deletes:&%s,linear:&%s,replacements:&%s}' %
        (count,digest,m['classical_bits'],json.dumps(leases),json.dumps(deletes),json.dumps(linear),json.dumps(replacements)))
    output=raw_stream(root/(prefix+'.ops.bin'));previous_output=hashlib.sha3_256(output).hexdigest();del output
    receipts.append({'prefix':prefix,'input_sha3_256':h,'output_sha3_256':previous_output,
                     'unwrappings':len(m.get('unwrappings',[])),'leases':len(leases),'zero':len(m.get('zero_products',[])),'linear':len(linear)})
module=r'''//! Exact source-bound copy removal and product retention. No arithmetic cuts.
use crate::circuit::{Op,OperationType as K,QubitId,BitId,RegisterId};
use sha3::{Digest,Sha3_256};
struct Stage{count:usize,hash:&'static str,scratch:u64,leases:&'static [[u64;9]],deletes:&'static [usize],linear:&'static [[u64;2]],replacements:&'static [[u64;8]]}
const STAGES:&[Stage]=&[__STAGES__];
fn hash(ops:&[Op])->String{let mut h=Sha3_256::new();for o in ops{h.update((o.kind as u64).to_le_bytes());for v in [o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}format!("{:x}",h.finalize())}
fn cx(q:u64,t:u64)->Op{let mut o=Op::empty();o.kind=K::CX;o.q_control1=QubitId(q);o.q_target=QubitId(t);o}
fn apply(ops:Vec<Op>,s:&Stage)->Vec<Op>{
 assert_eq!(ops.len(),s.count,"exact product input count");assert_eq!(hash(&ops),s.hash,"exact product input hash");
 let starts:std::collections::HashMap<_,_>=s.leases.iter().map(|s|(s[0] as usize,s)).collect();
 let ends:std::collections::HashMap<_,_>=s.leases.iter().map(|s|(s[1] as usize,s)).collect();
 let deletes:std::collections::HashSet<_>=s.deletes.iter().copied().collect();
 let linear:std::collections::HashMap<_,_>=s.linear.iter().map(|s|(s[0] as usize,s[1])).collect();
 let replacements:std::collections::HashMap<_,_>=s.replacements.iter().map(|s|(s[0] as usize,s)).collect();
 let mut out=Vec::with_capacity(ops.len()+3*s.leases.len());
 for(i,o)in ops.into_iter().enumerate(){
  if deletes.contains(&i){continue;}
  if let Some(r)=replacements.get(&i){assert_eq!(o.kind,K::CX);let kind=match r[1]{8=>K::CX,13=>K::CCX,_=>panic!("invalid moved product")};let x=Op{kind,q_control2:QubitId(r[2]),q_control1:QubitId(r[3]),q_target:QubitId(r[4]),c_target:BitId(r[5]),c_condition:BitId(r[6]),r_target:RegisterId(r[7])};x.validate();out.push(x);}
  else if let Some(&q)=linear.get(&i){assert_eq!(o.kind,K::CCX);assert!(q==o.q_control1.0||q==o.q_control2.0);let mut x=o;x.kind=K::CX;x.q_control2=QubitId(u64::MAX);x.q_control1=QubitId(q);x.validate();out.push(x);}
  else if let Some(r)=starts.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[r[3],r[4],r[5]]);let mut x=o;x.q_target=QubitId(r[2]);x.validate();out.push(x);out.push(cx(r[2],r[5]));}
  else if let Some(r)=ends.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[r[6],r[7],r[8]]);out.push(cx(r[2],r[8]));let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(r[2]);h.c_target=BitId(s.scratch);out.push(h);let mut z=Op::empty();z.kind=K::CZ;z.q_control1=QubitId(r[6]);z.q_target=QubitId(r[7]);z.c_condition=BitId(s.scratch);out.push(z);}
  else{out.push(o);}
 }out
}
pub(super) fn run(mut ops:Vec<Op>)->Vec<Op>{for stage in STAGES{ops=apply(ops,stage);}ops}
'''.replace('__STAGES__',',\n'.join(stages))
revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
subprocess.run(['git','-C',str(source),'worktree','add','--detach',str(candidate),revision],check=True)
shutil.copytree(source/'src/point_add',candidate/'src/point_add',dirs_exist_ok=True)
(candidate/'src/point_add/retained_product_pareto.rs').write_text(module)
mod=candidate/'src/point_add/mod.rs';text=mod.read_text();needle='    let nonce: u64 = required_env("TAIL_NONCE");'
assert text.count(needle)==1
mod.write_text(text.replace(needle,'    ops = retained_product_pareto::run(ops);\n'+needle)+'\nmod retained_product_pareto;\n')
changed=subprocess.check_output(['git','-C',str(candidate),'diff','--name-only'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed)
patch=subprocess.check_output(['git','-C',str(candidate),'diff','--binary']);(root/(name+'-tracked.patch')).write_bytes(patch)
(root/(name+'-retained_product_pareto.rs')).write_text(module)
receipt={'status':'NATIVE_SOURCE_PREPARED_NOT_TESTED','base_revision':revision,'candidate':str(candidate),'stages':receipts,
         'expected_output_sha3_256':previous_output,'module_sha256':hashlib.sha256(module.encode()).hexdigest(),
         'tracked_patch_sha256':hashlib.sha256(patch).hexdigest()}
(root/(name+'-native.json')).write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
