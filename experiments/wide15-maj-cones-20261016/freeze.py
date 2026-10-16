from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
code=int((R/'run.exit').read_text());assert code==0
d=json.loads((R/'DECLARATION.json').read_text());assert sha(Path(d['source']))==d['source_sha256']
assert json.loads((R/'SOURCE-PINS-BEFORE.json').read_text())==json.loads((R/'SOURCE-PINS-AFTER.json').read_text())
r=json.loads((R/'INVENTORY.json').read_text())
summary={'status':'SOURCE_ONLY_EXACT_MAJ_INVENTORY_TERMINAL','source_sha256':d['source_sha256'],
 'declaration_sha256':sha(R/'DECLARATION.json'),'run_exit':code,'all_syntactic_matches':r['all_syntactic_matches'],
 'contiguous_matches':r['contiguous_matches'],'disjoint_intervening_block_matches':r['disjoint_intervening_block_matches'],
 'deterministic_nonoverlapping_selected':r['deterministic_nonoverlapping_selected'],
 'guaranteed_executed_saving_T_per_shot':r['guaranteed_executed_saving_T_per_shot'],
 'maximum_syntactic_selected_saving_T_per_shot':r['maximum_syntactic_selected_saving_T_per_shot'],
 'conditional_executed_mean':'UNKNOWN; no circuit generation, input sample or nonce search',
 'inventory_sha256':sha(R/'INVENTORY.json'),'native_candidate_created':False,'record_claim':False}
(R/'TERMINAL-RECEIPT.json').write_text(json.dumps(summary,indent=2)+'\n')
(R/'SERVER-HASHREFS.json').write_text(json.dumps({d['source']:d['source_sha256']},indent=2)+'\n')
files=[p for p in R.rglob('*')if p.is_file()and p.name not in('evidence.tar.gz','MANIFEST.json','ARCHIVE-RECEIPT.json')and'__pycache__'not in p.parts]
m={p.relative_to(R).as_posix():sha(p)for p in files};(R/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
with tarfile.open(R/'evidence.tar.gz','w:gz')as t:
 for p in sorted(files+[R/'MANIFEST.json']):t.add(p,arcname=p.relative_to(R).as_posix())
with tarfile.open(R/'evidence.tar.gz')as t:
 for name,h in m.items():assert hashlib.sha256(t.extractfile(name).read()).hexdigest()==h,name
receipt={'status':'VERIFIED','archive_sha256':sha(R/'evidence.tar.gz'),'verified_members':len(m),'terminal_receipt_sha256':sha(R/'TERMINAL-RECEIPT.json')}
(R/'ARCHIVE-RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
