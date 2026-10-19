import hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-fold-plan7-20261020'
assert not t.exists()and(old/'run.exit').read_text().strip()=='0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for name in['builder.rs','record.rs','break_profile.rs','mod.rs','y15_onefold.rs']:(t/'src/point_add'/name).write_bytes((old/'observer/src/point_add'/name).read_bytes())
p=t/'src/point_add/mod.rs';raw=p.read_bytes();needle=b'std::env::set_var("LF_SQUARE_CAP", &break_cap);';assert raw.count(needle)==1
raw=raw.replace(needle,b'std::env::set_var("LF_SQUARE_CAP", "1234"); // Preserve accepted square planning; hard carry cap is separate.')
raw+=b'\nmod parity_bridge;\n';p.write_bytes(raw)
primitive=ws/'breakthrough-parity-bridge-20261020';pf=json.loads((primitive/'SOURCE_FREEZE.json').read_text());source=primitive/'primitive/src/point_add/parity_bridge.rs'
assert sha(source)==pf['source_files']['src/point_add/parity_bridge.rs']
(t/'src/point_add/parity_bridge.rs').write_bytes(source.read_bytes()+(r/'carryout-tests.rs').read_bytes())
p=t/'src/point_add/width_composition.rs';raw=p.read_bytes()
needle=b'fn direct_chunk(c:&mut Builder,map:&[Vec<QubitId>],b:&[QubitId],at:usize,w:usize,prev:QubitId,out:Option<QubitId>){'
assert raw.count(needle)==1;raw=raw.replace(needle,needle+b'\n    if strict_square_chunk(c,map,b,at,w,prev,out){return;}\n')
start=raw.index(b'pub(crate) fn direct_add_phase_transport(');match=re.search(rb'(?m)^}\r*\n',raw[start:]);assert match
end=start+match.end();body=raw[start:end]
needle=b'        let work=c.alloc_qubits(if last{w.saturating_sub(2)}else{w-1});';assert body.count(needle)==1
body=body.replace(needle,b'        if !strict_square_chunk(c,map,b,at,w,prev,out){\n'+needle)
needle=b'        c.free_vec(&work);';assert body.count(needle)==1;body=body.replace(needle,needle+b'\n        }\n')
raw=raw[:start]+body+raw[end:]+(r/'square-bridge.rs').read_bytes();p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233],'scope':'Plan7 walk plus original1234 square chunk planning with exact source-pivot borrowing to enforce global cap. All windows, boundaries and iteration schedules retained; tests include arbitrary carryout accumulator extension. No score or final gate.'},indent=2)+'\n')
