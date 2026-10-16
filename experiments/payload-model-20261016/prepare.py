from pathlib import Path
import csv,json,hashlib,shutil,subprocess
root=Path('/home/hclau/ecdsa_research/payload-model-20261016');old=root.parent/'prefilter-20261015';src=old/'observer-tip';dest=root/'observer-tip';assert not dest.exists();dest.mkdir()
for name in ['Cargo.toml','Cargo.lock','rust-toolchain.toml']:
 if(src/name).exists():shutil.copy2(src/name,dest/name)
shutil.copytree(src/'src',dest/'src');base=dest/'src/point_add'
shutil.copy2(root/'payload_observer.rs',base/'payload_observer.rs')
p=base/'value_trace.rs';s=p.read_text().replace(str(old),str(root));start=s.index('fn point_word(');end=s.index('\npub fn run(',start)
s=s[:start]+'''fn point_word(qs:&[QubitId],words:&[u64],lane:usize)->U256{let p=super::SECP256K1_P;let f=U256::from(0x1000003d1u64);let mut v=U256::ZERO;for(i,q)in qs.iter().enumerate(){if words[q.0 as usize]>>lane&1!=0{v=v.add_mod(if i<256{U256::from(1)<<i}else{f<<(i-256)},p);}}if qs.len()>256&&words[qs.last().unwrap().0 as usize]>>lane&1!=0{v=sub(v,f<<(qs.len()-256),p);}v}
'''+s[end:];p.write_text(s)
p=base/'mod.rs';s='mod payload_observer;\n'+p.read_text();needle='        value_trace::run(circ.rail_observation_ops());';assert s.count(needle)==1;s=s.replace(needle,needle+'\n        payload_observer::run(circ.rail_observation_ops());')
needle='        value_trace::point_mark(circ.op_count(),"after_square",x,y);';assert s.count(needle)==1;s=s.replace(needle,'        let observed_x=leapfrog::observed_preseed().unwrap_or_else(||x.to_vec());\n        value_trace::point_mark(circ.op_count(),"after_square",&observed_x,y);');p.write_text(s)
p=base/'leapfrog.rs';s=p.read_text();s+='\npub(crate) fn observed_preseed()->Option<Vec<QubitId>>{T6_PRESEED.with(|s|s.borrow().clone())}\n'
for name,rev in [('pay_fwd_tick','false'),('pay_rev_tick','true')]:
 sig=f'fn {name}(c: &mut Builder, t: usize, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_payload_unobserved'));s+=f'\n{sig}\nlet id=super::payload_observer::begin(c.op_count(),c.current_phase(),t,{rev},p,letter);\n{name}_payload_unobserved(c,t,letter,p);\nsuper::payload_observer::end(id,c.op_count(),p,letter);\n}}\n'
for name,rev in [('fwd_tick','false'),('rev_tick','true')]:
 sig=f'fn {name}(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_payload_unobserved'));letter='&[]'if name=='fwd_tick'else'&letter';save=''if name=='fwd_tick'else'let letter=wk.tape[t].clone();';endletter='wk.tape.last().unwrap()'if name=='fwd_tick'else'&letter';s+=f'\n{sig}\n{save}\nlet id=pay.as_deref().map(|p|super::payload_observer::begin(c.op_count(),c.current_phase(),t,{rev},p,{letter}));\n{name}_payload_unobserved(c,wk,t,pay.as_deref_mut());\nif let Some(id)=id{{super::payload_observer::end(id,c.op_count(),pay.as_deref().unwrap(),{endletter});}}\n}}\n'
for name,signature,args,rev in [('n2_pay_fwd_last','c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2], skip_rot: bool','c,letter,p,skip_rot','false'),('n2_pay_rev_last','c: &mut Builder, letter: &[QubitId], p: &mut [Vec<QubitId>; 2]','c,letter,p','true')]:
 sig=f'fn {name}({signature}) {{';assert s.count(sig)==1;s=s.replace(sig,sig.replace(name,name+'_payload_unobserved'));s+=f'\n{sig}\nlet id=super::payload_observer::begin(c.op_count(),c.current_phase(),rounds()-1,{rev},p,letter);\n{name}_payload_unobserved({args});\nsuper::payload_observer::end(id,c.op_count(),p,letter);\n}}\n'
needle='            y15::fwd_tick0_one(c, &letter, &mut pay);';assert s.count(needle)==1;s=s.replace(needle,'            let observe_id=super::payload_observer::begin(c.op_count(),c.current_phase(),t,false,&pay,&letter);\n'+needle+'\n            super::payload_observer::end(observe_id,c.op_count(),&pay,&letter);');p.write_text(s)
rows=list(csv.DictReader(open(old/'evidence/census-coordinates4096.tsv'),delimiter='\t'));by={(int(r['batch']),int(r['lane'])):r for r in rows};fps=[(694,38),(1318,50),(1658,27),(3184,27)];selected=[dict(by[k],family='false_positive')for k in fps]
for batch,lane in fps:
 selected.extend(dict(by[batch,j],family='nearby_control')for j in [lane-1,lane+1]if by[batch,j]['value']=='0')
details=[json.loads(l)for p in sorted((old/'evidence/recovered-population').glob('part-*.jsonl'))for l in p.read_text().splitlines()]
for family,pred in [('true_positive',lambda r:r['value'] and r['clean_loan_model_supported']and r['predicted_wrong_value']),('missed_failure',lambda r:r['value']and r['clean_loan_model_supported']and not r['predicted_wrong_value']),('unknown',lambda r:not r['clean_loan_model_supported'])]:
 for d in [r for r in details if pred(r)][:8]:selected.append(dict(by[d['batch'],d['lane']],family=family))
packet=root/'packets';packet.mkdir();(packet/'audit.tsv').write_text(''.join(f'{i} '+ ' '.join(r[k]for k in ['tx','ty','ox','oy','ex','ey'])+'\n'for i,r in enumerate(selected)));(packet/'audit-rows.json').write_text(json.dumps(selected,indent=2)+'\n')
for name in ['walk_model.py','predict-recovered.py']:shutil.copy2(old/name,root/name)
shutil.copytree(old/'model-source',root/'model-source')
patch=subprocess.run(['diff','-ruN',str(root.parent/'product-exact-20261015/tip/src'),str(dest/'src')],capture_output=True).stdout;(root/'observer.patch').write_bytes(patch)
(root/'source-manifest.json').write_text(json.dumps({'base':'4b2ec52fc55da796aa8f5ef851290297e8706424','expected_stream_sha256':'2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e','shots':len(selected),'source_files':{str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in (dest/'src').rglob('*')if p.is_file()}},indent=2)+'\n');print('prepared',len(selected),'shots')
