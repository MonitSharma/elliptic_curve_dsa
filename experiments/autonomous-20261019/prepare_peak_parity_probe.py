"""Inspect exact conservative ANF relations at the first complete-width state."""
from pathlib import Path
import hashlib,json,shutil
ws=Path(__file__).resolve().parent.parent;r=ws/'product-peak-parity-probe-20261020';assert not r.exists();r.mkdir();old=ws/'product-anf-witness-20261019'
meta=json.loads((ws/'product-clean-lease-probe-20261020/probe.json').read_text())['lease_probe'];point=meta['first_full_width_post_state'];epoch=next(x for x in meta['epochs'] if x['first']<=point<=x['last_proved_clean'])
assert point==1444755
for p in old.glob('*.rs'):shutil.copy2(p,r/p.name)
s=(r/'anf.rs').read_text();a=s.index('fn main(){');b=s.index('#[cfg(test)]mod tests{',a)
main='''fn prefix_with_abi(v:&[Op],through:usize)->Vec<Op>{let mut out=v[..=through].to_vec();out.extend(v.iter().filter(|o|o.kind==K::AppendToRegister).copied());out}
fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let whole=io::load_ops(&a[1]);assert_eq!(hash(&whole),a[3]);let config:serde_json::Value=serde_json::from_str(&std::fs::read_to_string("BINDING.json").unwrap()).unwrap();let through=config["point"].as_u64().unwrap()as usize;let start=config["epoch_first"].as_u64().unwrap()as usize;let end=config["epoch_last"].as_u64().unwrap()as usize;let touched:BTreeSet<_>=whole[start..=end].iter().flat_map(|o|[o.q_control1.0,o.q_control2.0,o.q_target.0]).filter(|&q|q!=NO).collect();let abi:BTreeSet<_>=whole.iter().filter(|o|o.kind==K::AppendToRegister&&o.q_target.0!=NO).map(|o|o.q_target.0).collect();let v=prefix_with_abi(&whole,through);let mut alg=Algebra{next:1,cap:256,degree:12,cuts:0};let(out,sites)=scan_with_witness(&v,&mut alg,false);let report=serde_json::json!({"status":"PREFIX_ABI_AND_ABSTRACT_STATE_CONTROL_NOT_A_CIRCUIT","full_input_raw_sha3_256":a[3],"point":through,"prefix_with_global_ABI_sha3_256":hash(&v),"output_prefix_sha3_256":hash(&out),"cuts":alg.cuts,"next_atom":alg.next,"sites":sites,"epoch_touched_roles":touched,"ABI_roles":abi});std::fs::write(&a[2],serde_json::to_string_pretty(&report).unwrap()).unwrap();}
'''
base=s[:a]+main+s[b:]
extra='''
#[cfg(test)]mod prefix_tests{use super::*;#[test]fn late_global_ABI_is_not_assumed_clean_in_prefix(){let mut x=Op::empty();x.kind=K::X;x.q_target.0=1;let mut cc=Op::empty();cc.kind=K::CCX;cc.q_control1.0=3;cc.q_control2.0=1;cc.q_target.0=2;let mut qr=Op::empty();qr.kind=K::AppendToRegister;qr.q_target.0=3;qr.r_target.0=0;let v=prefix_with_abi(&[x,cc,qr],1);let(out,_)=scan_with_witness(&v,&mut Algebra{next:1,cap:256,degree:12,cuts:0},false);assert_eq!(out[1].kind,K::CX);assert_eq!(out[1].q_control1.0,3);}}
'''
base+=extra;(r/'base.rs').write_text(base,newline='\n');(r/'anf.rs').unlink()
probe=base
needle='for(i,o)in v.iter().enumerate(){';assert probe.count(needle)==1
probe=probe.replace(needle,'let snapshots=std::env::var("ANF_SNAPSHOT_BASE").ok();let point=1444755usize;\n '+needle)
needle='if i%1_000_000==0{eprintln!';assert probe.count(needle)==1
probe=probe.replace(needle,'''if let Some(prefix)=&snapshots{if i==point-1||i==point{let data=serde_json::json!({"after_source_op":i,"q":q,"next_atom":alg.next,"cuts":alg.cuts,"scope":"Conservative universal ANF state with arbitrary global ABI inputs, not sampled bit values."});std::fs::write(format!("{prefix}-{i}.json"),serde_json::to_string(&data).unwrap()).unwrap();}}
  '''+needle)
