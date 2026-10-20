import difflib,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[2];r=Path(__file__).resolve().parent;out=root/'experiments/breakthrough-public8b-repeat-final-20261020';data=json.loads((out/'submission-status.json').read_text());s=data['submission'];assert s['officialMetrics']=={'qubits':1464,'toffoli':751020}and s['officialScore']==1099493280 and s['rejectionReason']=='score did not improve current best';review=json.loads((out/'FINAL-VERIFICATION.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'id':s['id'],'url':'https://api.ecdsa.fail/api/submissions/'+s['id'],'official_metrics':s['officialMetrics'],'official_product':s['officialScore'],'api_status':s['status'],'rejection_reason':s['rejectionReason'],'public_source':s['submissionCommitSha'],'local_source':review['source_revision'],'source_archive_sha256':review['source_archive_sha256'],'source_patch_sha256':review['source_patch_sha256'],'local_evidence_sha256':json.loads((out/'LOCAL-VERIFICATION.json').read_text())['archive_sha256'],'official_status_sha256':sha(out/'submission-status.json'),'model':'GPT-6 sol','harness':'Codex','scope':'Official metrics reproduce local complete benchmark. Improves independent minimum T by7 versus previous751027; product incumbent remains lower. Fresh paired census circuit saving3 with SE0; packet variation accounts for remaining difference. Auto-submission authorization persists.'};(out/'OFFICIAL-RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
status=f"""# Official Q1464/T751020 result

[Submission{s['id']}](https://api.ecdsa.fail/api/submissions/{s['id']})
officially reproduced **Q1464/T751020**, product1099493280.
API status rejected only because the global product score did not improve.
It is the independent public Toffoli minimum at the09:26UTC refresh.

All9024 unchanged benchmark shots pass; sole fresh32768x64 gate passes.
Lowest nonce52 among64 production screens, overrun53..64 and additional
partial controls1..8/24 protected full-state scalar batches disclosed.
Model **GPT-6 sol**, harness **Codex**; direct dependency8b declared.
The circuit saves exactly3 Toffolis on every paired census batch; this
protected packet improves7 rounded Toffolis versus the parent's packet.

Public source{s['submissionCommitSha']}; local source{review['source_revision']}.
Full disclosures in SUBMISSION-NOTE.md; all145 final evidence members and
194 source members verify locally. OFFICIAL-RESULT.json binds receipts.
The user authorized ongoing automatic submission of new verified improvements.
"""
(out/'STATUS.md').write_text(status);patch=[]
changes={
 'Status: **validating**, with no official score yet.':'**Officially reproduced** at Q1464/T751020. Promotion was rejected only because the global product score did not improve.',
 'API status validating, job queued.':'Officially reproduced Q1464/T751020, public source63d63c90. API rejected promotion only because the global product did not improve.',
 'No official score for\nthis new source is claimed yet.':'Official metrics match the local unchanged benchmark.',
 '##20 October2026,17:00SGT:':'## 20 October2026,17:00SGT:'
}
for path in ['README.md','docs/AGENT_HANDOFF.md','docs/research-plan.md','docs/results-status.md']:
 before=subprocess.check_output(['git','show',':'+path],cwd=root).decode();after=before
 for a,b in changes.items():after=after.replace(a,b)
 patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
 p=root/path;raw=p.read_bytes()
 for a,b in changes.items():
  aa=a.replace('\n','\r\n').encode();bb=b.replace('\n','\r\n').encode()
  if aa in raw:raw=raw.replace(aa,bb)
  else:raw=raw.replace(a.encode(),b.encode())
 p.write_bytes(raw)
p=r/'checkpoint-repeat-official-index.patch';p.write_bytes(''.join(patch).encode());subprocess.run(['git','apply','--cached','--check',str(p)],cwd=root,check=True);subprocess.run(['git','apply','--cached',str(p)],cwd=root,check=True);print(s['id'],s['officialMetrics'],s['submissionCommitSha'])
