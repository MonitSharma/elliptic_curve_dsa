"""Find actual proved-clean highest-role epochs with an unchanged strong allocator."""
from pathlib import Path
import hashlib,json,shutil
ws=Path(__file__).resolve().parent.parent;r=ws/'product-clean-lease-probe-20261020';assert not r.exists();r.mkdir()
original=ws/'product-support-tight-20261019/tight_color.rs';s=original.read_text();a=s.index('fn main(){');b=s.index('#[cfg(test)]mod tests{',a)
main='''fn main(){let a:Vec<_>=std::env::args().collect();assert_eq!(a.len(),4);let mut v=io::load_ops(&a[1]);assert_eq!(hash(&v),a[3]);let tail=v.split_off(v.len()-96);for p in tail.chunks_exact(2){assert_eq!(p[0],p[1]);assert_eq!(p[0].kind,K::X);assert_eq!(p[0].c_condition.0,NO);}let(out,mut report)=color(&v);let mut out=out;out.extend(tail);report["input_full_sha3_256"]=serde_json::json!(a[3]);report["output_full_sha3_256"]=serde_json::json!(hash(&out));std::fs::write(&a[2],serde_json::to_string_pretty(&report).unwrap()).unwrap();}
'''
base=s[:a]+main+s[b:];(r/'base.rs').write_text(base,newline='\n');shutil.copy2(ws/'product-copy-cache-20261019/io.rs',r/'io.rs')
probe=base
needle='for(i,original)in v.iter().enumerate(){let mut o=*original;';assert probe.count(needle)==1
setup='''let high=nq-1;let high_enabled=!registered.contains(&(high as u64));let mut high_touches=vec![];let mut positions=vec![vec![];nq];for(i,o)in v.iter().enumerate(){let mut qs=[o.q_control1.0,o.q_control2.0,o.q_target.0];qs.sort_unstable();for(j,x)in qs.into_iter().enumerate(){if x!=NO&&(j==0||x!=qs[j-1]){positions[x as usize].push(i);}}}
 let mut high_epochs=vec![];let mut pending:Option<(usize,usize,Id)>=None;let mut first_full_state=None;
 '''
probe=probe.replace(needle,setup+needle)
needle='let touched:BTreeSet<_>=[o.q_control1.0,o.q_control2.0,o.q_target.0].into_iter().filter(|&x|x!=NO).collect();';assert probe.count(needle)==1
probe=probe.replace(needle,needle+'''
  if high_enabled&&touched.contains(&(high as u64)){high_touches.push(i);if pending.is_none(){assert!(q[high].is_no());pending=Some((i,stack.len(),eff));}}
''')
needle='if i%1_000_000==0{eprintln!';assert probe.count(needle)==1
record='''if first_full_state.is_none()&&nq-free.len()==nq{first_full_state=Some(i);}
  if high_enabled&&touched.contains(&(high as u64))&&q[high].is_no(){let(start,depth,guard)=pending.take().unwrap();let mut donor_count=0;let mut examples=vec![];
   for role in 0..nq{if role==high||registered.contains(&(role as u64)){continue;}let p=&positions[role];let at=p.partition_point(|&x|x<start);if at==p.len()||p[at]>i{donor_count+=1;if examples.len()<8{examples.push(role);}}}
   let touch_count=high_touches.partition_point(|&x|x<=i)-high_touches.partition_point(|&x|x<start);
   high_epochs.push(serde_json::json!({"first":start,"last_proved_clean":i,"touches":touch_count,"ops":i-start+1,"start_scope_depth":depth,"end_scope_depth":stack.len(),"first_guard_id":guard,"last_guard_id":eff,"untouched_nonABI_donor_count":donor_count,"first8_untouched_donors":examples}));
  }
  '''
