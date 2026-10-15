from pathlib import Path
import csv, hashlib, json, shutil, subprocess

root=Path('/home/hclau/ecdsa_research/prefilter-20261015')
src=Path('/home/hclau/ecdsa_research/product-exact-20261015/tip')
dest=root/'observer-tip'
assert not dest.exists()
dest.mkdir()
for name in ('Cargo.toml','Cargo.lock','rust-toolchain.toml'):
    if (src/name).exists():shutil.copy2(src/name,dest/name)
shutil.copytree(src/'src',dest/'src')
base=dest/'src/point_add'
trace=(root/'value_trace.rs').read_text()
trace=trace.replace('/home/hclau/ecdsa_research/trace-value-20261015',str(root))
trace=trace.replace('["valuefail186","independent"]','["audit"]')
needle='let tape:Vec<_>=m.letter.iter().map(|q|s.qubits[q.0 as usize]>>lane&1).collect();'
assert trace.count(needle)==1
trace=trace.replace(needle,needle+'''
                                eprintln!("MODEL_OBS shot={} phase={} tick={} r0={:#x} r1={:#x} tape={:?}",batch*64+lane,m.phase,m.tick,vals[lane][0],vals[lane][1],tape);
''')
(base/'value_trace.rs').write_text(trace)
shutil.copy2('/home/hclau/ecdsa_research/rail-repair-20261015/diagnostic-rails-pre-y33-b3/src/point_add/observed_sim.rs',base/'observed_sim.rs')

def edit(path,needle,replacement):
    s=path.read_text();assert s.count(needle)==1,(path,needle,s.count(needle));path.write_text(s.replace(needle,replacement))
p=base/'mod.rs';p.write_text('mod value_trace;\nmod observed_sim;\n'+p.read_text())
edit(p,'        circ.y33_clears();','        value_trace::run(circ.rail_observation_ops());\n        circ.y33_clears();')
edit(base/'builder.rs','    pub(crate) fn y33_clears(&mut self) {','    pub(crate) fn rail_observation_ops(&self) -> &[Op] { &self.ops }\n    pub(crate) fn y33_clears(&mut self) {')
p=base/'leapfrog.rs'
fwd='fn fwd_tick(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {'
rev='fn rev_tick(c: &mut Builder, wk: &mut Walk, t: usize, mut pay: Option<&mut [Vec<QubitId>; 2]>) {'
edit(p,fwd,fwd.replace('fwd_tick(','fwd_tick_inner('));edit(p,rev,rev.replace('rev_tick(','rev_tick_inner('))
p.write_text(p.read_text()+'\n'+fwd+'''
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::FwdBefore,&wk.r,&[],lowrel());
    fwd_tick_inner(c,wk,t,pay.as_deref_mut());
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::FwdAfter,&wk.r,wk.tape.last().unwrap(),lowrel());
}
'''+rev+'''
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::RevBefore,&wk.r,&[],lowrel());
    rev_tick_inner(c,wk,t,pay.as_deref_mut());
    super::value_trace::mark(c.op_count(),c.current_phase(),t,super::value_trace::Kind::RevAfter,&wk.r,&[],lowrel());
}
''')
rows=list(csv.DictReader(open(root/'evidence/census-coordinates4096.tsv'),delimiter='\t'))
bad=[r for r in rows if r['value']=='1']
good=[r for r in rows[:1024] if r['value']=='0']
selected=bad[:24]+good[:8]
packet=root/'packets';packet.mkdir(exist_ok=True)
(packet/'audit.tsv').write_text(''.join(f'{i} '+ ' '.join(r[k] for k in ('tx','ty','ox','oy','ex','ey'))+'\n' for i,r in enumerate(selected)))
(packet/'audit-rows.json').write_text(json.dumps(selected,indent=2)+'\n')
patch=subprocess.run(['diff','-ruN',str(src/'src'),str(dest/'src')],capture_output=True).stdout
(root/'evidence/observer.patch').write_bytes(patch)
(root/'evidence/observer-manifest.json').write_text(json.dumps(dict(source=str(src),source_revision='4b2ec52fc55da796aa8f5ef851290297e8706424',destination=str(dest),shots=len(selected),patch_sha256=hashlib.sha256(patch).hexdigest(),expected_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'),indent=2)+'\n')
print('Prepared gate-inert observer',dest)
