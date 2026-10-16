"""Retain all four predetermined recursive cases, never select by packet results."""
import hashlib,json,re
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'recursive-unfold-fast-20261016';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (d/'launcher.exit').read_text().strip()=='0' and (d/'analysis.exit').read_text().strip()=='0'
target=d/'RESULTS.json';assert not target.exists();rows=[]
for family in ['product53','wide43']:
 for cap in [128,512]:
  name=d/f'{family}-{cap}';packets={}
  for packet in ['independent','structured']:
   p=Path(str(name)+f'-{packet}.log');line=next(x for x in p.read_text().splitlines() if x.startswith('DIAGNOSTIC_ONLY '));row=dict(re.findall(r'(\w+)=([^ ]+)',line));assert row['unequal_batches']=='0';packets[packet]=row
  stream=Path(str(name)+'.bin');manifest=Path(str(name)+'.manifest');log=Path(str(name)+'-generate.log')
  lines=log.read_text();resource=json.loads(Path(str(name)+'-resources.jsonl').read_text())
  rows.append(dict(family=family,atom_cap=cap,pair_cap=64,product_cap=1000000,extra_qubits_offered=0 if family=='product53' else 16,stream=str(stream.relative_to(r)),stream_sha256=sha(stream),chain_manifest=str(manifest.relative_to(r)),chain_manifest_sha256=sha(manifest),generate_log_sha256=sha(log),resources=resource,packets=packets,wall_time=next(x.split(': ',1)[1] for x in lines.splitlines() if 'Elapsed (wall clock)' in x),peak_rss_kib=int(re.search(r'Maximum resident set size \(kbytes\): (\d+)',lines).group(1))))
result=dict(status='ALL_FOUR_PREDECLARED_CASES_COMPLETE_DIAGNOSTIC_ONLY',scope='Four independent fixed cases, all retained including slower/no-gain configurations. Every512 full quantum/classical/phase/scratch comparison passes. These fixed coupled packets are diagnostics, not universal numerical means, native candidates, fresh failure gates or scored records.',source_declaration_sha256=sha(d/'DECLARATION.txt'),cases=rows,score=None,nonce_search_performed=False)
target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
