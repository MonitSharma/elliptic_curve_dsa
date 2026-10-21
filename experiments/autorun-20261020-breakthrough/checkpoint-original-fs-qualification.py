from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess,tarfile
root=Path(__file__).resolve().parents[2];a=Path(__file__).parent;r=a.parent/'breakthrough-original-fs-fixed-audit-20261021';sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args,input=None):return subprocess.check_output(['git','-C',str(root),*args],input=input)
assert not git('diff','--cached','--name-only').strip();assert(r/'run.exit').read_text().strip()=='0';f=json.loads((r/'SOURCE-FREEZE.json').read_bytes());assert all(sha(r/'local-tool'/n)==h for n,h in f['source_files'].items());v=json.loads((r/'RESULT.json').read_bytes());audit=v['fixed_original_FS_audit'];assert audit['new_nonce_screens']==0 and audit['production_nonce_rejections']==0;controls=audit['fixed_controls'];assert [c['nonce']for c in controls]==list(range(1,9));assert all(c['known_output_bits']==32768 for c in controls);assert [c['certified_wrong_shots']for c in controls]==[1,1,1,1,1,1,0,1]
with tarfile.open(r/'preserved-tool-source.tar.gz','w:gz')as ar:
 for n in sorted(f['source_files']):ar.add(r/'local-tool'/n,arcname=n,recursive=False)
with tarfile.open(r/'preserved-tool-source.tar.gz')as ar:
 for m in ar.getmembers():assert hashlib.sha256(ar.extractfile(m).read()).hexdigest()==f['source_files'][m.name]
(r/'PRESERVED-TOOL-SOURCE.json').write_text(json.dumps({'files':f['source_files'],'archive_sha256':sha(r/'preserved-tool-source.tar.gz')},indent=2)+'\n')
files={}
for p in r.rglob('*'):
 rel=p.relative_to(r)
 if 'local-tool'in rel.parts or'__pycache__'in rel.parts:continue
 if p.is_file()and p.name!='LOCAL-CHECKPOINT-MANIFEST.json':assert p.stat().st_size<20_000_000;files[rel.as_posix()]=sha(p)
(r/'LOCAL-CHECKPOINT-MANIFEST.json').write_text(json.dumps({'files':files,'scope':'OriginalFS fixed old-control certificate qualification only. No newnonce or retiredsearch resumption, sourcecandidate/gate/benchmark/submission.'},indent=2)+'\n')
state=json.loads((a/'CURRENT-ACTIVE.json').read_bytes());state.update(at_utc=datetime.now(timezone.utc).isoformat(),active_jobs=[],original_FS_fixed_replay_result={'status':'PASS_FIXED_OLD_CONTROLS_NOT_PRODUCTION','native_controls':44,'fresh_arbitrary_full_protected_value_comparisons':24,'selected_actual_mutated_stream_full_protected_value_comparisons':24,'fixed_nonces':list(range(1,9)),'old_recorded_batches':[7,3,5,5,4,1,0,29],'known_output_bits_per64lanes':32768,'certified_wrong_shots':[1,1,1,1,1,1,0,1],'scalar_packet_fullseed_prefixseed_equality':True,'original_first128_postinput_rng_bytes_equality':True,'new_nonce_screens':0,'production_nonce_rejections':0,'retired_search_resumed':False,'scope':'Exact OLD6192/cache188c. Seven originalclassical witnesses certified, nonce7phaseonly leftunrejected. Allsourcepointvalues quantified over arbitrary measurement words,48protected valuecomparisons. No acceptance/phase/dirty shortcut. Fresh changedcandidate requires its own passedgate/sourcecache/ORIGINAL_FS qualification.'},next_product_front='Prepare actual finished exact-public semantic CCXtoCX source187files/fullcanonical binding after refreshedrecords. No finalgate yet for thiscomponent. OriginalFS qualification now PASS for fixedalready-screenedoldcontrols; next verificationresearch is fast advisorynominator (modelneverrejects) + packedexactfailureproof + fullstatefallback. Keep obsolete searches/gatesfinal and no newproductionnonce before ownfinishedPASSgate.')
(a/'CURRENT-ACTIVE.json').write_text(json.dumps(state,indent=2)+'\n')
addition='''## 21 October 2026: ORIGINAL_FS fixed-control certificate qualification PASS

Native44 and48fresh complete protected VALUE comparisons PASS on exactOLD6192/
cache188c0947:24arbitraryinputs and3patterns at each8actualmutatedcontrolstreams.
Fixedalready-screenednonces1..8/batches7,3,5,5,4,1,0,29 were declared before
execution. Fullprotectedfiat_shamir_seed versus prefixstate+qualifiedtail agrees
on ALL9024attempt scalarbytes and first128postinputRNGbytes for everycontrol.
Curve-checkskip-without-refill membership through original selectedbatch.
All512outputbitsknown for every512points:sevenoriginalclassicalwitnesses each
certify1wrongshot; nonce7phaseonly certifies0 and remainsforfullstatefallback.
Originalverdicts neverrejudged. No acceptance/phase/dirtycertificate claimed.

No newnonce screened/rejected and retired1..65536search NOT resumed/extended.
No newcircuit/finalgate/benchmark/submission. Compact backend currentparent
32,768-point qualification remainsseparate; oldcache neverclaimedcurrentproof.
Next:finishedcurrentpublic exactsingleCCXtoCX source and solefreshgate after
recordrefresh; productionsearch stillrequirespassedgate/owncache/originalFS
qualification. Advisorymodel maynominateonly; exactproof or unchangedfullstate
mustconfirm everyrejection. Globalproductgoal ACTIVE; approved41pushdone,
newercommitslocal. PreserveQ692/useredits/unrelatedserverjobs/chemistry.

'''
for rel in ['docs/research-plan.md','docs/AGENT_HANDOFF.md']:
 p=root/rel;data=addition.encode()
 if not p.read_bytes().startswith(data):p.write_bytes(data+p.read_bytes())
 blob=git('hash-object','-w','--stdin',input=data+git('show','HEAD:'+rel)).decode().strip();mode=git('ls-tree','HEAD','--',rel).decode().split(' ',1)[0];subprocess.run(['git','-C',str(root),'update-index','--add','--cacheinfo',mode+','+blob+','+rel],check=True)
with(a/'LOG.md').open('a',encoding='utf-8')as log:log.write('\n'+addition)
scripts=['original-fs-fixed-audit.rs','prepare-original-fs-fixed-audit.py','checkpoint-original-fs-qualification.py','CURRENT-ACTIVE.json','LOG.md'];paths=[r.relative_to(root).as_posix()]+[(a/n).relative_to(root).as_posix()for n in scripts];subprocess.run(['git','-C',str(root),'add','--',*paths],check=True);allowed=paths+['docs/research-plan.md','docs/AGENT_HANDOFF.md'];assert all(any(p==q or p.startswith(q+'/')for q in allowed)for p in git('diff','--cached','--name-only').decode().splitlines());subprocess.run(['git','-C',str(root),'commit','-q','-m','Qualify original Fiat-Shamir fixed old-control value certificates'],check=True);print(git('rev-parse','HEAD').decode().strip())
