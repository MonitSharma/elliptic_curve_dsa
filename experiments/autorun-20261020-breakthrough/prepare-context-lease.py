"""Declare a genuinely new exact proof context, never accept by fingerprints."""
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=root/'experiments/breakthrough-context-lease-20261020';r.mkdir(exist_ok=False)
(r/'.gitattributes').write_text('* -text\n');(r/'.gitignore').write_text('tool/\n__pycache__/\n*resource-preflight*\nevidence.tar.gz\n')
(r/'PLAN.md').write_text('''# Exact context extension after official T750911

Input is the frozen official a4ee circuit, local final stream54c8cd60. Existing
arbitrary-cut equality starts exactly at the first reused product, losing earlier
relations between its inputs. Extend the cut backwards at most4096 operations,
within the SAME lexical outer condition scope. Start with arbitrary independent
quantum/classical values at that earlier cut; execute identical full exact value
semantics, capture the first effective product just before its producer, and
require exact equality with the second effective product. Unknown functions
stay unknown; cap overflow loses knowledge conservatively. Fingerprints nominate
only. Old exact proof, donor cleanliness/nonoverlap and phase rewrite unchanged.

The common outer predicate can be cofactored true because both endpoint ops are
in the same lexical scope; false skips both while donor stays zero. Never cross
its opening PushCondition during cut extension. Internal guards and measurements
are symbolically executed in original order; the two comparison points must have
empty relative guard stack. The prefix is unchanged, so any proved value relation
holds regardless of its incoming phase. Native basis/measurement/guard controls
and deliberate relation/phase faults precede the full scan. Donor budget16 is a
capacity bound, not scored width. Any component saving needs full final source,
fresh public comparison, its own declared final gate, nonce qualification and
unchanged benchmark. No final census, challenge packet or nonce screening here.
''')
(r/'context-tests.rs').write_text('''
#[cfg(test)]mod context_tests{
 use super::*;use quantum_ecc::circuit::RegisterId;use quantum_ecc::sim::Simulator;use sha3::digest::XofReader;
 struct Fixed(u8);impl XofReader for Fixed{fn read(&mut self,out:&mut[u8]){out.fill(self.0);}}
 fn fixture(outer:bool,inner:bool)->(Vec<Op>,usize,usize){let n=u64::MAX;let mut ops=vec![];for q in 0..5{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(0);o.q_target=QubitId(q);ops.push(o);}for b in 0..2{let mut o=Op::empty();o.kind=K::AppendToRegister;o.r_target=RegisterId(1);o.c_target=BitId(b);ops.push(o);}ops.push(make(K::R,n,n,5,n,n));if outer{ops.push(make(K::PushCondition,n,n,n,n,0));}ops.push(make(K::R,n,n,2,n,n));ops.push(make(K::CX,n,0,2,n,n));let first=ops.len();ops.push(make(K::CCX,0,1,3,n,if inner{1}else{n}));ops.push(make(K::X,n,n,4,n,n));let last=ops.len();ops.push(make(K::CCX,2,1,4,n,if inner{1}else{n}));if outer{ops.push(make(K::PopCondition,n,n,n,n,n));}(ops,first,last)}
 #[test]fn context_proves_prepared_alias_but_rejects_broken_relation(){for outer in[false,true]{for inner in[false,true]{let(mut ops,first,last)=fixture(outer,inner);assert!(!local_proof(&ops,first,last,6,2));assert!(context_proof(&ops,first,last,6,2));ops[first-1].q_control1=QubitId(1);assert!(!context_proof(&ops,first,last,6,2));}}}
 #[test]fn context_never_crosses_enclosing_scope_or_unbalanced_guard(){let n=u64::MAX;let ops=vec![make(K::R,n,n,2,n,n),make(K::CX,n,0,2,n,n),make(K::PushCondition,n,n,n,n,0),make(K::CCX,0,1,3,n,n),make(K::CCX,2,1,4,n,n),make(K::PopCondition,n,n,n,n,n)];assert_eq!(context_start(&ops,3),3);assert!(!context_proof(&ops,3,4,6,1));let bad=vec![make(K::CCX,0,1,2,n,n),make(K::PopCondition,n,n,n,n,n),make(K::CCX,0,1,3,n,n)];assert!(!context_proof(&bad,0,2,4,0));}
 #[test]fn context_lease_preserves_full_basis_phase_guards_and_cost_detects_missing_phase(){let mut caught=0;for outer in[false,true]{for inner in[false,true]{let(ops,first,last)=fixture(outer,inner);assert!(context_proof(&ops,first,last,6,2));let f=ops[first];let l=ops[last];let lease=[first as u64,last as u64,5,f.q_control2.0,f.q_control1.0,f.q_target.0,l.q_control2.0,l.q_control1.0,l.q_target.0];let out=rewrite_ops(ops.clone(),&[lease],2);let faulty:Vec<_>=out.iter().filter(|o|o.kind!=K::CZ).copied().collect();for pattern in[0u8,255,0xa5,0x5a]{for high in[false,true]{let mut ra=Fixed(pattern);let mut rb=Fixed(pattern);let mut rf=Fixed(pattern);let mut a=Simulator::new(6,3,&mut ra);let mut b=Simulator::new(6,3,&mut rb);let mut bad=Simulator::new(6,3,&mut rf);for lane in 0..64{for q in 0..5{a.qubits[q]|=((lane>>q&1)as u64)<<lane;}a.bits[0]|=((lane>>5&1)as u64)<<lane;a.bits[1]|=((if high{lane^0b10101}else{lane}>>4&1)as u64)<<lane;}b.qubits.clone_from(&a.qubits);bad.qubits.clone_from(&a.qubits);b.bits.clone_from(&a.bits);bad.bits.clone_from(&a.bits);let eff=(if outer{a.bits[0]}else{u64::MAX})&(if inner{a.bits[1]}else{u64::MAX});a.apply_iter(ops.iter());b.apply_iter(out.iter());bad.apply_iter(faulty.iter());assert_eq!(a.qubits,b.qubits);assert_eq!(a.bits[..2],b.bits[..2]);assert_eq!(a.phase,b.phase);assert_eq!(a.stats.toffoli_gates-b.stats.toffoli_gates,eff.count_ones()as u64);assert_eq!(b.qubits[5],0);caught+=u64::from(a.phase!=bad.phase);}}}}assert!(caught>0);}
}
''')
(r/'prepare.py').write_text("""import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'breakthrough-public140-cache-20261020';t=r/'tool';parent=ws/'breakthrough-public322-square-final-20261020';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text());pf=json.loads((parent/'SOURCE-FREEZE.json').read_text());assert all(sha(old/'tool'/p)==h for p,h in f['tool_source_files'].items());assert not t.exists();assert sha(parent/'candidate/ops.bin')=='54c8cd60337d1afaa36ff37ae0b29f321838df707350704def8a02e3e8716e69';assert all(sha(parent/'candidate'/p)==h for p,h in{**pf['source_files'],**pf['protected_files']}.items());t.mkdir()
for name in['Cargo.toml','Cargo.lock','discover.rs','io.rs']:shutil.copyfile(old/'tool'/name,t/name)
subprocess.run(['cp','-a','--reflink=auto',str(old/'tool/target'),str(t/'target')],check=True);p=t/'discover.rs';source=p.read_text();start=source.index('fn local_proof(');end=source.index('fn tri_and(',start);original=source[start:end];new=original.replace('fn local_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool','fn exact_proof_from(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize,start:usize)->bool');a='let f=ops[first];let product=alg.and(&q[f.q_control1.0 as usize],&q[f.q_control2.0 as usize]);let expected=if f.c_condition.0==no{product}else{alg.and(&product,&c[f.c_condition.0 as usize])};';assert new.count(a)==1;new=new.replace(a,'let mut expected=None;');a='for o in &ops[first..last]{';assert new.count(a)==1;new=new.replace(a,'for (i,o) in ops[start..last].iter().enumerate(){\\n  if start+i==first{if !stack.is_empty()||base!=vec![0]{return false;}let product=alg.and(&q[o.q_control1.0 as usize],&q[o.q_control2.0 as usize]);expected=Some(if o.c_condition.0==no{product}else{alg.and(&product,&c[o.c_condition.0 as usize])});}');new=new.replace('actual==expected','Some(actual)==expected');new+='''+
fn context_start(ops:&[Op],first:usize)->usize{
 let floor=first.saturating_sub(4096);let mut depth=0usize;let mut start=first;
 for i in(floor..first).rev(){match ops[i].kind{K::PopCondition=>depth+=1,K::PushCondition=>{if depth==0{break;}depth-=1;},_=>{}}if depth==0{start=i;}}
 start
}
fn context_proof(ops:&[Op],first:usize,last:usize,nq:usize,nb:usize)->bool{
 if local_proof(ops,first,last,nq,nb){return true;}
 let start=context_start(ops,first);start<first&&exact_proof_from(ops,first,last,nq,nb,start)
}
'''
assert source.count('if local_proof(&ops,first,i,nq,nb){')==1;source=source.replace('if local_proof(&ops,first,i,nq,nb){','if context_proof(&ops,first,i,nq,nb){');source=source[:end]+new+source[end:] if False else source.replace(original,original+new);source+='\\n'+(r/'context-tests.rs').read_text();assert 'fn exact_proof_from' in source;p.write_text(source);(r/'old-local-proof.rs').write_text(original);(r/'new-context-proof.rs').write_text(new);subprocess.run(['/home/hclau/.cargo/bin/cargo','+1.93.0','generate-lockfile','--offline'],cwd=t,check=True);deps=f['protected_dependency_files'];assert all(sha(Path(p))==h for p,h in deps.items());(r/'SOURCE-FREEZE.json').write_text(json.dumps({'tool_source_files':{p.name:sha(p)for p in t.iterdir()if p.is_file()},'protected_dependency_files':deps,'parent_final_source_freeze_sha256':sha(parent/'SOURCE-FREEZE.json'),'input':str(parent/'candidate/ops.bin'),'input_sha256':sha(parent/'candidate/ops.bin'),'context_lookback_operations':4096,'extra_donor_budget':16,'scope':'Earlier arbitrary cut in same lexical scope, exact equality only. Native tests/faults before component scan, no gate/nonce/score.'},indent=2)+'\\n')
""".replace("new+='''+", "new+='''"))
(r/'run.py').write_text('''import hashlib,json,os,re,subprocess,time
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'tool';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd,name,cwd=t,env=None):
 with(r/(name+'.log')).open('xb')as log:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT);(r/(name+'.pid')).write_text(str(p.pid)+'\\n');rc=p.wait()
 (r/(name+'.exit')).write_text(str(rc)+'\\n');assert rc==0,name
try:
 run(['python3','prepare.py'],'prepare',r);f=json.loads((r/'SOURCE-FREEZE.json').read_text());run(['/home/hclau/.cargo/bin/cargo','+1.93.0','test','--release','--bin','product_pareto_discover','--','--nocapture'],'tests');assert re.findall(r'test result: ok\\. (\\d+) passed; 0 failed;',(r/'tests.log').read_text())==['7'];run(['/home/hclau/.cargo/bin/cargo','+1.93.0','build','--release','--bin','product_pareto_discover'],'build');start=time.time();run(['timeout','3600',str(t/'target/release/product_pareto_discover'),f['input'],str(r/'context16')],'discover',env=dict(os.environ,RESEARCH_EXTRA_DONORS='16'));assert all(sha(t/p)==h for p,h in f['tool_source_files'].items());a=json.loads((r/'context16.json').read_text());result={'status':'EXACT_CONTEXT_LEASE_COMPONENT_NOT_SCORED','native_controls':7,'leases':len(a['leases']),'proposed':a['proposed'],'diagnostic_saving':a['depth_weight_saving_diagnostic'],'output_stream_sha256':sha(r/'context16.ops.bin'),'max_donor':max((x[2]for x in a['leases']),default=None),'seconds':time.time()-start,'source_freeze_sha256':sha(r/'SOURCE-FREEZE.json')};(r/'RESULT.json').write_text(json.dumps(result,indent=2)+'\\n');(r/'run.exit').write_text('0\\n');print(json.dumps(result),flush=True)
except BaseException:
 (r/'run.exit').write_text('1\\n');raise
''')
print(r)
