"""Port a source-bound exact discovery into src/point_add only.

No search, census, or submission occurs here. Refuses to overwrite a checkout.
"""
import ctypes
import ctypes.util
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

root = Path(__file__).resolve().parent
prefix = sys.argv[1]
source = Path(sys.argv[2]).resolve()
candidate = root / ('candidate-' + prefix)
assert not candidate.exists(), candidate
manifest = json.loads((root / (prefix + '.json')).read_text())
assert manifest['peak_qubits'] == 1234
assert manifest.get('leases') or manifest.get('zero_products') or manifest.get('linear_products')
data = Path(manifest['input']).read_bytes()
assert data[:8] == b'QECCOPSZ'
n = struct.unpack_from('<Q', data, 8)[0]
assert n == manifest['input_count']
z = ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p, ctypes.c_size_t]
z.ZSTD_decompress.restype = ctypes.c_size_t
buf = ctypes.create_string_buffer(n * 56)
assert z.ZSTD_decompress(buf, n * 56, data[16:], len(data)-16) == n * 56
raw = buf.raw
assert hashlib.sha3_256(raw).hexdigest() == manifest['input_sha3_256']
tail = list(struct.iter_unpack('<7Q', raw[-96*56:]))
no = (1 << 64)-1
for a,b in zip(tail[::2],tail[1::2]):
    assert a == b and a[0] == 6 and a[3] in (0,1)
    assert all(a[k] == no for k in (1,2,4,5,6))
count = n-96
digest = hashlib.sha3_256(raw[:count*56]).hexdigest()
revision = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
subprocess.run(['git','-C',str(source),'worktree','add','--detach',str(candidate),revision],check=True)
shutil.copytree(source/'src/point_add',candidate/'src/point_add',dirs_exist_ok=True)

leases = manifest['leases']
zero = manifest.get('zero_products',[])
linear = sorted((int(k),v) for k,v in manifest.get('linear_products',{}).items())
assert all(s[1] < count for s in leases)
assert all(i < count for i in zero) and all(i < count for i,_ in linear)
module = r'''//! Exact product rewrites discovered independently of benchmark inputs.
//! Full input binding; explicit classical conditions; no approximate cuts.
use crate::circuit::{Op,OperationType as K,QubitId,BitId};
use sha3::{Digest,Sha3_256};
const INPUT_COUNT:usize=__COUNT__;
const INPUT_SHA3:&str="__HASH__";
const SCRATCH_CT:u64=__SCRATCH__;
const LEASES:&[[u64;9]]=&__LEASES__;
const ZERO:&[usize]=&__ZERO__;
const LINEAR:&[[u64;2]]=&__LINEAR__;
fn hash(ops:&[Op])->String{
 let mut h=Sha3_256::new();for o in ops{h.update((o.kind as u64).to_le_bytes());
 for v in [o.q_control2.0,o.q_control1.0,o.q_target.0,o.c_target.0,o.c_condition.0,o.r_target.0]{h.update(v.to_le_bytes());}}format!("{:x}",h.finalize())
}
fn cx(q:u64,t:u64)->Op{let mut o=Op::empty();o.kind=K::CX;o.q_control1=QubitId(q);o.q_target=QubitId(t);o}
pub(super) fn run(ops:Vec<Op>)->Vec<Op>{
 assert_eq!(ops.len(),INPUT_COUNT,"exact product input count");
 assert_eq!(hash(&ops),INPUT_SHA3,"exact product input hash");
 let starts:std::collections::HashMap<_,_>=LEASES.iter().map(|s|(s[0] as usize,s)).collect();
 let ends:std::collections::HashMap<_,_>=LEASES.iter().map(|s|(s[1] as usize,s)).collect();
 let zero:std::collections::HashSet<_>=ZERO.iter().copied().collect();
 let linear:std::collections::HashMap<_,_>=LINEAR.iter().map(|s|(s[0] as usize,s[1])).collect();
 let mut out=Vec::with_capacity(ops.len()+3*LEASES.len());
 for (i,o) in ops.into_iter().enumerate(){
  if zero.contains(&i){assert_eq!(o.kind,K::CCX);continue;}
  if let Some(&q)=linear.get(&i){assert_eq!(o.kind,K::CCX);assert!(q==o.q_control1.0||q==o.q_control2.0);let mut x=o;x.kind=K::CX;x.q_control2=QubitId(u64::MAX);x.q_control1=QubitId(q);x.validate();out.push(x);}
  else if let Some(s)=starts.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[3],s[4],s[5]]);let mut x=o;x.q_target=QubitId(s[2]);x.validate();out.push(x);out.push(cx(s[2],s[5]));}
  else if let Some(s)=ends.get(&i){assert_eq!(o.kind,K::CCX);assert_eq!([o.q_control2.0,o.q_control1.0,o.q_target.0],[s[6],s[7],s[8]]);out.push(cx(s[2],s[8]));let mut h=Op::empty();h.kind=K::Hmr;h.q_target=QubitId(s[2]);h.c_target=BitId(SCRATCH_CT);out.push(h);let mut z=Op::empty();z.kind=K::CZ;z.q_control1=QubitId(s[6]);z.q_target=QubitId(s[7]);z.c_condition=BitId(SCRATCH_CT);out.push(z);}
  else{out.push(o);}
 }
 out
}
'''
for a,b in {
    '__COUNT__':str(count),'__HASH__':digest,'__SCRATCH__':str(manifest['classical_bits']),
    '__LEASES__':json.dumps(leases),'__ZERO__':json.dumps(zero),'__LINEAR__':json.dumps(linear)
}.items():
    module=module.replace(a,b)
(candidate/'src/point_add/retained_product_pareto.rs').write_text(module)
mod=candidate/'src/point_add/mod.rs'
text=mod.read_text()
needle='    let nonce: u64 = required_env("TAIL_NONCE");'
assert text.count(needle)==1
text=text.replace(needle,'    ops = retained_product_pareto::run(ops);\n'+needle)
mod.write_text(text+'\nmod retained_product_pareto;\n')
changed=subprocess.check_output(['git','-C',str(candidate),'diff','--name-only'],text=True).splitlines()
assert all(p.startswith('src/point_add/') for p in changed)
patch=subprocess.check_output(['git','-C',str(candidate),'diff','--binary'])
(root/(prefix+'-tracked.patch')).write_bytes(patch)
# Untracked module is separately preserved; git diff alone would omit it.
(root/(prefix+'-retained_product_pareto.rs')).write_text(module)
receipt={'status':'NATIVE_SOURCE_PREPARED_NOT_TESTED','base_revision':revision,
         'candidate':str(candidate),'input_count':count,'input_sha3_256':digest,
         'leases':len(leases),'zero_products':len(zero),'linear_products':len(linear),
         'source_module_sha256':hashlib.sha256(module.encode()).hexdigest(),
         'tracked_patch_sha256':hashlib.sha256(patch).hexdigest()}
(root/(prefix+'-native.json')).write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
