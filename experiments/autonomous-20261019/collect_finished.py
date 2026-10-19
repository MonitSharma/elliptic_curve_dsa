"""Preserve completed experiments, including every failed admission/compile."""
import hashlib,io,json,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent.parent
configs={
 'product-classical-nine-proof-20261019':({'run.exit':0,'edits.exit':0},'Eight independent SAT factor identities and ninth XOR identity replay UNSAT. Full-stream audit proves only these replacements and identical R/Hmr order. TRANSFER.json binds18 old accepted runtime artifacts unchanged. New-source runtime acceptance remains disabled. Initial transfer draft used nonexistent RESULT.json; corrected to existing after-eight.json, preserving the draft.'),
 'product-classical-factors-refresh-20261019':({'run.exit':0,'control.exit':0},'Eight exact source-only reductions; protected 512-shot transcripts pass on public and parent4 sources. Guard-ordered17 remains source-only. No scored result.'),
 'product-captured-factors-20261019':({'run.exit':0,'control.exit':0},'Sixteen static reductions pass512 full transcripts. Independent cost proof shows the additional eight never execute; no benefit over simple8. Not a nonce fallback.'),
 'product-captured-factors-native-20261019':({'run.exit':0},'Native byte-identical captured16 prototype,175 source files and17 protected unchanged. Not selected: no additional executed saving and many extra classical bits. No gate or nonce.'),
 'product-classical-factors-native-20261019':({'run.exit':0},'Native byte-identical simple8 prototype,174 source files and17 protected unchanged. Preserved before the independently discovered ninth reduction. No gate or nonce.'),
 'product-factor-cost-proof-20261019':({'run.exit':1,'run-v2.exit':0},'First resource admission failed because the registry did not accept a recorded native worktree cwd; preserved. Corrected admission succeeded. Universal BoolDag proof shows all eight additional captured-only reductions have false guards; not a score.'),
 'product-classical-type-probe-20261019':({'run.exit':0},'Conservative source-only typing found exactly one remaining classical-control CCX after simple8, with true guard. Quantum inputs are unknown. No width reduction proved and no score.'),
 'product-classical-control-expression-20261019':({'run.exit':0},'Exact classical-prefix induction proves q706=bit773 XOR bit774 at op5387927 under true guard, depth0. Source full/pre-tail hashes bound. No circuit change, gate, nonce or score.'),
 'product-classical-nine-20261019':({'run.exit':0},'Native byte-identical parent4+simple8+one unconditional classical-XOR reduction. Four primitive/source-binding controls and512 full transcripts pass;17 protected files unchanged. Statistical qualification is separate; consult qualification/RESULT.json if present. No resource record claimed.'),
}
name=sys.argv[1];exits,note=configs[name];r=root/name
for p,code in exits.items():assert int((r/p).read_text())==code,p
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
with (r/'STATUS.md').open('a') as f:f.write('\n## Completed evidence checkpoint\n\n'+note+'\n')
files={};omitted={}
for p in r.rglob('*'):
    rel=p.relative_to(r)
    if not p.is_file() or p.is_symlink() or any(x in rel.parts for x in ['target','candidate','.git','__pycache__','evidence']):continue
    if p.name.startswith(('evidence','EVIDENCE','LOCAL-VERIFICATION')):continue
    key=rel.as_posix();item={'bytes':p.stat().st_size,'sha256':sha(p)}
    if name=='product-classical-nine-20261019' and ((rel.parts[0]=='qualification' and rel.name!='DECLARATION.json') or rel.name=='gate-v2-nohup.log'):continue
    if p.suffix=='.bin' or p.stat().st_size>5_000_000:omitted[key]=item
    else:files[key]=item
manifest={'server_directory':str(r),'captured_utc':datetime.now(timezone.utc).isoformat(),'terminal_exits':exits,
          'scope':note,'included_files':files,'larger_files_preserved_on_server':omitted}
p=r/'evidence.tar.gz'
with tarfile.open(p,'x:gz') as a:
    for key in sorted(files):a.add(r/key,arcname=key)
    raw=(json.dumps(manifest,indent=2)+'\n').encode();m=tarfile.TarInfo('SNAPSHOT-MANIFEST.json');m.size=len(raw);a.addfile(m,io.BytesIO(raw))
receipt={'archive':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'files':len(files),'omitted':omitted}
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='omitted'}))
