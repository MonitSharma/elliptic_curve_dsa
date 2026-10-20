import hashlib,json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;t=r/'candidate';f=json.loads((r/'SOURCE-FREEZE.json').read_text());revision='63d63c90a25e204d3173d5078f5a0bf12c9d65b7';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*a):return subprocess.check_output(['git','-C',str(t),*a])
if subprocess.run(['git','-C',str(t),'cat-file','-e',revision],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:subprocess.run(['git','-C',str(t),'fetch','origin',revision],check=True)
paths=git('ls-tree','-r','--name-only',revision,'--','src/point_add').decode().splitlines();assert set(paths)==set(f['source_files'])
for p,h in{**f['source_files'],**f['protected_files']}.items():assert hashlib.sha256(git('show',revision+':'+p)).hexdigest()==h,p
assert sha(t/'ops.bin')=='6a8af77b4b0f7e428d52759d555737493dfbf2803a58e0e53d4268557c9fb36f'
(r/'PUBLIC-SOURCE-VERIFICATION.json').write_text(json.dumps({'status':'OFFICIAL_COMMIT_EVERY_SOURCE_AND_PROTECTED_BYTE_MATCHES_VALIDATED_LOCAL','public_submission':'32256595-e0a3-4015-96ab-3422c866ec48','public_source_revision':revision,'local_source_revision':git('rev-parse','HEAD').decode().strip(),'source_files':len(paths),'protected_files':len(f['protected_files']),'exact_parent_stream':str(t/'ops.bin'),'exact_parent_stream_sha256':sha(t/'ops.bin'),'scope':'Read-only official Git-object verification for future parent comparisons. Does not change source, evidence, prior final verdict, commit or submission.'},indent=2)+'\n');print('Official source verified:',len(paths),'source files;',len(f['protected_files']),'protected files')
