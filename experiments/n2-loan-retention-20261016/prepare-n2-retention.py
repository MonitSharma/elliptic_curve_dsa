from pathlib import Path
import json,hashlib,subprocess,datetime
r=Path('/home/hclau/ecdsa_research/n2-loan-retention-20261016');r.mkdir(exist_ok=True);source=r.parent/'product-exact-20261015/tip';d=r/'all-retained';rev='4b2ec52fc55da796aa8f5ef851290297e8706424'
assert not d.exists();assert subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()==rev
decl=dict(status='PREDECLARED SOURCE-ONLY RESOURCE AUDIT; NO SAMPLING',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_revision=rev,parent_actual_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',family='ALL n2_lend rails disabled at ALL source calls; hold all original rail bits throughout divide and multiply N2 payload batches',source_selection='structural function family; no tick/packet/input-dependent selection',remaining_clean_loan_premises='NONE: no N2 rail bit is lent',no_reset_discard=True,no_claim_full_arithmetic_correctness=True,no_fresh_census=True,no_table_or_allocator_anchor_bypass=True,source_only_metrics='raw source component Q/T/ABI only; native record qualification impossible unless every inherited check passes')
(r/'ALL-RETAINED-PREDECLARATION.json').write_text(json.dumps(decl,indent=2)+'\n')
subprocess.run(['git','-C',str(source),'worktree','add','--detach',str(d),rev],check=True);p=d/'src/point_add/leapfrog.rs';s=p.read_text();a=s.index('fn n2_lend(ri: usize) -> bool {');b=s.index('\n}',a)+2;s=s[:a]+'fn n2_lend(_ri: usize) -> bool { false }'+s[b:]
# Gate-inert local metrics surround the ENTIRE predeclared source family. All
# original build checks remain in place, and any rejection is terminal.
sig='fn n2_loan_out(c: &mut Builder, wk: &mut Walk, fault: bool) {';assert s.count(sig)==1;s=s.replace(sig,sig+'\n    super::n2_retention_metrics::begin(c, &wk.r);')
sig='fn n2_loan_in(c: &mut Builder, wk: &mut Walk, mul: bool) {';a=s.index(sig);b=s.index('\n}',a)+2;part=s[a:b];part=part[:-2]+'\n    super::n2_retention_metrics::end(c, &wk.r);\n}';s=s[:a]+part+s[b:];p.write_text(s)
p=d/'src/point_add/mod.rs';s='mod n2_retention_metrics;\n'+p.read_text();needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        n2_retention_metrics::complete(circ);\n'+needle);p.write_text(s)
trace='''use super::Builder;use crate::circuit::QubitId;use std::sync::Mutex;
static START:Mutex<Option<(usize,f64)>>=Mutex::new(None);
pub fn begin(c:&Builder,r:&[Vec<QubitId>;2]){*START.lock().unwrap()=Some((c.op_count(),c.expected_total()));eprintln!("N2_RETENTION_BEGIN phase={} at={} active={} peak={} dims={:?} rails={:?}",c.current_phase(),c.op_count(),c.active_qubits(),c.peak_total(),c.i13_dims(),r);}
pub fn end(c:&Builder,r:&[Vec<QubitId>;2]){let(at,t)=START.lock().unwrap().take().unwrap();eprintln!("N2_RETENTION_END phase={} begin={at} end={} source_expected_T_delta={} active={} peak={} dims={:?} rails={:?}",c.current_phase(),c.op_count(),c.expected_total()-t,c.active_qubits(),c.peak_total(),c.i13_dims(),r);}
pub fn complete(c:&Builder){eprintln!("N2_RETENTION_RAW_COMPLETE ops={} dims={:?} peak={} source_expected_T={} STATUS=COMPONENT_ONLY_ALL_ORIGINAL_CHECKS_FOLLOW",c.op_count(),c.i13_dims(),c.peak_total(),c.expected_total());}
'''
(d/'src/point_add/n2_retention_metrics.rs').write_text(trace)
(r/'all-retained.patch').write_bytes(subprocess.check_output(['git','-C',str(d),'diff','--binary']))
(r/'all-retained-source.json').write_text(json.dumps(dict(source_revision=rev,files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(d/'src/point_add').rglob('*')if p.is_file()},new_untracked_helper='src/point_add/n2_retention_metrics.rs'),indent=2)+'\n')
print('PREDECLARED ALL N2 LOANS RETAINED; no sampling, no anchor bypass')
