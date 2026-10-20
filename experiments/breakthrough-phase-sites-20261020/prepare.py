"""Observe exact original-planner caller contracts; must preserve raw13f6."""
import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-hardcap-audit-20261020'
assert not t.exists()and(old/'run-v2.exit').read_text().strip()=='0'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/builder.rs';raw=p.read_bytes();needle=b'    pub fn alloc_qubits(&mut self, n: usize) -> Vec<QubitId> {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n        if self.active_qubits as usize+n>=1233{eprintln!("ARRAY_CALL\\t{}\\t{}\\t{}\\t{}\\t{}",self.phase,self.ops.len(),self.active_qubits,n,std::panic::Location::caller());}')
p.write_bytes(raw)
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes()
needle=b'fn lin_and(c: &mut Builder, a: &Lin, b: &Lin) -> QubitId {';assert raw.count(needle)==1
raw=raw.replace(needle,b'#[track_caller]\n'+needle+b'\n    if c.active_qubits()>=1232{eprintln!("LIN_AND_CALL\\t{}\\t{}\\t{}\\t{}",c.current_phase(),c.op_count(),c.active_qubits(),std::panic::Location::caller());}')
needle=b'fn lin_lt_phase(c: &mut Builder, a: &[QubitId], add: &[Lin], cin: QubitId) {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'''
    if a.len()>=2{
        let n=a.len();let rows:Vec<_>=add.iter().map(|r|r.w.clone()).collect();
        phase_site_audit(c,"lin_lt",a,&rows,cin,None);
    }
''')
needle=b'fn carry_out_parity_xor(c: &mut Builder, acc: &[QubitId], add: &[Vec<QubitId>], comp: bool, cin: QubitId, out: Option<QubitId>) {';assert raw.count(needle)==1
raw=raw.replace(needle,needle+b'\n    if acc.len()>=2&&out.is_none(){phase_site_audit(c,"parity_phase",acc,add,cin,out);}')
raw+=b'''
fn phase_site_audit(c:&mut Builder,family:&str,acc:&[QubitId],rows:&[Vec<QubitId>],cin:QubitId,out:Option<QubitId>){
    use std::collections::BTreeSet;
    let n=acc.len();let a:BTreeSet<_>=rows[n-2].iter().map(|q|q.0).collect();let d:BTreeSet<_>=rows[n-1].iter().map(|q|q.0).collect();
    let rank=if a.is_empty()||d.is_empty()||a==d{1}else{2};
    let forbidden:BTreeSet<_>=acc.iter().copied().chain([cin]).chain(out).map(|q|q.0).collect();
    let admissible=rows.iter().all(|row|row.iter().all(|q|!forbidden.contains(&q.0))&&row.iter().map(|q|q.0).collect::<BTreeSet<_>>().len()==row.len());
    eprintln!("FUSION_SITE\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}\\t{}",family,c.current_phase(),c.op_count(),c.active_qubits(),n,rank,usize::from(admissible));
}
''';p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in f['protected_files'].items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'raw_control':'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b',
 'scope':'Original1234 planner only. Allocation-array callers, Lin AND callers, exact two-stage phase-fusion admission/rank audit. Metadata only; require byte-identical complete raw stream.'},indent=2)+'\n')
