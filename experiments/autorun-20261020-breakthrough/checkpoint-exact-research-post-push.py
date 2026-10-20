import gzip,hashlib,json,subprocess,tarfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;ex=a.parent
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip()
dirs=['breakthrough-sat-proof-check-ram-20261020','breakthrough-sat-proof-tools-v5-20261020','breakthrough-value-semantic-guards-audit-20261020','breakthrough-value-semantic-guards-audit-v2-20261020','breakthrough-value-cofactor-qualification-20261020','breakthrough-local-de8-replay-20261020','breakthrough-global-prefix-component-20261020','breakthrough-global-prefix-component-v2-20261020','breakthrough-global-prefix-component-v3-20261020','breakthrough-global-prefix-component-v4-20261020','breakthrough-de8-second-cache-20261020','breakthrough-global-phase-component-20261020','breakthrough-global-phase-component-v2-20261020','breakthrough-value-normalized-aig-20261020','breakthrough-de8-generic-repeat-20261020','breakthrough-de8-generic-repeat-v2-20261020','breakthrough-value-dominance-audit-20261020','breakthrough-value-boolean-reset-audit-20261020']
excluded={'local-tool','local-protected','tool-repos','observer','candidate','target','__pycache__'}
for name in dirs:
 r=ex/name;assert r.is_dir();(r/'.gitattributes').write_text('* -text\n')
 p=r/'.gitignore';prior=p.read_text()if p.exists()else''
 for line in ['local-tool/','local-protected/','tool-repos/','observer/','candidate/','target/','__pycache__/','*.ops.bin','*.cnf','*.drat','*resource-preflight*','evidence.tar.gz','normalized-value-ir.bin.zst']:
  if line not in prior.splitlines():prior+=line+'\n'
 p.write_text(prior)
 f=json.loads((r/'SOURCE-FREEZE.json').read_bytes())if(r/'SOURCE-FREEZE.json').exists()else{}
 names=f.get('tool_source_files',f.get('source_files',{}))
 tool=r/'local-tool'
 if tool.is_dir():
  if names and all((tool/n).is_file()for n in names):
   assert all(sha(tool/n)==h for n,h in names.items()),name
  else:names={n:sha(tool/n)for n in ['Cargo.toml','Cargo.lock','io.rs','discover.rs']if(tool/n).is_file()}
  with tarfile.open(r/'preserved-tool-source.tar.gz','w:gz')as archive:
   for n in sorted(names):archive.add(tool/n,arcname=n,recursive=False)
  (r/'PRESERVED-TOOL-SOURCE.json').write_text(json.dumps({'files':names,'archive_sha256':sha(r/'preserved-tool-source.tar.gz'),'scope':'Original frozen files checked where pre-test freeze exists. Partial setup-failure files are preserved as found, not recast as a pre-test freeze.'},indent=2)+'\n')
 for p in r.glob('*.jsonl'):
  if p.stat().st_size>1000000:p.with_suffix(p.suffix+'.gz').write_bytes(gzip.compress(p.read_bytes(),mtime=0))
 files={}
 for p in r.rglob('*'):
  rel=p.relative_to(r)
  if any(part in excluded for part in rel.parts):continue
  if not p.is_file()or p.suffix in['.cnf','.drat','.jsonl']or p.name.endswith('ops.bin')or'resource-preflight'in p.name or p.name in['evidence.tar.gz','LOCAL-CHECKPOINT-MANIFEST.json','normalized-value-ir.bin.zst']:continue
  assert p.stat().st_size<20_000_000,(name,rel,p.stat().st_size)
  files[rel.as_posix()]=sha(p)
 (r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'status':'COMPLETED_OR_FAILED_RESEARCH_PRESERVED_NOT_SCORED','files':files,'scope':'Original outcomes and failures retained; component/proxy/verifier-only counts are not quantum scores. Original sealed evidence remains authoritative.'},indent=2)+'\n')
