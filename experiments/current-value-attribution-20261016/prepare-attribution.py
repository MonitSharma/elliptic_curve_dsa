from pathlib import Path
import csv,json,hashlib,subprocess,shutil,datetime
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');r.mkdir(exist_ok=True)
pre=r.parent/'prefilter-20261015';census_path=r.parent/'product-tip-20261015/tip-census.jsonl';coords_path=pre/'evidence/census-coordinates4096.tsv'
census=[json.loads(s)for s in census_path.read_text().splitlines()];assert len(census)==4096
bad={(x['batch'],f['lane'])for x in census for f in x['failures']if f['value']};assert len(bad)==431
batches=sorted({b for b,l in bad});assert all(census[b]['batch']==b and census[b]['skipped']==0 for b in batches)
rows=[]
with coords_path.open()as f:
 for x in csv.DictReader(f,delimiter='\t'):
  key=int(x['batch']),int(x['lane'])
  if key[0]in batches:rows.append(x)
assert len(rows)==64*len(batches)and sum(int(x['value'])for x in rows)==431
packet=r/'packets';packet.mkdir(exist_ok=True)
(packet/'tip431.tsv').write_text(''.join(str(int(x['batch'])*64+int(x['lane']))+' '+' '.join(x[k]for k in['tx','ty','ox','oy','ex','ey'])+'\n'for x in rows))
(packet/'tip431-keys.tsv').write_text(''.join(f'{x["batch"]} {x["lane"]} {x["k1"]} {x["k2"]} {x["value"]}\n'for x in rows))
(packet/'batches.json').write_text(json.dumps(batches)+'\n')
(packet/'expected-census.jsonl').write_text(''.join(json.dumps(census[b])+'\n'for b in batches))
declaration=dict(status='FIXED DIAGNOSTIC REPLAY BEFORE OBSERVATION',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',actual_final_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',
 cohort_label='tip-4b2ec52f',cohort_domain='ecdsa-research-failure-census-v1',value_witnesses=431,all_value_witnesses_selected=True,
 original_batches=batches,original_full_context_shots=len(rows),sampling='NONE; replay exact existing inputs and original per-batch MR words; all64original lanes retained',
 attribution='source marker neighborhoods map into literal ACTUAL final2a Ops; unmapped boundaries stay UNKNOWN; replay final2a and compare everyq/b/phase/T to unchanged protected Simulator',
 intended_interfaces='full signed extended payload stage; actual tape-driven modular payload ticks; signed forward/reverse fold equations; full square window signed arithmetic',
 no_candidate_change=True,no_packet_selected_cuts=True,no_source_ideal_correctness_assumption=True,
 inputs={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())for p in[census_path,coords_path]},
 packets={str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in packet.iterdir()})