probe=probe.replace(needle,record+needle)
needle='let result=serde_json::json!({"status":"TIGHT_GUARD_SUPPORT_LIFETIME_DIAGNOSTIC_NOT_A_SCORE",';assert probe.count(needle)==1
probe=probe.replace(needle,needle+'"lease_probe":{"highest_role":high,"enabled_nonABI":high_enabled,"touches":high_touches.len(),"first_full_width_post_state":first_full_state,"epochs":high_epochs,"trailing_unclosed":pending,"scope":"Read-only support boundaries and untouched-donor counts. Unknown donor values; no lease, new width or resource score."},')
probe+='''
#[cfg(test)]mod lease_tests{
 use super::*;use quantum_ecc::circuit::{BitId,QubitId};
 fn op(k:K,a:u64,b:u64,t:u64)->Op{let mut o=Op::empty();o.kind=k;o.q_control1=QubitId(a);o.q_control2=QubitId(b);o.q_target=QubitId(t);if k==K::Hmr{o.c_target=BitId(1);}o}
 fn input()->Op{let mut o=Op::empty();o.kind=K::AppendToRegister;o.c_target=BitId(0);o.r_target.0=0;o}
 #[test]fn conditional_writes_and_matching_reset_close_a_global_zero_epoch(){let mut x=op(K::X,NO,NO,4);x.c_condition=BitId(0);let mut h=op(K::Hmr,NO,NO,4);h.c_condition=BitId(0);let(_,r)=color(&[input(),x,h]);let p=&r["lease_probe"];assert_eq!(p["epochs"].as_array().unwrap().len(),1);assert!(p["trailing_unclosed"].is_null());assert_eq!(p["epochs"][0]["last_proved_clean"],2);}
 #[test]fn partial_reset_cannot_close_an_unconditionally_dirty_epoch(){let mut h=op(K::Hmr,NO,NO,4);h.c_condition=BitId(0);let(_,r)=color(&[input(),op(K::X,NO,NO,4),h]);assert!(r["lease_probe"]["epochs"].as_array().unwrap().is_empty());assert!(!r["lease_probe"]["trailing_unclosed"].is_null());}
 #[test]fn intervening_phase_touches_are_not_idle_donors(){let(_,r)=color(&[op(K::X,NO,NO,4),op(K::CCZ,1,2,3),op(K::R,NO,NO,4)]);let e=&r["lease_probe"]["epochs"][0];assert_eq!(e["untouched_nonABI_donor_count"],1);assert_eq!(e["first8_untouched_donors"],serde_json::json!([0]));}
}
'''
(r/'probe.rs').write_text(probe,newline='\n')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
old=json.loads((ws/'product-lease-footprint-20261020/BINDING.json').read_text())
(r/'BINDING.json').write_text(json.dumps({**old,'source_files':{p.name:sha(p) for p in r.glob('*.rs')},'original_allocator_source_sha256':sha(original),'scope':'Read-only semantic clean-epoch instrumentation; original source body/queries untouched, all old report fields and full output must match baseline.'},indent=2)+'\n')
driver=(ws/'product-linear-witness-controls-v2-20261020/evidence/run.py').read_text();cut=driver.index("with (r/'build-tests.log')");driver=driver[:cut]+'''for source,expected in [('base',12),('probe',15)]:
 with (r/('build-tests-'+source+'.log')).open('xb') as f:subprocess.run(args+['--test',source+'.rs','-o',source+'-tests.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
 with (r/('tests-'+source+'.log')).open('xb') as f:subprocess.run(['./'+source+'-tests.bin','--test-threads=1'],stdout=f,stderr=subprocess.STDOUT,check=True)
 assert str(expected)+' passed; 0 failed' in (r/('tests-'+source+'.log')).read_text()
 with (r/('build-'+source+'.log')).open('xb') as f:subprocess.run(args+[source+'.rs','-o',source+'.bin'],stdout=f,stderr=subprocess.STDOUT,check=True)
inp=ws/'product-copy-cache-native-20261020/candidate/ops.bin';assert sha(inp)==b['input_compressed_sha256']
for source in ['base','probe']:
 with (r/(source+'.log')).open('xb') as f:subprocess.run(['/usr/bin/time','-v','./'+source+'.bin',str(inp),str(r/(source+'.json')),b['input_raw_sha3_256']],stdout=f,stderr=subprocess.STDOUT,check=True)
base=json.loads((r/'base.json').read_text());probe=json.loads((r/'probe.json').read_text());extra=probe.pop('lease_probe');assert base==probe,'No original report/output/counter may change'
assert sha(inp)==b['input_compressed_sha256']
(r/'RESULT.json').write_text(json.dumps({'status':'READ_ONLY_STRONG_CLEAN_LEASE_BOUNDARIES_AND_COMPLETE_BASELINE_CONTROL_PASS','base_tests':12,'probe_tests':15,'all_prior_report_fields_and_complete_output_identical':True,'source_files':b['source_files'],'binary_hashes':{name:sha(r/(name+'.bin')) for name in ['base','probe']},'first_full_state':extra['first_full_width_post_state'],'epochs':len(extra['epochs']),'uncovered_high_touches':extra['touches']-sum(e['touches'] for e in extra['epochs']),'no_idle_donor_epochs':sum(e['untouched_nonABI_donor_count']==0 for e in extra['epochs']),'gate_or_nonce_or_score':False},indent=2)+'\\n');print((r/'RESULT.json').read_text(),flush=True)
'''
(r/'run.py').write_text(driver,newline='\n')
for name in ['run.sh','launch.py']:(r/name).write_text((ws/'product-lease-footprint-20261020'/name).read_text().replace('product-lease-footprint-20261020','product-clean-lease-probe-20261020'),newline='\n')
(r/'.gitignore').write_text('/*.bin\n')
(r/'STATUS.md').write_text('''# Strong proved-clean epochs for the highest quantum role

Declared before launch. New copy-cache input, existing exact strong support
semantics, fixed16-term/32-factor limits. Add only read-only metadata, with NO
new Boolean/abstraction queries. Require all12 old controls plus3 boundary
controls, identical whole output hash and every old report field on the same
complete input. Find every high-role interval ending in proved global zero,
including conditional resets; report all donor counts but only8 donor IDs.
This refines the lexical footprint's three multi-million-op intervals and
two trailing uses. It is NOT the old negative support-branch alias screen:
future leasing uncomputes/restores a held value and needs an independent
value identity. No alias, circuit rewrite, width result, gate or nonce here.
One server CPU/12GiB. Preserve original/failed sources and running jobs.
''')
print('Prepared strong clean-boundary metadata with complete baseline control; no launch')
