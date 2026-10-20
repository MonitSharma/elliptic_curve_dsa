"""Freeze exact paused read-set admission and full plain-ripple adaptation."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-hardcarry-20261020';paused=ws/'breakthrough-parity-paused-20261020'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not t.exists()and(old/'run-v2.exit').read_text().strip()=='0'and(paused/'run-v2.exit').read_text().strip()=='0'
f=json.loads((old/'SOURCE_FREEZE.json').read_text());pf=json.loads((paused/'SOURCE_FREEZE-v2.json').read_text())
for parent,freeze,sub in[(old,f,'observer'),(paused,pf,'primitive')]:assert all(sha(parent/sub/p)==h for p,h in{**freeze['source_files'],**freeze['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
def edit(name,needle,replacement):
 p=t/'src/point_add'/name;raw=p.read_bytes();assert raw.count(needle)==1,(name,needle,raw.count(needle));p.write_bytes(raw.replace(needle,replacement))
(t/'src/point_add/parity_paused.rs').write_bytes((paused/'primitive/src/point_add/parity_paused.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as stream:stream.write(b'\nmod parity_paused;\n')
edit('modular.rs',b'if c.current_phase()!="square"||a.is_empty()||a.len()>b.len(){return false;}',b'if a.is_empty()||a.len()>b.len(){return false;}')
edit('modular.rs',b'let hard=std::env::var("HARD_CARRY_CAP").expect("Pinned global width").parse::<usize>().unwrap();',b'let hard=std::env::var("HARD_CARRY_CAP").expect("Pinned global width").parse::<usize>().unwrap();if hard>=1234{return false;}')
needle=b'fn ladder_parity_add_mid(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], cin: Option<QubitId>, mid: &mut dyn FnMut(&mut Builder, &[Option<QubitId>])) {'
edit('leapfrog.rs',needle,needle+b'\n    if yp8_paused_borrow(c,acc,add,cin,mid){return;}')
# Both complete YP8 callers establish the same exact read masks and original reserve.
needle=b'    let reserve = yp8_reserve(acc.len(), b.len(), tick, true);'
edit('leapfrog.rs',needle,needle+b'\n    let _read_scope=yp8_read_scope(&acc,b,tick,reserve);')
needle=b'    let reserve = yp8_reserve(acc.len(), b.len(), tick, false);'
edit('leapfrog.rs',needle,needle+b'\n    let _read_scope=yp8_read_scope(&acc,b,tick,reserve);')
needle=b'            for (j, cj) in carry.iter().enumerate() {'
edit('leapfrog.rs',needle,needle+b'\n                if !yp8_flip_reads(acc[delta+j]){continue;}')
# Runtime source audit examines every gate emitted by yp8_logic, not guessed counts.
needle=b'fn yp8_logic(c: &mut Builder, t2: &[QubitId], b: &[QubitId], s1: QubitId, ct: QubitId, tick: usize, outs: Option<(QubitId, QubitId, QubitId)>) {'
edit('leapfrog.rs',needle,needle+b'''
    let read_audit_from=c.op_count();
    let(tmask,bmask)=yp8_read_indices(t2.len(),b.len(),tick);
    let allowed:Vec<_>=tmask.into_iter().map(|i|t2[i]).chain(bmask.into_iter().map(|i|b[i])).collect();
    let forbidden:Vec<_>=t2.iter().chain(b.iter()).copied().filter(|q|!allowed.contains(q)).collect();
''')
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes();flat=raw.replace(b'\r',b'')
start=flat.index(b'fn yp8_logic(');end=flat.index(b'\n}\n\n/// [`fast_add_halve_forced_lr`] for forced move 2 under LF_YP8',start)
oldsub=flat[start:end];newsub=oldsub+b'\n    c.assert_avoids_since(read_audit_from,&forbidden);'
# This function now has mixed old/new line endings. Replace its exact byte span by locating ASCII anchors.
start_raw=raw.index(b'fn yp8_logic(');anchor=raw.index(b'/// [`fast_add_halve_forced_lr`] for forced move 2 under LF_YP8',start_raw)
end_raw=raw.rfind(b'}',start_raw,anchor)
assert raw[start_raw:end_raw].replace(b'\r',b'').rstrip()==oldsub.rstrip()
raw=raw[:start_raw]+newsub+b'\n'+raw[end_raw:];raw+=(r/'yp8_read_adapter.rs').read_bytes();p.write_bytes(raw)
needle=b'    pub fn cz(&mut self, a: QubitId, b: QubitId) {'
edit('builder.rs',needle,b'''    pub fn assert_avoids_since(&self,from:usize,forbidden:&[QubitId]) {
        for (j,op) in self.ops[from..].iter().enumerate() {
            for q in [op.q_control2,op.q_control1,op.q_target] {
                assert!(!forbidden.contains(&q),"YP8 read-set contract: op{} touches {:?}",from+j,q);
            }
        }
    }
'''+needle)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'caps':[1234,1233],'all_original_planner_caps':1234,'scope':'Exact YP8 low/sign/window read mask; every yp8_logic gate audited against it. Partial sum flip only required target bits. Source-exclusive paused MAJ borrowing excludes protected targets/source and pending hooks. Full plain modular ripple contracts adapted in all phases. Baseline1234 exact13f6. No arithmetic window/iteration change, final gate, nonce or scored resource result.'},indent=2)+'\n')
