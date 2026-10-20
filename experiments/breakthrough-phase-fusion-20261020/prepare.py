import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'primitive';base='90e777ea8242faa0acb2462c5cb5be7c318a2d64'
assert not t.exists();subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();names=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={p:sha(t/p)for p in names if not p.startswith('src/point_add/')};assert len(protected)==17
(t/'src/point_add/phase_fusion.rs').write_bytes((r/'phase_fusion.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as f:f.write(b'\nmod phase_fusion;\n')
p=t/'src/point_add/builder.rs';raw=p.read_bytes();needle=b'    pub fn cz(&mut self, a: QubitId, b: QubitId) {';assert raw.count(needle)==1
insert=b'''    /// Three-body phase with the same scored-gate attribution as CCX.
    #[track_caller]
    pub fn ccz(&mut self, a: QubitId, b: QubitId, d: QubitId) {
        if a == b { self.cz(a, d); return; }
        if a == d { self.cz(a, b); return; }
        if b == d { self.cz(a, b); return; }
        let mut op = Op::empty();
        op.kind = OperationType::CCZ;
        op.q_control2 = a; op.q_control1 = b; op.q_target = d;
        if self.ccx_census.watching() {
            let at = self.at();
            self.ccx_census.on_gate(at, OperationType::CCZ, std::panic::Location::caller());
        }
        self.push_op(op);
    }
''';p.write_bytes(raw.replace(needle,insert+needle))
assert all(sha(t/p)==h for p,h in protected.items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':protected,
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
 'scope':'Exact two-stage carry-phase fusion, one fewer clean carry. Source-row rank<=1 uses one CCZ, rank2 two; CCZ is scored. All original operands and exact phase sign restore. Native component only, no point-add resource result/final gate/nonce.'},indent=2)+'\n')
