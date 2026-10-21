from pathlib import Path
import hashlib,json,tarfile,ast
a=Path(__file__).parent;ex=a.parent;r=ex/'breakthrough-de8-repeat-final-20261020';old=ex/'breakthrough-exact-witness-final-20261020'
def adapt(s):
 for x,y in [('breakthrough-exact-witness-finished-20261020','breakthrough-de8-repeat-finished-20261020'),('breakthrough-exact-witness-final-gate-20261020','breakthrough-de8-repeat-final-gate-20261020'),('breakthrough-exact-witness-nonce-20261020','breakthrough-de8-repeat-nonce-20261020'),('full259-witness-final-20261020-v1','cache-repeat-generic-final-20261020-v1'),('747218','746114')]:s=s.replace(x,y)
 return s
s=(old/'seal.py').read_text();s=adapt(s[:s.index("proof=ws/'breakthrough-exact-witness-context-20261020'")]).replace('28e443bcc2f3dc0793c6a416a496b07cfbeb4c4f','bd6672a873f85953eb7c5197e9cf46982ce19708').replace('==205','==206').replace("'source_files':205","'source_files':206").replace('Exact full259 witness andsharedsum withnewcacheproofs at nonce','Exact two product holds and repeated generic simplification at nonce').replace('Complete unchanged benchmark of exactfull259 witness/sharedsum andfreshlyproven existing-wire caches on strong arithmetic. Targets independentT versus public2bd; no globalproduct claim.','Complete unchanged benchmark of exact two new context cache holds and a repeated unchanged generic pipeline. Targets independentT versus currentde8; no globalproduct claim.')
s+=(a/'de8-repeat-sealer-tail.py').read_text();ast.parse(s);(r/'seal.py').write_text(s)
s=(old/'review.py').read_text();s=s.replace("assert(r/'run.exit').read_text()", "research=r.parent/'breakthrough-de8-repeat-finished-20261020'\n while not(research/'pipeline.exit').exists():assert time.time()-start<21600;time.sleep(2)\n assert(research/'pipeline.exit').read_text().strip()=='0'\n assert(r/'run.exit').read_text()")
ast.parse(s);(r/'review.py').write_text(s)
s=(old/'submit.py').read_text().replace('2bd0f979-ab55-4f91-8133-68a08febaa67','de8bac6a-afff-479e-b716-8cbf2dce6c73').replace("'source_files':205","'source_files':206");ast.parse(s);(r/'submit.py').write_text(s)
(r/'wait-official.py').write_text((old/'wait-official.py').read_text())
s=(old/'verify-official-source.py').read_text().replace('len(paths)==205','len(paths)==206').replace("747218-b['rounded_mean_executed_toffoli']","746114-b['rounded_mean_executed_toffoli']");ast.parse(s);(r/'verify-official-source.py').write_text(s)
names=['breakthrough-de8-second-cache-20261020','breakthrough-de8-generic-repeat-v3-20261020','breakthrough-de8-generic-development-20261020'];bundle=a/'de8-repeat-proof-package.tar.gz'
with tarfile.open(bundle,'w:gz')as archive:
 for name in names:
  for p in(ex/name).iterdir():
   if p.is_file()and not p.name.endswith('ops.bin')and p.suffix!='.jsonl':archive.add(p,arcname=name+'/'+p.name,recursive=False)
 for n in ['seal.py','review.py','submit.py','wait-official.py','verify-official-source.py']:archive.add(r/n,arcname=r.name+'/'+n,recursive=False)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest();(a/'DE8-REPEAT-PACKAGE-TRANSFER.json').write_text(json.dumps({'archive_sha256':sha(bundle),'scope':'Supplement original immutable local proof/development evidence and reviewed seal/upload scripts. Upload still requires complete benchmark PASS, currentrecord improvement, every local evidence/source member verified. No automatic blindupload.'},indent=2)+'\n');print(bundle.name,sha(bundle))
