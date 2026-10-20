import hashlib,json,tarfile
from pathlib import Path
r=Path(__file__).resolve().parent;a=r/'attempt-v2';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert not(r/'EVIDENCE-MANIFEST.json').exists();assert(r/'run.exit').read_text().strip()=='1'and(r/'run-v2.exit').read_text().strip()=='1'
assert'PermissionError'in(r/'replay.log').read_text();result=json.loads((a/'PAIRED-RESULT.json').read_text());assert not result['all_four_final_register_hashes_match_including_failed_inputs'];assert result['value_failing_shot_identities_equal']and not result['different_other_lanes']
assert all(x['parent_value_fails']and x['candidate_value_fails']for x in result['different_target_lanes']);assert result['summaries']['candidate']['dirty_shots']==0
for name,row in result['summaries'].items():assert sha(a/(name+'.jsonl'))==row['rows_sha256']
assert(a/'original-parent.jsonl').read_bytes()==(r/'original-parent.jsonl').read_bytes()
freeze=json.loads((a/'REPLAY-FREEZE.json').read_text());assert freeze['label']==result['label']and freeze['batches']==512
for info in freeze['streams'].values():assert sha(Path(info['path']))==info['sha256']
croot=r.parent/'breakthrough-phase-pebble-plan7-20261020';cf=json.loads((croot/'SOURCE_FREEZE.json').read_text());assert all(sha(croot/'observer'/p)==h for p,h in{**cf['source_files'],**cf['protected_files']}.items())
summary={'status':'FAILED_FULL_OUTPUT_EQUALITY_NONCOMPETITIVE','different_target_lanes':len(result['different_target_lanes']),'different_output_batches':len(result['different_output_batches']),'all_target_differences_already_value_failing_in_both':True,'candidate_source_freeze_sha256':sha(croot/'SOURCE_FREEZE.json'),'candidate_native_evidence_manifest_sha256':sha(croot/'EVIDENCE-MANIFEST.json'),'original_parent_control_repeated_identically':True,'result':result,'scope':'Keep failed output-equivalence verdict. Cause not isolated; no universal proof, scored improvement, final gate or nonce.'}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(summary,indent=2)+'\n')
files=[p for p in sorted(r.rglob('*'))if p.is_file()and p.name not in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json']and'__pycache__'not in p.parts]
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':summary},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p in files+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size};(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
