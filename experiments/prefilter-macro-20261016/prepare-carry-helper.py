from pathlib import Path
import shutil,subprocess,json,hashlib
root=Path('/home/hclau/ecdsa_research/prefilter-macro-20261016');out=root/'additional';out.mkdir(exist_ok=True)
p=root/'observer-tip/src/point_add/y15_onefold.rs'
shutil.copy2(p,out/'y15-before-carry-helper.rs');shutil.copy2(root/'observer.log',out/'observer-before-carry-helper.log')
s=p.read_text()
replacements=[
('    let [c4, c5, c6] = cw;\n    let mut st:', '    eprintln!("CARRY_RECS_BEGIN at={} tick={:?}",c.op_count(),PAYLOAD_AT.with(|x|x.get()));\n    let [c4, c5, c6] = cw;\n    let mut st:'),
('            Rec::UndoC6 => {\n                let m = c.alloc_bit();','            Rec::UndoC6 => {\n                eprintln!("CARRY_C6_BEGIN at={} tick={:?} c4={} c5={} c6={}",c.op_count(),PAYLOAD_AT.with(|x|x.get()),c4.0,c5.0,c6.0);\n                let m = c.alloc_bit();'),
('    st.expect("y28: the fold\'s undo list holds c6")','    eprintln!("CARRY_RECS_END at={} tick={:?}",c.op_count(),PAYLOAD_AT.with(|x|x.get()));\n    st.expect("y28: the fold\'s undo list holds c6")'),
('    let [c1, c2, c3, c4] = cw;\n    if let Some(m) = c4m {','    eprintln!("CARRY_LOW_BEGIN at={} tick={:?} measured={}",c.op_count(),PAYLOAD_AT.with(|x|x.get()),c4m.is_some());\n    let [c1, c2, c3, c4] = cw;\n    if let Some(m) = c4m {'),
('    if !carry_loan_on() {c.cx(c3, acc[3]);}\n    maj_wire_erase','    eprintln!("CARRY_LOW_ERASE_END at={} tick={:?} measured={}",c.op_count(),PAYLOAD_AT.with(|x|x.get()),c4m.is_some());\n    if !carry_loan_on() {c.cx(c3, acc[3]);}\n    maj_wire_erase')]
for a,b in replacements:
 assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
p.write_text(s)
(out/'carry-helper-source.patch').write_bytes(subprocess.check_output(['git','-C',str(root/'observer-tip'),'diff','--binary']))
(out/'carry-helper-source.json').write_text(json.dumps(dict(gate_inert=True,component_only=True,files={str(p.relative_to(root/'observer-tip')):hashlib.sha256(p.read_bytes()).hexdigest()for p in(root/'observer-tip/src/point_add').rglob('*')if p.is_file()}),indent=2)+'\n')