assert not(r/'REPLAY-PREDECLARATION.json').exists();(r/'REPLAY-PREDECLARATION.json').write_text(json.dumps(declaration,indent=2)+'\n')
tip=r.parent/'product-exact-20261015/tip';d=r/'source-observer';rev=declaration['source_revision'];assert not d.exists();assert subprocess.check_output(['git','-C',str(tip),'rev-parse','HEAD'],text=True).strip()==rev
subprocess.run(['git','-C',str(tip),'worktree','add','--detach',str(d),rev],check=True);b=d/'src/point_add'
original=r.parent/'failure-floor-20261015/payload_trace.rs';trace=original.read_text().split('pub fn run(ops:&[Op]){')[0]
dump='''
pub fn dump(ops:&[Op]){use std::io::Write;let root="/home/hclau/ecdsa_research/current-value-attribution-20261016";let mut out=std::fs::File::create(format!("{root}/raw-markers.jsonl")).unwrap();let ids=|q:&[QubitId]|q.iter().map(|q|q.0).collect::<Vec<_>>();
for m in MARKS.lock().unwrap().iter(){writeln!(out,"{{\\"family\\":\\"payload\\",\\"at\\":{},\\"id\\":{},\\"before\\":{},\\"phase\\":\\"{}\\",\\"tick\\":{},\\"rev\\":{},\\"skip\\":{},\\"pay0\\":{:?},\\"pay1\\":{:?},\\"letter\\":{:?}}}",m.at,m.id,m.before,m.phase,m.t,m.rev,m.skip,ids(&m.pay[0]),ids(&m.pay[1]),ids(&m.letter)).unwrap();}
for m in FOLDS.lock().unwrap().iter(){writeln!(out,"{{\\"family\\":\\"fold\\",\\"at\\":{},\\"id\\":{},\\"before\\":{},\\"phase\\":\\"{}\\",\\"tick\\":{},\\"rev\\":{},\\"acc\\":{:?},\\"e\\":{:?},\\"nm\\":{:?},\\"shift\\":{:?},\\"src\\":{:?}}}",m.at,m.id,m.before,m.phase,m.t,m.rev,ids(&m.acc),ids(&m.e),ids(&m.nm),ids(&m.shift),ids(&m.src)).unwrap();}
for(id,m)in STAGES.lock().unwrap().iter().enumerate(){writeln!(out,"{{\\"family\\":\\"stage\\",\\"at\\":{},\\"id\\":{id},\\"label\\":\\"{}\\",\\"x\\":{:?},\\"y\\":{:?},\\"offset\\":\\"{:#x}\\"}}",m.at,m.label,ids(&m.x),ids(&m.y),m.offset).unwrap();}
for m in WINDOWS.lock().unwrap().iter(){writeln!(out,"{{\\"family\\":\\"window\\",\\"at\\":{},\\"id\\":{},\\"before\\":{},\\"inv\\":{},\\"shift\\":{},\\"value\\":{:?},\\"out\\":{:?},\\"cin\\":{}}}",m.at,m.id,m.before,m.inv,m.shift,ids(&m.value),ids(&m.out),m.cin.map_or("null".to_string(),|q|q.0.to_string())).unwrap();}
crate::write_ops(ops,std::path::Path::new(&format!("{root}/raw-builder.bin"))).unwrap();eprintln!("SOURCE_MARKERS_ONLY; ACTUAL FINAL OPS MUST BE REPLAYED SEPARATELY; no score");
}
'''
(b/'payload_trace.rs').write_text(trace+dump);(r/'payload_trace_original.rs').write_bytes(original.read_bytes())
p=b/'mod.rs';s='mod payload_trace;\n'+p.read_text();needle='        circ.y33_clears();';assert s.count(needle)==1;s=s.replace(needle,'        payload_trace::dump(circ.rail_observation_ops());\n        std::process::exit(0);\n'+needle)
needle='        if seams { leapfrog::divide_seamed(circ, y, x, ox); } else { leapfrog::divide(circ, y, x); }';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        payload_trace::stage(circ.op_count(),"divide",x,y,square::sub_square_offset());')
needle='        circ.set_phase("multiply");';assert s.count(needle)==1;s=s.replace(needle,'        let observed_x=leapfrog::observed_preseed().unwrap_or_else(||x.to_vec());\n        payload_trace::stage(circ.op_count(),"square",&observed_x,y,SECP256K1_P-SECP256K1_P);\n'+needle)
needle='        if seams { leapfrog::multiply_seamed(circ, y, x, ox); } else { leapfrog::multiply(circ, y, x); }';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        payload_trace::stage(circ.op_count(),"multiply",x,y,SECP256K1_P-SECP256K1_P);');p.write_text(s)
p=b/'builder.rs';s=p.read_text();needle='    pub(crate) fn y33_clears(&mut self) {';assert s.count(needle)==1;s=s.replace(needle,'    pub(crate) fn rail_observation_ops(&self)->&[Op]{&self.ops}\n'+needle);p.write_text(s)
p=b/'leapfrog.rs';s=p.read_text()
for name,revflag in [('pay_fwd_tick','false'),('pay_rev_tick','true')]:
 sig=f'fn {name}(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_unobserved'))
 save='super::payload_trace::set_letter(id,letter);'if revflag=='true'else''
 s+=f'\n{sig}\nlet id=super::payload_trace::begin(c.op_count(),c.current_phase(),t,{revflag},p);{save}\n{name}_unobserved(c,t,letter,p);\nsuper::payload_trace::end(id,c.op_count(),p,letter,false);\n}}\n'