(r/'probe.rs').write_text(probe,newline='\n')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
binding=json.loads((ws/'product-lease-footprint-20261020/BINDING.json').read_text());binding.update({'source_files':{p.name:sha(p) for p in r.glob('*.rs')},'point':point,'epoch_first':epoch['first'],'epoch_last':epoch['last_proved_clean'],'original_clean_probe_sha256':sha(ws/'product-clean-lease-probe-20261020/probe.json'),'scope':'First complete-width state chosen solely from proved-clean footprint, two fixed adjacent snapshots. No circuit/gate/nonce/score.'})
(r/'BINDING.json').write_text(json.dumps(binding,indent=2)+'\n')
driver=(ws/'product-linear-witness-controls-v2-20261020/evidence/run.py').read_text();cut=driver.index("with (r/'build-tests.log')");driver=driver[:cut]+'''for source in ['base','probe']:
 with (r/('build-tests-'+source+'.log')).open('xb') as f:subprocess.run(args+['--test',source+'.rs','-o',source+'-tests.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
 with (r/('tests-'+source+'.log')).open('xb') as f:subprocess.run(['./'+source+'-tests.bin','--test-threads=1'],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert '17 passed; 0 failed' in (r/('tests-'+source+'.log')).read_text()
 with (r/('build-'+source+'.log')).open('xb') as f:subprocess.run(args+[source+'.rs','-o',source+'.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
inp=ws/'product-copy-cache-native-20261020/candidate/ops.bin';assert sha(inp)==b['input_compressed_sha256']
for source in ['base','probe']:
 env=dict(os.environ);env.pop('ANF_SNAPSHOT_BASE',None)
 if source=='probe':env['ANF_SNAPSHOT_BASE']=str(r/'snapshot')
 with (r/(source+'.log')).open('xb') as f:subprocess.run(['/usr/bin/time','-v','./'+source+'.bin',str(inp),str(r/(source+'.json')),b['input_raw_sha3_256']],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
assert (r/'base.json').read_bytes()==(r/'probe.json').read_bytes(),'Every prefix hash, site/cut/atom counter and ABI field must match'
subprocess.run(['python3',str(r/'rank.py')],check=True)
'''
(r/'run.py').write_text(driver,newline='\n')
(r/'rank.py').write_text('''import hashlib,json
from pathlib import Path
r=Path(__file__).resolve().parent;meta=json.loads((r/'probe.json').read_text());b=json.loads((r/'BINDING.json').read_text());results=[]
for point in [b['point']-1,b['point']]:
 p=r/f'snapshot-{point}.json';snap=json.loads(p.read_text());q=snap['q'];terms=sorted({tuple(m) for poly in q for m in poly if m});column={m:i for i,m in enumerate(terms)};basis={};relations=[]
 for wire,poly in enumerate(q):
  if wire==len(q)-1:continue
  mask=sum(1<<column[tuple(m)] for m in poly if m);support=1<<wire;constant=[] in poly
  while mask:
   pivot=mask.bit_length()-1
   if pivot not in basis:basis[pivot]=(mask,support,constant);break
   other,provenance,c=basis[pivot];mask^=other;support^=provenance;constant^=c
  if not mask:
   wires=[i for i in range(len(q)) if support>>i&1];actual=set()
   for w in wires:actual.symmetric_difference_update(tuple(m) for m in q[w])
   assert actual==({()} if constant else set())
   quiet=not any(w in meta['epoch_touched_roles'] for w in wires)
   donors=[w for w in wires if w not in meta['ABI_roles'] and w!=len(q)-1] if quiet else []
   relations.append({'wires':wires,'constant':constant,'all_wires_untouched_in_epoch':quiet,'nonABI_donors':donors})
 results.append({'after_source_op':point,'qubit_roles':len(q),'non_high_rows':len(q)-1,'monomials':len(terms),'rank':len(basis),'linear_relations':len(relations),'quiet_held_relations':sum(bool(x['nonABI_donors']) for x in relations),'relations':relations,'snapshot_sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()})
(r/'RESULT.json').write_text(json.dumps({'status':'EXACT_CONSERVATIVE_PEAK_ANF_RANK_DIAGNOSTIC_COMPLETED','prefix_baseline_all_fields_and_hashes_equal':True,'base_tests':17,'probe_tests':17,'fixed_epoch':[b['epoch_first'],b['epoch_last']],'states':results,'scope':'Exact rank of conservative ANF abstraction, not a quantum width lower bound, lease, native candidate, census, nonce or score.'},indent=2)+'\\n');print(json.dumps([{k:v for k,v in x.items() if k!='relations'} for x in results],indent=2),flush=True)
''',newline='\n')
for name in ['run.sh','launch.py']:(r/name).write_text((ws/'product-lease-footprint-20261020'/name).read_text().replace('product-lease-footprint-20261020','product-peak-parity-probe-20261020'),newline='\n')
(r/'.gitignore').write_text('/*.bin\n')
(r/'STATUS.md').write_text('''# Exact ANF parity at the first complete-width state

Declared before launch. Static point1444755 selected from the finished strong
clean-boundary probe on frozen cache input, not from any sampled input/nonce.
Compare unchanged baseline and read-only snapshot copies: prefix hashes, all
sites/atom/cut counters, global ABI metadata all equal. Include every global
ABI annotation before interpreting a prefix; late input annotations must never
be assumed clean.17 tests per copy before execution. Fixed cap256/degree12.
Independent unbounded integer GF2 elimination on the two saved states before/
after the peak checks every discovered relation by raw polynomial symmetric
difference. Exclude high wire and seek non-ABI donors whose ENTIRE relation is
untouched during the fixed epoch. Exact rank here concerns a conservative
abstraction, not physical-width optimality. No lease/circuit/gate/nonce/score.
One server CPU/12GiB, global resource check before pinning actual work.
''')
print('Prepared fixed first-peak universal ANF snapshots and independent parity diagnostic; no launch')