assessment=ex/'breakthrough-assessment-20261020';snap=assessment/json.loads((assessment/'LATEST.json').read_bytes())['snapshot'];records=json.loads((snap/'PUBLIC-RECORDS.json').read_bytes());raw=(snap/'public-submissions.json').read_bytes();(snap/'public-submissions.json.gz').write_bytes(gzip.compress(raw,mtime=0));(snap/'.gitattributes').write_text('* -text\n');(snap/'SNAPSHOT-MANIFEST.json').write_text(json.dumps({'raw_api_sha256':hashlib.sha256(raw).hexdigest(),'files':{n:sha(snap/n)for n in ['PUBLIC-RECORDS.json','leader-product.json','leader-qubits.json','leader-toffoli.json','public-submissions.json.gz']}},indent=2)+'\n')
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),push_status='EXPLICIT_USER_APPROVAL_EXECUTED: exact41f769ec44e40c915c3149d8332c15b10bca71f8 pushed to main by verified fast-forward. Newer commits remain local; do not push newer HEAD under this exact approval.',latest_public_snapshot=snap.relative_to(root).as_posix(),public_product=records['leaders']['product'],public_width=records['leaders']['qubits'],public_toffoli=records['leaders']['toffoli'],global_product_goal_status='ACTIVE_UNFINISHED',active_jobs=[{'environment':'Windows hidden foreground WSL','pid':34560,'directory':'breakthrough-value-normalized-aig-v2-20261020','purpose':'Native29PASS. Fixed oldsource/firstfailure, complete semantic/cofactor normalization then unchanged qualified AIG/CNF and24+3protected controls. Source export only; no rejection certificate yet.'},{'environment':'Windows hidden foreground WSL','pid':47240,'directory':'breakthrough-de8-generic-repeat-v3-20261020','purpose':'Fixed2newcacheleases on exactde8 plus second unchanged generic pipeline; nativephase/faultcontrol beforegeneration. Component only, no gate/nonce/benchmark.'}],server_status='SSH restored, hostname LHC-104-070. Dominance15/24protected and Boolean-reset17/24protected auditsDONE, both26archive members locallyverified, no knownbits. Existing unrelated workloads untouched; no remote research restarted.',proof_status='Kissat UNSAT is UNCHECKED. Same proof RAM DRAT check900s returned0 but explicitly s TIMEOUT, no VERIFIED: INCONCLUSIVE. No nonce rejected.',exact_component_status='Globalprefixnative14 finds3T action lowerings on exactde8, public1829 no-op. Phaseextensionnative18PASS findsNO additional lowering on eitherparent. Secondcache native9 yields2T andexact same output for0/16/64extra donorbudgets; no actualrecord claimed.',semantic_status='Native24/120protected exactsemantic normalization liveRNG393. Boundedcofactor native25/120protected liveRNG310, no knownbits/certificates. Above-boundnegativecontrol qualification native26PASS; productioncore unchanged.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
prefix='''## 21 October 2026: approved push completed; exact research continues

The user explicitly approved commit41f769ec, which was pushed by normal
fast-forward to origin/main. Newer research commits remain local; this approval
does not authorize pushing a newer endpoint. Fresh22:56UTC1716records unchanged:
T746114/Q1464/de8, product932057476/Q1234/T755314/1829, width669/1df8.
Global product goal ACTIVE. No new benchmark/finalgate/nonce/submission.

SSH restored; LHC-104-070 available178GiB/144threads at preflight. Completed
dominance15 and Boolean-reset17native audits each24protected comparisons and
zero knownoutputbits. Both26member archives fullyverified locally in separate
original-evidence directories, preserving local.gitignore differences. No
existing remote work restarted/stopped; chemistry/QOB untouched.

Exactsemantic guard normalization24native/120protected reduces liveRNG5690
to393; exactboundedcofactor25native/120protected reaches310, still no known or
certifiedwrongbits. Above-bound cofactor negativecontrol26native qualification
passes with productioncore unchanged. Fixed firstoldfailure Kissat UNSAT remains
UNCHECKED: sameproof RAM DRAT900s returns0 but says s TIMEOUT, never VERIFIED.
No nonce rejected and no old gate verdict rerun.

Currentde8 source205/protected17 reproduces exactpublicframe131712 locally.
Globalprefix native14:3exact action lowerings, no public1829 rewrite. Second
cache native9:2fresh leases/849proposed,2proxyT, same output on0/16/64extra
donors; width remains1464. Phaseextension native18 has no further saving on
eitherparent. Original phasefixture16/18 failures preserved, V2 fixes only an
invalid repeated-wire test and an expectation (Zproduct precedesCZ), production
unchanged. All these are COMPONENTS, not scores or verified new records.

Running fixed normalized-AIGv2 native29PASS with24+3protected qualification,
and exact2cache+secondgeneric sourcev3. Prior iterator compile failure and
Windows text/binary patch setupfailures retained; none ran pointinputs/gates.
Any competitive finalsource needs own frozen gate against current exactparent,
ascendinglowestpassingnonce and unchangedbenchmark before automatic submission.
'''
for rel in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/rel;data=prefix.encode()+b'\n'
 if not p.read_bytes().startswith(data):p.write_bytes(data+p.read_bytes())
 blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+rel)).decode().strip();mode=git('ls-tree','HEAD','--',rel).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+rel],check=True)
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n'+prefix+'\n')
scripts=['global-prefix-simplify.rs','global-prefix-simplify-v3.rs','global-prefix-simplify-v4.rs','prepare-cofactor-qualification.py','prepare-de8-second-cache.py','prepare-global-prefix-component.py','prepare-global-prefix-component-v2.py','prepare-global-prefix-component-v3.py','prepare-global-prefix-component-v4.py','prepare-local-de8-replay.py','prepare-ram-proof-check.py','run-ram-proof-check.py','prepare-value-semantic-guards-audit.py','prepare-value-semantic-guards-audit-v2.py','value-semantic-guards.rs','prepare-global-phase-component.py','prepare-global-phase-component-v2.py','prepare-normalized-value-aig.py','prepare-normalized-value-aig-v2.py','prepare-post-outage-collection.py','seal-post-outage.py','collect-post-outage.py','collect-post-outage-preserving.py','prepare-de8-generic-repeat.py','prepare-de8-generic-repeat-v2.py','prepare-de8-generic-repeat-v3.py','checkpoint-exact-research-post-push.py','CURRENT-ACTIVE.json','LOG.md']
paths=['experiments/'+n for n in dirs]+['experiments/autorun-20261020-breakthrough/'+n for n in scripts]+[snap.relative_to(root).as_posix(),'experiments/breakthrough-assessment-20261020/LATEST.json']
for name in ['breakthrough-value-normalized-aig-v2-20261020','breakthrough-de8-generic-repeat-v3-20261020']:
 r=ex/name
 paths.extend(p.relative_to(root).as_posix()for p in r.iterdir()if p.is_file()and p.name in ['SOURCE-FREEZE.json','PLAN.md','.gitignore','.gitattributes','audit.rs','aig.rs','FAILURE-FIXTURES.json','verify-input.py','verify.py','run-local.sh','source.patch','point-add-source.tar.gz','foreground-windows.pid'])
subprocess.run(['git','-C',str(root),'add','--',*paths,':!**/public-submissions.json'],check=True)
staged=git('diff','--cached','--name-only').decode().splitlines()
assert all(any(p==q or p.startswith(q+'/')for q in paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'])for p in staged)
assert not any(any('/'+bad+'/'in p for bad in excluded)or p.endswith('ops.bin')or p.endswith('.cnf')or p.endswith('.drat')for p in staged)
subprocess.run(['git','-C',str(root),'commit','-q','-m','Preserve exact phase, cache and semantic proof research; record approved push'],check=True)
print(git('rev-parse','HEAD').decode().strip())