for name,revflag in [('fwd_tick','false'),('rev_tick','true')]:
 sig=f'fn {name}(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_unobserved'))
 letter='wk.tape.last().unwrap()'if revflag=='false'else'&letter';save=''if revflag=='false'else'let letter=wk.tape[t].clone();'
 save2=''if revflag=='false'else'if let Some(id)=id{super::payload_trace::set_letter(id,&letter);}'
 s+=f'\n{sig}\n{save}\nlet id=pay.as_deref().map(|p|super::payload_trace::begin(c.op_count(),c.current_phase(),t,{revflag},p));{save2}\n{name}_unobserved(c,wk,t,pay.as_deref_mut());\nif let Some(id)=id{{super::payload_trace::end(id,c.op_count(),pay.as_deref().unwrap(),{letter},false);}}\n}}\n'
for name,args,call,revflag,skip in [('n2_pay_fwd_last','c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2], skip_rot: bool','c,letter,p,skip_rot','false','skip_rot'),('n2_pay_rev_last','c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]','c,letter,p','true','false')]:
 sig=f'fn {name}({args}) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_unobserved'));save='super::payload_trace::set_letter(id,letter);'if revflag=='true'else''
 s+=f'\n{sig}\nlet id=super::payload_trace::begin(c.op_count(),c.current_phase(),rounds()-1,{revflag},p);{save}\n{name}_unobserved({call});\nsuper::payload_trace::end(id,c.op_count(),p,letter,{skip});\n}}\n'
needle='            y15::fwd_tick0_one(c, &letter, &mut pay);';assert s.count(needle)==1;s=s.replace(needle,'            let observed_id=super::payload_trace::begin(c.op_count(),c.current_phase(),t,false,&pay);\n'+needle+'\n            super::payload_trace::end(observed_id,c.op_count(),&pay,&letter,false);')
s+='\npub(crate) fn observed_preseed()->Option<Vec<QubitId>>{T6_PRESEED.with(|s|s.borrow().clone())}\n';p.write_text(s)
p=b/'y15_onefold.rs';s=p.read_text()
for name,flag in [('fold_fwd_v2','false'),('fold_rev_v2','true')]:
 a=s.index('fn '+name+'(');end=s.index('\n}',a)+2;part=s[a:end];needle='    let mw = acc.len();';assert part.count(needle)==1;src='src'if flag=='true'else'&[]'
 part=part.replace(needle,needle+f'\n    let observed_id=super::super::payload_trace::fold_begin(c.op_count(),acc,e,nm,k1,k2,{flag},{src});')
 assert part.endswith('    plan\n}');part=part[:-len('    plan\n}')]+ '    super::super::payload_trace::fold_end(observed_id,c.op_count());\n    plan\n}';s=s[:a]+part+s[end:]
p.write_text(s)
p=b/'square.rs';s=p.read_text();a=s.index('fn window_add(');end=s.index('\n///',a);part=s[a:end];needle='    addsub_wide(circ, value, &out[shift..top], negate);';assert part.count(needle)==1;part=part.replace(needle,'    let observed_id=super::payload_trace::window_begin(circ.op_count(),negate,shift,value,out,None);\n'+needle+'\n    super::payload_trace::window_end(observed_id,circ.op_count());');s=s[:a]+part+s[end:]
a=s.index('fn wcin_windows(');end=s.index('\nfn wcin_finish(',a);part=s[a:end];needle='        let inv = negate ^ neg;';assert part.count(needle)==1;part=part.replace(needle,needle+'\n        let observed_id=super::payload_trace::window_begin(circ.op_count(),inv,shift,high,out,Some(c));');needle='        if inv { circ.x_all(win); }';assert part.count(needle)==2;i=part.rindex(needle)+len(needle);part=part[:i]+'\n        super::payload_trace::window_end(observed_id,circ.op_count());'+part[i:];s=s[:a]+part+s[end:];p.write_text(s)
(r/'source-observer.patch').write_bytes(subprocess.check_output(['git','-C',str(d),'diff','--binary']))
(r/'source-observer-manifest.json').write_text(json.dumps(dict(base=rev,component_only=True,no_gate_mutation=True,raw_expected='ff5163962ff5337753235d79f4026893e35b0445ae7406bf03be76d8a3d27a69',files={str(p.relative_to(d)):hashlib.sha256(p.read_bytes()).hexdigest()for p in b.rglob('*')if p.is_file()}),indent=2)+'\n')
print('PREDECLARED',len(bad),'value witnesses,',len(batches),'original full batch contexts; source metadata only')
