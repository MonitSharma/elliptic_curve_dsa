from pathlib import Path
import shutil,subprocess,json,hashlib
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');dest=root/'observer-tip';p=dest/'src/point_add/compare.rs'
for name in ['observer.patch','observer-source.json','observer.log','raw-stream-bindings.sha256']:
 shutil.copy2(root/name,root/(name.replace('.', '-v1.',1)))
shutil.copy2(p,root/'compare-v1.rs')
s=p.read_text();needle='    cmp_lt_phase_v0(circ, u, v, borrow_in, None)\n}';assert s.count(needle)==1
s=s.replace(needle,'''    let macro_compare_at=circ.op_count();
    cmp_lt_phase_v0(circ, u, v, borrow_in, None);
    eprintln!("C35_END\\t{}\\t{}\\t{}\\t{}",macro_compare_at,circ.op_count(),u.len(),borrow_in.is_some()as u8);
}''');p.write_text(s)
(root/'observer.patch').write_bytes(subprocess.check_output(['git','-C',str(dest),'diff','--binary']))
(root/'observer-source.json').write_text(json.dumps(dict(base='4b2ec52fc55da796aa8f5ef851290297e8706424',gate_inert=True,component_only=True,files={str(p.relative_to(dest)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(dest/'src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
