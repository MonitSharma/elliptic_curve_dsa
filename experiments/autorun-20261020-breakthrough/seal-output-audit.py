"""Preserve the failed equality verdict and its same-input classification."""
import hashlib,json,os,shutil,tarfile
from pathlib import Path
from datetime import datetime,timezone
r=Path('/home/hclau/ecdsa_research/breakthrough-output-audit-20261020');assert not(r/'EVIDENCE-MANIFEST.json').exists()
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert(r/'run.exit').read_text().strip()=='1'and(r/'run-v2.exit').read_text().strip()=='0'
f1=json.loads((r/'TOOL-SOURCE-FREEZE.json').read_text());f2=json.loads((r/'TOOL-SOURCE-FREEZE-v2.json').read_text());failed=json.loads((r/'OUTPUT-DIAGNOSTIC.json').read_text());classification=json.loads((r/'OUTPUT-DIFFERENCE-CLASSIFICATION.json').read_text())
for sub,f in[('tool',f1),('tool-v2',f2)]:
 assert all(sha(r/sub/p)==h for p,h in f['source_files'].items());assert len(f['protected_dependency_files'])==17;assert all(sha(Path(p))==h for p,h in f['protected_dependency_files'].items())
assert not failed['all_four_final_register_hashes_match_including_failed_inputs']
assert classification['same_label_and_all_old_fields_reproduced']and classification['value_failing_shot_identities_equal']and classification['target_differences_confined_to_both_value_failing']
assert len(classification['different_target_lanes'])==11 and not classification['different_other_lanes']
v1=r/'bin/output-v1';v2=r/'tool/target/release/product_paired_diagnostic'
assert sha(v1)==failed['output_binary_sha256']and sha(v2)==classification['observation_binary_sha256'];shutil.copyfile(v2,r/'bin/output-v2')
original=[json.loads(l)for l in(r/'original-parent.jsonl').read_text().splitlines()];parent=[json.loads(l)for l in(r/'parent.jsonl').read_text().splitlines()]
assert[{k:v for k,v in row.items()if k!='output_sha3_256'}for row in parent]==original
for name in['parent','candidate']:
 before=[json.loads(l)for l in(r/(name+'.jsonl')).read_text().splitlines()];after=[json.loads(l)for l in(r/(name+'-v2.jsonl')).read_text().splitlines()]
 assert[{k:v for k,v in row.items()if k not in['target_lane_hashes','other_lane_hashes']}for row in after]==before
runtime={'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'v1_full_output_equality_verdict':'FAILED_PRESERVED','classification':classification,
 'protected_dependency_files_checked':17,'binaries_retained_on_server':{str(p):sha(p)for p in[r/'bin/output-v1',r/'bin/output-v2']},'official_benchmark_and_candidate_sources_unchanged':True,'no_final_gate_nonce_or_scored_result':True}
(r/'TERMINAL-AUDIT.json').write_text(json.dumps(runtime,indent=2)+'\n');files=[]
for current,dirs,names in os.walk(r):
 dirs[:]=sorted(d for d in dirs if d not in['target','bin','__pycache__'])
 for n in sorted(names):
  p=Path(current)/n
  if'resource-preflight'in n or n in['evidence.tar.gz','EVIDENCE-MANIFEST.json','PACKAGE-RESULT.json','LOCAL-VERIFICATION.json']:continue
  files.append(p)
(r/'EVIDENCE-MANIFEST.json').write_text(json.dumps({'files':{p.relative_to(r).as_posix():sha(p)for p in files},'terminal_audit':runtime},indent=2)+'\n')
with tarfile.open(r/'evidence.tar.gz','w:gz')as archive:
 for p in sorted(files)+[r/'EVIDENCE-MANIFEST.json']:archive.add(p,arcname=p.relative_to(r).as_posix())
receipt={'archive_sha256':sha(r/'evidence.tar.gz'),'archive_bytes':(r/'evidence.tar.gz').stat().st_size,'members':len(files)+1,'manifest_sha256':sha(r/'EVIDENCE-MANIFEST.json')}
(r/'PACKAGE-RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
