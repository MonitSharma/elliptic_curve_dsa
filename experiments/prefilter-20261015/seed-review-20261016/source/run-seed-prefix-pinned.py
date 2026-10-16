from pathlib import Path
import hashlib,json,subprocess,datetime
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');d=r/'seed-prefix-pinned-v1';assert not d.exists();d.mkdir()
paths=[r.parent/'product-exact-20261015/tip/ops.bin',r/'actual-seed-markers.json',r/'seed-bdd-contract.json',r/'tool/src/bin/seed_prefix_zeros.rs',r/'tool/src/bin/seed_support.rs',r/'seed-prefix-source.json',r/'target-tool/release/seed_prefix_zeros',r/'tool/Cargo.toml',r/'tool/Cargo.lock',r/'seed-prefix-build.log',r/'seed-prefix-build.exit']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();before={str(p):sha(p)for p in paths};assert before[str(paths[0])]=='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e'
decl=json.loads((r.parent/'seed-restore-20261016/PREDECLARATION.json').read_text());assert sha(r/'actual-seed-markers.json')==decl['proof_files']['actual-seed-markers.json'];assert sha(r/'seed-bdd-contract.json')==decl['proof_files']['seed-bdd-contract.json'];assert sha(r/'seed-prefix-source.json')==decl['proof_files']['seed-prefix-source.json']
meta=json.loads((r/'seed-prefix-source.json').read_text())
for name,h in meta['files'].items():assert sha(r/name)==h
(d/'before.json').write_text(json.dumps(before,indent=2)+'\n')
with(d/'replay.log').open('w')as out:code=subprocess.run([str(r/'target-tool/release/seed_prefix_zeros')],stdout=out,stderr=subprocess.STDOUT).returncode
(d/'replay.exit').write_text(str(code)+'\n');assert code==0
after={str(p):sha(p)for p in paths};assert before==after
new=json.loads((d/'replay.log').read_text().splitlines()[0]);old=json.loads((r/'seed-prefix-zeros.log').read_text().splitlines()[0]);assert new==old and all(new['exact_zero']);assert new['at']==618858 and len(new['q'])==48
(d/'after.json').write_text(json.dumps(after,indent=2)+'\n')
out=dict(status='PASS HASH-PINNED SAME QUERY PREFIX REPLAY',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),before_after_all_identical=True,files_before_after=before,all48scratch_exact_zero_for_all_symbolic_ABI_inputs_and_MR=True,old_unpinned_query_output_identical=True,old_log_sha256=sha(r/'seed-prefix-zeros.log'),new_log_sha256=sha(d/'replay.log'),original_declaration_sha256=sha(r.parent/'seed-restore-20261016/PREDECLARATION.json'),limitation='This adds provenance to identical prefix proof; old evidence preserved, no circuit/input/census adjustment')
(d/'RECEIPT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
