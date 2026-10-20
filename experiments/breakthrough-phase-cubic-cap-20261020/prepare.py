import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer';old=ws/'breakthrough-direct-transport-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE-v2.json').read_text())
assert not t.exists()and(old/'run-v3.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in{**f['source_files'],**f['protected_files']}.items())
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in(old/'observer/src/point_add').rglob('*'):
 if p.is_file():dest=t/p.relative_to(old/'observer');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
p=t/'src/point_add/y15_onefold.rs';raw=p.read_bytes()
def change(a,b):
 global raw
 assert raw.count(a)==1,(a,raw.count(a));raw=raw.replace(a,b)
change(b'struct T0Phase {\n    k1: QubitId,\n    k2: QubitId,\n    t: QubitId,',b'struct T0Phase {\n    k1: QubitId,\n    k2: QubitId,\n    t: Option<QubitId>,')
change(b'        let t = and_new(c, k1, k2);\n        let mut at:',b'''        let hard=super::super::phase_fit::cap();
        let direct=Y29_FAULT==0&&k1!=k2&&hard<1234&&c.active_qubits()as usize+1>hard;
        let t=if direct{eprintln!("PHASE_CUBIC_DIRECT\\t{}\\t{}\\t{}\\t{n}",c.current_phase(),c.op_count(),c.active_qubits());None}else{Some(and_new(c,k1,k2))};
        let mut at:''')
change(b'        self.done[j] = true;\n        for &(mono, bit) in &self.at[j] {',b'''        self.done[j] = true;
        if self.t.is_none()&&self.at[j].iter().any(|&(mono,_)|mono==3){
            let parity=c.alloc_bit();c.bit_store0(parity);
            for &(mono,bit)in &self.at[j]{if mono==3{c.bit_xor_into(parity,bit);}}
            c.push_condition(parity);phase_cubic_lin(c,self.k1,self.k2,f);c.pop_condition();c.free_bit(parity);
        }
        for &(mono, bit) in &self.at[j] {
            if mono==3&&self.t.is_none(){continue;}
''')
change(b'                _ => Some(self.t),',b'                _ => self.t,')
change(b'        y29_phrot_clear(c, self.t, self.k1, self.k2);',b'        if let Some(t)=self.t{y29_phrot_clear(c,t,self.k1,self.k2);}')
raw+=b'''
fn phase_cubic_lin(c:&mut Builder,k1:QubitId,k2:QubitId,f:&Lin){
    let constant=f.one^f.w.contains(&k1)^f.w.contains(&k2);if constant{c.cz(k1,k2);}
    let other:Vec<_>=f.w.iter().copied().filter(|q|*q!=k1&&*q!=k2).collect();
    if let Some((&pivot,rest))=other.split_first(){for &q in rest{c.cx(q,pivot);}c.ccz(k1,k2,pivot);for &q in rest.iter().rev(){c.cx(q,pivot);}}
}
''';raw+=(r/'tests.rs').read_bytes();p.write_bytes(raw)
assert not(t/'target').exists();subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True)
assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in(t/'src/point_add').rglob('*')if p.is_file()},'caps':[1234,1233],'scope':'At actual overflow only, replace T0Phase quantum letter-product temporary with direct conditional cubic phase on arbitrary affine rows. Aggregate its classical flags by XOR; exactalias/constant terms are Clifford. Preserveoldfault controls and originalmodewhenhard1234 orcontrolsaliased. Nativeallsmallquantum/classicalinputs, affineconstants/controlaliases, guards, everycleanupRNGposition, exactwidth/Stats/phase, thenallretainedcontrols/fullsourcegeneration. No finalgate/nonce/record.'},indent=2)+'\n')
