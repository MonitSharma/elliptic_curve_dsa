"""Adapt the admitted static loader, preserving A29 repair and original nonce ordering."""
import json,subprocess,sys
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'repair53-native-20261016';d.mkdir(exist_ok=True)
freeze=json.loads((r/'REPAIR53_FREEZE.json').read_text());prefix=freeze['prefix_manifest'];parent=freeze['repair_parent_prefix_manifest']
old=r.parent/'frozen-cache-table-20261016';source=(old/'prepare.py').read_text()
changes={
'root=Path(__file__).resolve().parent':f'root=Path({str(d)!r})',
"up=root.parent/'product-exact-20261015'":"up=root.parent",
"root.parent/'toffoli'":"up/'tip'",
'PRODUCT25_FREEZE.json':'REPAIR53_FREEZE.json',
"parent=up/'tip/ops.bin'":"parent=up/'repair-cache53-20261016/input-1cd3457b.bin'",
'pn-96==11630620':f"pn-96=={parent['pre_tail_ops']}",
'b200178da6b06e841e384f71c2562c54b1dec09e6ef0a1c44990d408dba4e2e2':parent['pre_tail_sha3_256'],
'fn-96==14142533':f"fn-96=={prefix['pre_tail_ops']}",
'24027e53f377f24195d290b5d343c519156cfa3ae45f64529def428a901f8480':prefix['pre_tail_sha3_256'],
'frozen_cache25':'frozen_cache_repair53',
"dest=tree/'src/point_add';shutil.copy2(compressed_path,":"dest=tree/'src/point_add';shutil.copytree(up/'repair-cache53-20261016/repair-point-add-source',dest,dirs_exist_ok=True);shutil.copy2(compressed_path,",
"'prepared_source_generation_speed_experiment_not_a_new_resource_candidate'":"'NATIVE_REPAIRED53_PORT_PREPARED_NOT_YET_VERIFIED'",
}
for a,b in changes.items():assert a in source,a;source=source.replace(a,b)
oldwrite="p.write_text(source.replace(needle,'    ops = frozen_cache_repair53::run(ops);\\n'+needle)+'\\nmod frozen_cache_repair53;\\n')"
newwrite="assert source.count('    ops = precision_family::run(ops);')==1\np.write_text(source.replace('    ops = precision_family::run(ops);','    ops = precision_family::run(ops);\\n    ops = frozen_cache_repair53::run_after_identity_tail(ops);')+'\\nmod frozen_cache_repair53;\\n')"
assert oldwrite in source;source=source.replace(oldwrite,newwrite)
oldadd="['git','-C',str(tree),'add','--intent-to-add','src/point_add/frozen_cache_repair53.rs','src/point_add/frozen_cache_repair53.bin']"
assert oldadd in source;source=source.replace(oldadd,"['git','-C',str(tree),'add','--intent-to-add','src/point_add']")
source=source.replace("'diff','HEAD','--','src/point_add'","'diff','--binary','HEAD','--','src/point_add'")
source=source.replace('Store exact pre-tail cache output; bind original pre-cache input prefix; retain original nonce construction after table. No packet-dependent content or gates changed.','Bind exact repaired prefix after original nonce and A29 construction; validate/split96-op identity tail, replace only prefix with frozen exact cache output, reappend identical tail. No packet content or gates changed.')
template=(old/'frozen_cache.rs.in').read_text().replace('frozen_cache25','frozen_cache_repair53')
wrapper='''
// A29 is intentionally retained at its original after-tail hook. Split only
// the admitted96-op identity suffix and reappend its exact existing bytes.
fn split_identity_tail(mut ops:Vec<Op>)->(Vec<Op>,Vec<Op>){
 let at=ops.len().checked_sub(96).expect("frozen cache full source lacks identity tail");let tail=ops.split_off(at);
 for pair in tail.chunks_exact(2){for o in pair{assert!(o.kind==K::X&&o.q_target.0<=1&&o.q_control1.0==u64::MAX&&o.q_control2.0==u64::MAX&&o.c_target.0==u64::MAX&&o.c_condition.0==u64::MAX&&o.r_target.0==u64::MAX,"frozen cache current identity tail shape");}assert_eq!(pair[0],pair[1],"frozen cache current paired tail");}
 (ops,tail)
}
pub(super) fn run_after_identity_tail(ops:Vec<Op>)->Vec<Op>{let(prefix,tail)=split_identity_tail(ops);let mut out=run(prefix);out.extend(tail);out}
#[cfg(test)]mod current_tail_tests{
 use super::*;
 fn full()->Vec<Op>{let mut p=Op::empty();p.kind=K::X;p.q_target=QubitId(0);let mut v=vec![p];for i in 0..48{let mut o=p;o.q_target=QubitId((i%2)as u64);v.extend([o,o]);}v}
 #[test]fn exact_tail_bytes_and_prefix_retained(){let original=full();let(p,t)=split_identity_tail(original.clone());assert_eq!(p,&original[..1]);assert_eq!(t,&original[1..]);let mut joined=p;joined.extend(t);assert_eq!(joined,original);}
 #[test]#[should_panic(expected="current paired tail")]fn nonidentity_pair_rejected(){let mut v=full();v[2].q_target=QubitId(1);split_identity_tail(v);}
 #[test]#[should_panic(expected="current identity tail shape")]fn conditional_suffix_rejected(){let mut v=full();v[1].c_condition=BitId(0);split_identity_tail(v);}
 #[test]#[should_panic(expected="current identity tail shape")]fn phase_gate_suffix_rejected(){let mut v=full();v[1].kind=K::Z;split_identity_tail(v);}
 #[test]#[should_panic(expected="full source lacks identity tail")]fn missing_suffix_rejected(){split_identity_tail(vec![]);}
}
'''
(d/'frozen_cache.rs.in').write_text(template+wrapper)
(d/'generated-prepare.py').write_text(source)
subprocess.run([sys.executable,str(d/'generated-prepare.py')],check=True)
