from pathlib import Path
import ast,shutil
a=Path(__file__).parent;ex=a.parent;old=ex/'breakthrough-depth12-final-20261020';r=ex/'breakthrough-public-best-drop-final-20261020';r.mkdir(exist_ok=False)
for n in ['.gitattributes','.gitignore']:shutil.copyfile(old/n,r/n)
verify='''def verify_search(sr):
 expected=1;total=0;passes=[]
 for prefix in sr['prefixes']:
  path=Path(prefix['path']);assert prefix['first']==expected and sha(path)==prefix['sha256'];seen=bytearray(prefix['screens']);found=[]
  with path.open()as inp:
   for line in inp:
    row=json.loads(line);k=row['nonce'];i=k-expected;assert 0<=i<len(seen)and not seen[i];seen[i]=1;assert row['rejection_policy']=='exact_full_state_only'
    if row['pass']:found.append(k)
  assert all(seen)and sorted(found)==prefix['passes'];assert prefix['highest']==expected+len(seen)-1;expected=prefix['highest']+1;total+=len(seen);passes.extend(found)
 assert total==sr['production_screens']and expected-1==sr['highest_screened'];assert passes and min(passes)==sr['selected_nonce'];return sorted(passes)
'''
s=(old/'finalize.py').read_text().replace('breakthrough-depth12-nonce-20261020','breakthrough-public-best-drop-nonce-continuation-20261020').replace('breakthrough-depth12-finished-20261020','breakthrough-public-best-drop-finished-20261020').replace('breakthrough-depth12-final-gate-20261020','breakthrough-public-best-drop-final-gate-20261020').replace('breakthrough-depth12-final-20261020','breakthrough-public-best-drop-final-20261020').replace('depth12_context_cache.rs','public_best_drop_cache.rs').replace("env['PEBBLE_HARD_CAP']='1234'","env['PEBBLE_HARD_CAP']='1233'")
start=s.index(' rows=[json.loads(x)for x in(search/');end=s.index(' gate=ws/',start)
s=s[:start]+" passes=verify_search(sr)\n assert f'SELECTED_OFFICIAL_REPLAY nonce={k} ok=true shots=9024 classical=0 phase=0 ancilla=0' in(search/'selected-search.log').read_text()\n"+s[end:]
s=s.replace('try:\n while not(search/',verify+'\ntry:\n while not(search/').replace('Targets independent Toffoli objective, not global product.','Targets complete product objective versus exact current public parent. Lowest passing nonce is never selected by cost.')
ast.parse(s);(r/'finalize.py').write_text(s)
# Keep seal implementation separate and reviewable; no uploads before local verification.
(r/'verify_search.py').write_text('from pathlib import Path\nimport hashlib,json\ndef sha(p):\n with p.open("rb")as source:return hashlib.file_digest(source,"sha256").hexdigest()\n'+verify)
s=(old/'submit.py').read_text().replace("parent=min(eligible,key=lambda x:x['officialMetrics']['toffoli']);assert parent['id']=='71d9dc7e-550b-480d-8d9e-c2af1989c0d7'","parent=min(eligible,key=lambda x:x['officialScore']);assert parent['id']=='acd0d88e-7445-4430-ba59-3c24c9bf4e0f'").replace('Fresh Toffoli parent changed','Fresh product parent changed').replace("assert b['rounded_mean_executed_toffoli']<parent['officialMetrics']['toffoli']","assert b['product']<parent['officialScore']").replace('does not beat current public T','does not beat current public product').replace("'source_files':205","'source_files':177")
ast.parse(s);(r/'submit.py').write_text(s)
(r/'PLAN.md').write_text('''# Complete benchmark and final packaging after the lowest exact nonce PASS

Wait for aggregate strictlyascending qualified search. Verify every prefix hash,
contiguity and lowestPASS. Keep original frozen/gated source intact. Clone a
separate detached7499 worktree, copy all177point-add sources and change ONLY
public_best_drop_cache::IDENTITY_NONCE0 to selectednonce. All17protected files
must match the original. Run unchanged benchmark.sh/all9024shots, compare every
pre-tail byte and all96 identitytail ops, preserve logs/score, restore historical
results.tsv. Never try another passingnonce for a better cost. Product must
strictly improve933231010 and freshly checked currentpublicacd0 before upload.
Seal source/gate/native/proof/grid/failedlaunch/allprefix evidence; independently
verify every archived/source member locally, then authorized GPT-6sol/Codex
submission. No upload can occur before the required localverificationreceipt.
''')
print(r)
