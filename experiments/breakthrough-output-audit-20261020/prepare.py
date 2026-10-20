"""Separate development replay extension; official benchmark stays untouched."""
import hashlib,json,shutil,subprocess,tomllib
from pathlib import Path
r=Path(__file__).resolve().parent;ws=r.parent;old=ws/'simd-census-v2-20261016/tool';t=r/'tool';assert not t.exists();t.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in['Cargo.toml','Cargo.lock','build.rs','simd8count.c','simd8wide.h']:shutil.copyfile(old/name,t/name)
shutil.copytree(old/'src',t/'src')
p=t/'src/main.rs';before=p.read_bytes();needle=b'     let failures=(0..64).filter(|lane|bad>>lane&1!=0)';assert before.count(needle)==1
insert=b'''     let mut output_digest=sha3::Sha3_256::default();
     sha3::Digest::update(&mut output_digest,b"ecdsa-four-register-output-v1");
     for lane in 0..64 {for reg in regs[..4].iter(){let value=get(&q,&b,reg,lane,j);sha3::Digest::update(&mut output_digest,value.to_le_bytes::<32>());}}
     let output_hash=sha3::Digest::finalize(output_digest).iter().map(|v|format!("{v:02x}")).collect::<String>();
'''
after=before.replace(needle,insert+needle)
needle=b'\\"failures\\":[{failures}]';assert after.count(needle)==1
after=after.replace(needle,b'\\"output_sha3_256\\":\\"{output_hash}\\",'+needle);p.write_bytes(after)
diff=subprocess.run(['git','diff','--no-index',str(old/'src/main.rs'),str(p)],capture_output=True,check=False);assert diff.returncode==1
(r/'output-only.patch').write_bytes(diff.stdout)
config=tomllib.loads((t/'Cargo.toml').read_text());lib=Path(config['dependencies']['quantum_ecc']['path'])
tracked=subprocess.check_output(['git','-C',str(lib),'ls-files']).decode().splitlines()
protected={str(lib/name):sha(lib/name)for name in tracked if not name.startswith('src/point_add/')};assert len(protected)==17
(r/'TOOL-SOURCE-FREEZE.json').write_text(json.dumps({'original_binary_sha256':'790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66',
 'source_files':{p.relative_to(t).as_posix():sha(p)for p in t.rglob('*')if p.is_file()},'protected_dependency_files':protected,
 'binary_name':config['package']['name'],'label':'breakthrough-local-fold-output-v1','batches':512,'workers':2,'protected_scalar_batches_per_run':8,
 'scope':'Append SHA3-256 of all four final registers in fixed lane/register order to each diagnostic row. Every original row field must match original binary on all512 parent batches; protected full-state and scoredT controls remain8/run. Then compare all parent/candidate output hashes including inherited wrong outputs. No candidate/harness/scorer/official benchmark modification or final gate.'},indent=2)+'\n')
