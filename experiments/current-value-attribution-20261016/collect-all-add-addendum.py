from pathlib import Path
import hashlib,json,tarfile,shutil
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016');n='all-add-attribution-addendum-v3';d=r/n;assert not d.exists();d.mkdir();assert(r/'all-add-analysis.exit').read_text().strip()=='0'
files=['prepare-all-add-replay.py','run-all-add-replay.sh','analyze-all-adds.py','join-all-add-stages.py','ALL-ADD-REPLAY-DECLARATION.json','ALL-ADD-ATTRIBUTION.json','all-add-first-global-join.json','all-add-first-global-join.log','all-add-replay.log','all-add-replay.exit','all-add-build.log','all-add-build.exit','all-add-prepare.log','all-add-prepare.exit','all-add-replay-preflight.log','all-add-stream-source-before.sha256','all-add-stream-source-after.sha256','all-add-analysis.log','all-add-analysis.exit','tool/src/all_add_runtime.rs','tool/src/bin/current_all_adds.rs']
files.extend(str(p.relative_to(r))for p in(r/'all-add-setup-whitespace-negative').rglob('*')if p.is_file())
for f in files:
 q=d/f;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(r/f,q)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={n:sha(r/n)for n in['attribution-checkpoint-v1.tar.gz','phase-attribution-addendum-v2.tar.gz']}
(d/'BASE-PINS.json').write_text(json.dumps(dict(depends_on=pins,source_stream_sha256='2a522394cdf3e6a0df7784ad4db761030933c1f7ccd0ff8e641d68ec7a4dab3e',same431_witnesses_413contexts=True,no_candidate=True,all89local_add_errors_at_divide131=True,all89first_global_stage_divide_and_first_PAY_divide131=True,not_an_end_to_end_repair_count=True),indent=2)+'\n')
manifest={str(p.relative_to(d)):dict(bytes=p.stat().st_size,sha256=sha(p))for p in d.rglob('*')if p.is_file()};(d/'MANIFEST.json').write_text(json.dumps(dict(files=manifest,depends_on=pins),indent=2)+'\n');p=r/(n+'.tar.gz')
with tarfile.open(p,'w:gz')as tf:tf.add(d,arcname=n)
with tarfile.open(p)as tf:
 for f,v in manifest.items():x=tf.extractfile(n+'/'+f).read();assert len(x)==v['bytes']and hashlib.sha256(x).hexdigest()==v['sha256']
out=dict(status='PASS',archive=str(p),sha256=sha(p),bytes=p.stat().st_size,verified_members=len(manifest));(r/(n+'-receipt.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
