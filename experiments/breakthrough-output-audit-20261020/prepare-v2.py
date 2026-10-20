"""Observe the same failed diagnostic per lane; retain the v1 verdict."""
import hashlib,json,shutil,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;old=r/'tool';t=r/'tool-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert(r/'run.exit').read_text().strip()=='1'and not t.exists()
f=json.loads((r/'TOOL-SOURCE-FREEZE.json').read_text());report=json.loads((r/'OUTPUT-DIAGNOSTIC.json').read_text())
assert not report['all_four_final_register_hashes_match_including_failed_inputs']
assert all(sha(old/p)==h for p,h in f['source_files'].items());assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
(r/'bin').mkdir(exist_ok=False);binary=old/'target/release'/f['binary_name'];assert sha(binary)==report['output_binary_sha256'];shutil.copyfile(binary,r/'bin/output-v1')
t.mkdir()
for name in['Cargo.toml','Cargo.lock','build.rs','simd8count.c','simd8wide.h']:shutil.copyfile(old/name,t/name)
shutil.copytree(old/'src',t/'src')
p=t/'src/main.rs';raw=p.read_bytes();needle=b'     let failures=(0..64).filter(|lane|bad>>lane&1!=0)';assert raw.count(needle)==1
insert=b'''     let mut target_lane_hashes=Vec::new();let mut other_lane_hashes=Vec::new();
     for lane in 0..64 {
      let mut target_digest=sha3::Sha3_256::default();let mut other_digest=sha3::Sha3_256::default();
      sha3::Digest::update(&mut target_digest,b"ecdsa-target-pair-v1");sha3::Digest::update(&mut other_digest,b"ecdsa-other-pair-v1");
      for (index,reg) in regs[..4].iter().enumerate(){let value=get(&q,&b,reg,lane,j);if index<2{sha3::Digest::update(&mut target_digest,value.to_le_bytes::<32>());}else{sha3::Digest::update(&mut other_digest,value.to_le_bytes::<32>());}}
      target_lane_hashes.push(format!("\\\"{}\\\"",sha3::Digest::finalize(target_digest).iter().map(|v|format!("{v:02x}")).collect::<String>()));
      other_lane_hashes.push(format!("\\\"{}\\\"",sha3::Digest::finalize(other_digest).iter().map(|v|format!("{v:02x}")).collect::<String>()));
     }
     let target_lane_hashes=target_lane_hashes.join(",");let other_lane_hashes=other_lane_hashes.join(",");
'''
raw=raw.replace(needle,insert+needle);needle=b'\\"failures\\":[{failures}]';assert raw.count(needle)==1
raw=raw.replace(needle,b'\\"target_lane_hashes\\":[{target_lane_hashes}],\\"other_lane_hashes\\":[{other_lane_hashes}],'+needle);p.write_bytes(raw)
diff=subprocess.run(['git','diff','--no-index',str(old/'src/main.rs'),str(p)],capture_output=True,check=False);assert diff.returncode==1;(r/'lane-observation-only.patch').write_bytes(diff.stdout)
(r/'TOOL-SOURCE-FREEZE-v2.json').write_text(json.dumps({'v1_source_freeze_sha256':sha(r/'TOOL-SOURCE-FREEZE.json'),'source_files':{p.relative_to(t).as_posix():sha(p)for p in t.rglob('*')if p.is_file()},'protected_dependency_files':f['protected_dependency_files'],'label':f['label'],'batches':f['batches'],'scope':'Same frozen candidate/parent, same label and same512 batches. Append per-lane target/other SHA3 hashes; every old field including full-output hash must reproduce v1 exactly. Classify the existing failed full-output equality verdict; never replace it or rerun a final gate.'},indent=2)+'\n')
