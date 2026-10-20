import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'tool';old=ws/'breakthrough-generic-postpass-20261020';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=json.loads((old/'SOURCE_FREEZE.json').read_text())
assert not t.exists() and (old/'run-v2.exit').read_text().strip()=='0';assert all(sha(old/'observer'/p)==h for p,h in {**f['source_files'],**f['protected_files']}.items());inputfile=old/'generic-cap1233/ops.bin';assert sha(inputfile)=='92b151d84c4ab7936786aa4901f4399d8557dc49228666af72546a3f0495ef86'
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),f['base']],check=True)
for p in (old/'observer/src/point_add').rglob('*'):
 if p.is_file():q=t/p.relative_to(old/'observer');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
reference={n:sha(r/n)for n in ['mod.rs','table.rs','tests_table.rs','tests_classical_factors.rs','product7_simplify.rs']};dest=t/'src/point_add/extra_truth14';dest.mkdir(exist_ok=False)
s=(r/'mod.rs').read_text().replace('\r','').replace('const SUPPORT_CAP: usize = 9;','const SUPPORT_CAP: usize = 14;').replace('at most nine immutable','at most fourteen immutable')
a='''        let mut table = Table::low(0);
        for row in 0..1usize << atoms.len() {
            let left = a.value_in_union(&a_positions, row);
            let right = b.value_in_union(&b_positions, row);
            let value = if is_and { left & right } else { left ^ right };
            table.set(row, value);
        }'''
b='''        let left=a.table.lift(&a_positions,atoms.len());let right=b.table.lift(&b_positions,atoms.len());
        let table=if is_and{left.and(right)}else{left.xor(right)};''';assert s.count(a)==1;s=s.replace(a,b);s+='\n#[cfg(test)]#[path="vector_tests.rs"]mod vector_tests;\n#[cfg(test)]#[path="stream_audit.rs"]mod stream_audit;\n';(dest/'mod.rs').write_bytes(s.encode());(dest/'table.rs').write_bytes((r/'table14.rs').read_bytes())
s=(r/'product7_simplify.rs').read_text().replace('\r','');a='''    let mut table = Table::low(0);
    for row in 0..1usize << atoms.len() {
        table.set(row, a.value_in_union(&left, row) & b.value_in_union(&right, row));
    }''';b='    let table=a.table.lift(&left,atoms.len()).and(b.table.lift(&right,atoms.len()));';assert s.count(a)==1;s=s.replace(a,b);(dest/'product7_simplify.rs').write_bytes(s.encode())
s=(r/'tests_table.rs').read_text().replace('\r','');a='let a=from_fn((0..9).collect(),|r|r.count_ones()%2==1);let b=from_fn(vec![9],|r|r==1);';b='let a=from_fn((0..SUPPORT_CAP as u64).collect(),|r|r.count_ones()%2==1);let b=from_fn(vec![SUPPORT_CAP as u64],|r|r==1);';assert s.count(a)==1;s=s.replace(a,b);(dest/'tests_table.rs').write_bytes(s.encode())
for n in ['tests_classical_factors.rs','vector_tests.rs','stream_audit.rs']:(dest/n).write_bytes((r/n).read_bytes())
p=t/'src/point_add/mod.rs';p.write_bytes(p.read_bytes()+b'\nmod extra_truth14;\n');subprocess.run(['cp','-a','--reflink=auto',str(old/'observer/target'),str(t/'target')],check=True);assert all(sha(t/p)==h for p,h in f['protected_files'].items());(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':f['base'],'protected_files':f['protected_files'],'source_files':{p.relative_to(t).as_posix():sha(p)for p in (t/'src/point_add').rglob('*')if p.is_file()},'legacy_reference':reference,'input_stream':str(inputfile),'input_stream_sha256':sha(inputfile),'scope':'Research-only cloned exact Boolean optimizer with14 immutable atoms and vectorized truth lifting/cofactor removal. New backend tested against independent scalar functions, exhaustive one-hot linear maps and original-vs-rewritten full random guarded measurement circuits. Unsupported whole expressions remain fresh, never assumed equal. No harness/Cargo changes. Audit frozen generic input only afternativecontrols; original9product pass first, then14products/classical. No benchmark, finalgate, nonce or scored result.'},indent=2)+'\n')
