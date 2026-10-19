"""Preserve completed experiments, including every failed admission/compile."""
import hashlib,io,json,sys,tarfile
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent.parent
configs={
 'scalar-window-20261019':({'run.exit':0},'Pure public-input backend window experiment. Each window matches655360 fresh public scalar pairs against the frozen backend, including edges and partial batches. Frozen20 median1.53631s beats new20/22/24 at2.27685/1.98899/2.44487s; no reliable production benefit. Keep the original window20 library. Reference binary outputs and libraries stay server-side with hashes. No circuit, nonce, active runtime or score changed.'),
 'rail-sx-20261019':({'run.exit':0,'branch.exit':0},'Exact sign-extension experiment:287100 primitive cases, all widths1..319,262144 frozen advisory flags and517 adversarial/partial/changed-table cases match. Dynamic-index v1 is correct but slower (0.560x). Fixed-branch variant gives1.173x kernel median. Complete-prefix evidence is mixed, so keep the active runtime unchanged. No circuit, new-source nonce or score.'),
 'rail-sx-prefix-20261019':({'run.exit':0},'Disabled helper-only parent4 copy changes only advisory library path and its explicit hash check; all rows match the qualified prefix. Own seed and partial zero-MR/scalar shadows pass. Three paired512-nonce timings have median ratio1.0496 but two pairs lose: no reliable end-to-end gain and no production port.3083 repeated diagnostic attempts within the already screened1..4096; no new unique nonce or selection. No active circuit/runtime changed.'),
 'product-classical-twelve-native-20261019':({'run.exit':0},'Native twelve-static-reduction prototype reproduces raw2ef31475... byte for byte,180 source files and17 protected unchanged. All18 primitive/table/source controls pass. Source frozen before classical9 verdict; no nonce or official benchmark. Independent gate plan fixed before valid-point pilot; its machine-readable final declaration/census has not started.'),
 'product-classical-twelve-proof-20261019':({'run.exit':0,'component.exit':0},'Three independently serialized source-bound factor identities replay UNSAT. Full-stream edit audit proves every other op and R/Hmr event unchanged. TRANSFER binds the full earlier certificate chain. Fresh4096 valid-point control saves1.00341796875 executed T per point (SE0.010534977), with every paired value/phase/dirty diagnostic identical. This is component/source evidence only, not a statistical gate verdict, nonce screen or scored record.'),
 'product-classical-factors-wide-20261019':({'run.exit':101,'run-v2.exit':0},'Compile-only v1 failed on an inner doc comment inside include!, preserved with complete source/logs. V2 changes that comment only. Seven primitive/table controls pass; cap7 reproduces the frozen simple8 stream exactly. Predetermined cap9 on classical9 removes3 additional static CCX and saves493 executed Toffolis across512 full raw transcripts, with Q1234 and every q/c/phase/physical-RNG value identical. This is source/component evidence, no scored record, gate or nonce.'),
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
    if p.suffix in ['.bin','.so','.o','.a'] or p.stat().st_size>5_000_000:omitted[key]=item
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
