from pathlib import Path
import hashlib,json,shutil
a=Path(__file__).resolve().parent;ex=a.parent;old=ex/'breakthrough-global-quantum-alias-v3-20261021';r=ex/'breakthrough-reset-reference-inventory-20261021';r.mkdir(exist_ok=False);t=r/'local-tool';t.mkdir()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
f=json.loads((old/'SOURCE-FREEZE.json').read_bytes());assert all(sha(old/'local-tool'/p)==h for p,h in f['tool_source_files'].items())
for n in ['Cargo.toml','Cargo.lock','io.rs']:shutil.copyfile(old/'local-tool'/n,t/n)
p=t/'Cargo.toml';p.write_text(p.read_text().replace('name = "global_quantum_alias"','name = "reset_reference_inventory"'))
s=(old/'local-tool/discover.rs').read_text();s=s.replace('let mut counts=BTreeMap::<&str,usize>::new();','let mut counts=BTreeMap::<&str,usize>::new();let mut reset_refs=vec![];')
needle='let fb=alg.and(&eff,&q[b]);'
assert s.count(needle)==1
inventory='''
   if flip!=0{
    let post=alg.xor(&q[t],&flip);let masked=alg.and(&eff,&post);let mut reference=None;
    if masked==0{reference=Some(("constant",0usize,false));}else if masked==eff{reference=Some(("constant",1usize,false));}
    if reference.is_none(){for(value,negative)in[(post,false),(post^1,true),(masked,false),(masked^eff,true)]{if value<=1{continue;}if let Some(wires)=qindex.get(&value){for &wire in wires{if wire==t{continue;}let desired=if negative{q[wire]^1}else{q[wire]};if alg.and(&eff,&desired)==masked{reference=Some(("quantum",wire,negative));break;}}}if reference.is_some(){break;}}}
    if reference.is_none(){for(value,negative)in[(post,false),(post^1,true),(masked,false),(masked^eff,true)]{if value<=1{continue;}if let Some(bits)=index.get(&value){for &bit in bits{let desired=if negative{c[bit]^1}else{c[bit]};if alg.and(&eff,&desired)==masked{reference=Some(("classical",bit,negative));break;}}}if reference.is_some(){break;}}}
    if let Some((kind,reference,negative))=reference{reset_refs.push(serde_json::json!({"operation":i,"target":t,"control1":a,"control2":b,"reference_kind":kind,"reference":reference,"complement":negative,"effective_guard_expression":eff,"masked_post_expression":masked}));}
   }
'''
s=s.replace(needle,needle+inventory).replace('"rewrites":counts,','"rewrites":counts,"reset_reference_inventory":reset_refs,')
start=s.index('fn main(');end=s.index('\n',start)
main='''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),3);let ops=io::load_ops(&a[1]);let(_,stats)=global_prefix_simplify(&ops,1024);let r=serde_json::json!({"status":"READ_ONLY_EXACT_RESET_REFERENCE_INVENTORY_NOT_A_CIRCUIT_OR_SCORE","input_records_sha3":hash(&ops),"proof":stats});std::fs::write(format!("{}.json",a[2]),serde_json::to_string_pretty(&r).unwrap()+"\\n").unwrap();}'''
s=s[:start]+main+s[end:]
s+='''
#[cfg(test)]mod reset_inventory_tests{
 use super::*;use quantum_ecc::circuit::RegisterId;
 fn fixture()->Vec<Op>{let n=u64::MAX;let mut ops=vec![];for q in[0,1]{let mut o=Op::empty();o.kind=K::AppendToRegister;o.q_target=QubitId(q);o.r_target=RegisterId(0);ops.push(o);}ops.extend([make(K::CX,n,0,1,n,n),make(K::CX,n,0,2,n,n),make(K::CCX,2,1,0,n,n),make(K::CCX,2,1,0,n,n)]);ops}
 #[test]fn inverse_majority_restores_a_live_reference(){let ops=fixture();let(_,r)=global_prefix_simplify(&ops,1024);assert!(r["reset_reference_inventory"].as_array().unwrap().iter().any(|x|x["operation"]==5&&x["reference_kind"]=="quantum"&&x["reference"]==2&&x["complement"]==false));}
 #[test]fn exact_and_uncompute_has_zero_post_target(){let n=u64::MAX;let mut ops=fixture();ops.truncate(2);ops.extend([make(K::CCX,0,1,2,n,n),make(K::CCX,0,1,2,n,n)]);let(_,r)=global_prefix_simplify(&ops,1024);assert!(r["reset_reference_inventory"].as_array().unwrap().iter().any(|x|x["operation"]==3&&x["reference_kind"]=="constant"&&x["reference"]==0));}
 #[test]fn arbitrary_input_self_reference_is_excluded(){let mut ops=fixture();ops.truncate(2);let n=u64::MAX;ops.push(make(K::CCX,0,1,2,n,n));let(_,r)=global_prefix_simplify(&ops,1024);assert!(r["reset_reference_inventory"].as_array().unwrap().is_empty());}
}
'''
(t/'discover.rs').write_text(s);(r/'discover.rs').write_text(s)
paths={'public1829':ex/'breakthrough-public1829-width-port-local-v4-20261020/public/ops.bin','compact1233':ex/'breakthrough-compact-context-alias-20261021/cap1233-r012.ops.bin','compact1234':ex/'breakthrough-compact-context-alias-20261021/cap1234-t21.ops.bin','official_ffe20':old/'official-ffe20.ops.bin'}
f.update(tool_source_files={n:sha(t/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']},input_streams={n:sha(p)for n,p in paths.items()},native_controls=18,scope='Read-only full-prefix inventory: exact post-CCX target under original effective guard equals constant, current other quantum wire or current classical bit/complement. All source HMR words symbolic; no sampled fingerprints. Three new inverse-MAJ/AND-uncompute/self-alias controls plus fifteen inherited exact-algebra controls. No replacement emitted, no new measurement, point inputs, gate, nonce, benchmark or score. IDs local to this expression graph only.')
(r/'SOURCE-FREEZE.json').write_text(json.dumps(f,indent=2)+'\n')
runner='''import hashlib,json,resource,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert all(sha(r/'local-tool'/p)==h for p,h in f['tool_source_files'].items());deps=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-protected';assert all(sha(deps/p)==h for p,h in f['protected_files'].items());exe=r.parent/'breakthrough-value-guard-fusion-audit-20261020/local-tool/target/release/reset_reference_inventory'
paths=PATHS;rows={}
def limits():resource.setrlimit(resource.RLIMIT_AS,(6*1024**3,6*1024**3));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
for n,p in paths.items():
 p=Path(p);assert sha(p)==f['input_streams'][n];start=time.monotonic()
 with(r/(n+'.log')).open('xb')as log:
  job=subprocess.Popen(['timeout','900',str(exe),str(p),str(r/n)],stdout=log,stderr=subprocess.STDOUT,preexec_fn=limits);(r/(n+'.pid')).write_text(str(job.pid)+'\\n');rc=job.wait()
 (r/(n+'.exit')).write_text(str(rc)+'\\n');row={'exit':rc,'seconds':time.monotonic()-start}
 if rc==0:
  data=json.loads((r/(n+'.json')).read_bytes());hits=data['proof']['reset_reference_inventory'];row.update(total=len(hits),by_kind={k:sum(h['reference_kind']==k for h in hits)for k in ['constant','quantum','classical']},report_sha256=sha(r/(n+'.json')))
 rows[n]=row;(r/'PROGRESS.json').write_text(json.dumps(rows,indent=2)+'\\n')
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_RESET_REFERENCE_INVENTORY_COMPLETE','cases':rows,'native_controls':18,'binary_sha256':sha(exe),'scope':f['scope']},indent=2)+'\\n')
'''
wsl=lambda p:'/mnt/c/'+str(p.resolve())[3:].replace('\\','/')
runner=runner.replace('PATHS',repr({n:wsl(p)for n,p in paths.items()}));(r/'run.py').write_text(runner)
s=(old/'run-local.sh').read_text().replace(old.name,r.name).replace('--bin global_quantum_alias','--bin reset_reference_inventory').replace('15 passed;','18 passed;');(r/'run-local.sh').write_bytes(s.encode())
(r/'PLAN.md').write_text(f['scope']+'\n');(r/'.gitignore').write_text('local-tool/\n__pycache__/\n');(r/'.gitattributes').write_text('* -text\n');print(r.name)
