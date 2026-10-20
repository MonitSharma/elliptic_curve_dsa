import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';rawbase=ws/'breakthrough-cap-cost-20261020';parent=ws/'breakthrough-phase-pebble-paused-20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((parent/'SOURCE_FREEZE.json').read_text());assert not t.exists()and(parent/'run.exit').read_text().strip()=='0'
assert all(sha(parent/'primitive'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for name in['builder.rs','record.rs','break_profile.rs','mod.rs']:(t/'src/point_add'/name).write_bytes((rawbase/'observer/src/point_add'/name).read_bytes())
for name in['phase_fusion.rs','phase_pebble.rs']:(t/'src/point_add'/name).write_bytes((parent/'primitive/src/point_add'/name).read_bytes())
(t/'src/point_add/phase_fit.rs').write_bytes((r/'phase_fit.rs').read_bytes())
def edit(name,needle,replacement):
 p=t/'src/point_add'/name;raw=p.read_bytes();assert raw.count(needle)==1,(name,needle,raw.count(needle));p.write_bytes(raw.replace(needle,replacement))
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod phase_fusion;\nmod phase_pebble;\nmod phase_fit;\n')
needle=b'    let break_cap = std::env::var("BREAK_CAP").expect("Diagnostic BREAK_CAP required");'
edit('mod.rs',needle,needle+b'\n    assert_eq!(break_cap,"1234");let hard=std::env::var("BREAK_HARD").expect("Independent hard cap required");assert!(["1234","1233"].contains(&hard.as_str()));')
needle=b'    std::env::set_var("HEO_PIN_PP_WALK_MAX_QUBITS", &break_cap);'
edit('mod.rs',needle,needle+b'\n    std::env::set_var("PEBBLE_HARD_CAP",&hard);')
pb=(parent/'primitive/src/point_add/builder.rs').read_bytes();start=pb.index(b'    /// Three-body phase');end=pb.index(b'    pub fn cz(',start)
edit('builder.rs',b'    pub fn cz(&mut self, a: QubitId, b: QubitId) {',pb[start:end]+b'    pub fn cz(&mut self, a: QubitId, b: QubitId) {')
for name,signature,insertion in[
 ('leapfrog.rs',b'fn ladder_parity_add(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], cin: Option<QubitId>) {',b'\n    if phase_plain_try(c,acc,add,cin){return;}'),
 ('leapfrog.rs',b'fn ladder_parity_add_mid(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], cin: Option<QubitId>, mid: &mut dyn FnMut(&mut Builder, &[Option<QubitId>])) {',b'\n    if phase_pause_try(c,acc,add,cin,mid){return;}'),
 ('leapfrog.rs',b'fn gidney_add_lean(c: &mut Builder, a: &[QubitId], b: &[QubitId], cin: Option<QubitId>) {',b'\n    if a.len()==b.len(){let rows:Vec<_>=a.iter().map(|&q|vec![q]).collect();if phase_plain_try(c,b,&rows,cin){return;}}')]:edit(name,signature,signature+insertion)
for forward in[True,False]:
 needle=f'    let reserve = yp8_reserve(acc.len(), b.len(), tick, {str(forward).lower()});'.encode();edit('leapfrog.rs',needle,needle+f'\n    let _phase_pause=phase_pause_scope(&acc,tick,reserve,{str(forward).lower()});'.encode())
needle=b'            for (j, cj) in carry.iter().enumerate() {'
edit('leapfrog.rs',needle,needle+b'\n                if super::phase_fit::cap()<1234&&cj.is_none(){continue;} // This dropped position already holds its completed sum.')
needle=b'fn carry_out_parity_xor(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], comp: bool, cin: QubitId, out: Option<QubitId>) {'
edit('leapfrog.rs',needle,needle+b'\n    if super::phase_fit::cap()<1234&&out.is_none()&&acc.len()>=2&&c.active_qubits()as usize+acc.len()-1>super::phase_fit::cap(){if super::phase_fusion::apply(c,acc,add,comp,cin,true){return;}}')
needle=b'fn lin_lt_phase(c: &mut Builder, a: &[QubitId], add: &[Lin], cin: QubitId) {'
edit('leapfrog.rs',needle,needle+b'''
    if super::phase_fit::cap()<1234&&a.len()>=2&&c.active_qubits()as usize+a.len()-1>super::phase_fit::cap(){
        let rows:Vec<_>=add.iter().map(|v|v.w.clone()).collect();if super::phase_fit::source_ok(a,&rows,cin){let w=a.len();c.x_all(a);let mut d=vec![cin];for i in 0..w-2{let q=m_carry(c,a[i],&add[i],d[i]);d.push(q);}
            assert!(super::phase_fusion::pair(c,a[w-2],a[w-1],d[w-2],&add[w-2].w,add[w-2].one,&add[w-1].w,add[w-1].one,false));for i in(1..w-1).rev(){m_carry_erase(c,d[i],a[i-1],&add[i-1],d[i-1]);}c.x_all(a);return;}
    }
''')
# The selected variants are exact; the original outer merged-op eligibility stays unchanged.
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes();start=raw.index(b'fn m_fold_plan(');end=raw.index(b'fn plan_x2(',start);part=raw[start:end];assert b'cells::cap()'in part
raw=raw[:start]+part.replace(b'cells::cap()',b'super::phase_fit::cap()')+raw[end:];raw+=(r/'leapfrog_adapter.rs').read_bytes();p.write_bytes(raw)
# Replace only complete ordinary chunks. Existing boundary-drop ladders stay original.
needle=b'        let direct = last && w >= 2;'
edit('y15_onefold.rs',needle,needle+b'''
        if let Some(out)=phase_chunk_try(c,&acc[lo..hi],&add[lo..hi],cin,!last,direct){if let Some(out)=out{kept.push((lo,hi,cin,out));cin=out;}lo=hi;continue;}
''')
needle=b'        let direct = last && w >= 2 && m_fold_lean();'
edit('leapfrog.rs',needle,needle+b'\n        if let Some(out)=phase_chunk_try(c,&acc[lo..hi],&add[lo..hi],cin,!last,direct){if let Some(out)=out{kept.push((lo,hi,cin,out));cin=out;}lo=hi;continue;}')
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},'caps':[1234,1233],
 'scope':'Fresh accepted raw source: exact phase-pebble ordinary/paused ladders and carry-birth hooks, DP min-rank schedules, ordinary Y15/generic fold chunks, exact top phase fusion, independent generic m_fold_plan low-carry storage budget. Original outer walk/square eligibility/windows/iterations unchanged. Known-terminal modular adapters and prior negative sources are excluded. No final gate/nonce or scored result.'},indent=2)+'\n')
