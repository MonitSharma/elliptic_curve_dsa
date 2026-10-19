import hashlib,io,json,tarfile
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-classical-nine-filter-20261019'
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert (r/'build.exit').read_text().strip()=='0'
bound=json.loads((r/'WATCH_SOURCE.json').read_text());assert all(sha(r/p)==h for p,h in bound.items())
prep=json.loads((r/'PREPARATION.json').read_text());assert all(sha(r/'tool'/p)==v['sha256'] for p,v in prep['files'].items())
names=['build.exit','build.log','BINARY.sha256','BUILD_SOURCE.sha256','build-preflight.json','PREPARATION.json','WATCH_SOURCE.json','ADMISSION-REPAIR.json','validate.py']
files={name:{'bytes':(r/name).stat().st_size,'sha256':sha(r/name)} for name in names}
for name in prep['files']:
    p=r/'tool'/name;files['tool/'+name]={'bytes':p.stat().st_size,'sha256':sha(p)}
manifest={'status':'DISABLED_NEW_SOURCE_FILTER_BUILD_PASS_WAITS_FOR_GATE','binary_sha256':sha(r/'tool/target/release/value_prefilter'),'all_watched_scripts_unchanged':True,'included_files':files,'no_runtime_qualification_or_nonce_selection_claimed':True}
p=r/'build-evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for name in sorted(files):a.add(r/name,arcname=name)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
(r/'BUILD-EVIDENCE.json').write_text(json.dumps({'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'binary_sha256':manifest['binary_sha256']},indent=2)+'\n')
print(json.dumps({'status':manifest['status'],'files':len(files),'binary_sha256':manifest['binary_sha256']}))
