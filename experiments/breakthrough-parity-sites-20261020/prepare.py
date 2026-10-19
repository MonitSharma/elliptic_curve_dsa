import hashlib,json,re,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;t=r/'observer'
base='90e777ea8242faa0acb2462c5cb5be7c318a2d64';assert not t.exists()
subprocess.run(['git','-C',str(ws/'toffoli'),'worktree','add','--detach',str(t),base],check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=subprocess.check_output(['git','-C',str(t),'ls-files']).decode().splitlines()
protected={name:sha(t/name)for name in paths if not name.startswith('src/point_add/')};assert len(protected)==17
old=ws/'breakthrough-cap-cost-20261020/observer'
for name in['builder.rs','record.rs','break_profile.rs','mod.rs']:
    (t/'src/point_add'/name).write_bytes((old/'src/point_add'/name).read_bytes())
(t/'src/point_add/parity_probe.rs').write_bytes((r/'parity_probe.rs').read_bytes())
with(t/'src/point_add/mod.rs').open('ab')as f:f.write(b'\nmod parity_probe;\n')
p=t/'src/point_add/leapfrog.rs';raw=p.read_bytes()
for name,kind in[('ladder_parity_add','plain'),('ladder_parity_add_mid','paused')]:
    starts=list(re.finditer(rb'\bfn '+name.encode()+rb'\s*\(',raw));assert len(starts)==1
    begin=raw.index(b'{',starts[0].end());match=re.search(rb'(?m)^}\r*\n',raw[begin:]);assert match
    end=begin+match.start();body=raw[begin+1:end]
    prefix=f'\nlet break_probe_start=super::parity_probe::begin(c,acc,add,cin,"{kind}",Y28_HOOK.with(|x|x.get().is_some()));\nlet break_probe_result=(|| {{\n'.encode()
    suffix=f'\n}})();\nsuper::parity_probe::end(c,"{kind}",break_probe_start);\nbreak_probe_result\n'.encode()
    raw=raw[:begin+1]+prefix+body+suffix+raw[end:]
p.write_bytes(raw)
assert all(sha(t/p)==h for p,h in protected.items())
(r/'source.patch').write_bytes(subprocess.check_output(['git','-C',str(t),'diff','--binary','HEAD']))
(r/'SOURCE_FREEZE.json').write_text(json.dumps({'base':base,'protected_files':protected,
    'source_files':{p.relative_to(t).as_posix():sha(p)for p in sorted((t/'src/point_add').rglob('*'))if p.is_file()},
    'expected_native_raw_sha256':'13f6ffc377e0f2ec043a54d04296c79eb68fc0a16e2ce0277bdc7dcc624e8e7b',
    'scope':'Source-exclusive pivot availability observation, including paused ladders which are not automatically eligible for a replacement. No gates changed.'},indent=2)+'\n')
