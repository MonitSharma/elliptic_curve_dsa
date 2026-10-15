from pathlib import Path
import json,hashlib,shutil
r=Path('/home/hclau/ecdsa_research/value-carry-contracts-20261016');d=r/'tool/src/bin';source=r.parent/'prefilter-20261015/tool/src/width_interned_witness_cap512.rs'
original=source.read_bytes();(r/'support-original.rs').write_bytes(original)
(d/'support.rs').write_text(original.decode()+'\nimpl Support{pub(super)fn zero_ids(&self)->Vec<usize>{self.qubits.iter().enumerate().filter_map(|(q,v)|v.is_zero().then_some(q)).collect()}}\n')
shutil.copy2(r/'support_donors.rs',d/'support_donors.rs')
x=json.loads((r/'terminal-interfaces.json').read_text());queries=sorted({row['actual_ccx']for row in x['rows']if'actual_ccx'in row})
(r/'terminal-queries.txt').write_text(''.join(f'{q}\n'for q in queries))
(r/'support-source.json').write_text(json.dumps(dict(original_path=str(source),original_sha256=hashlib.sha256(original).hexdigest(),copied_sha256=hashlib.sha256((d/'support.rs').read_bytes()).hexdigest(),new_query_only=True,whole_original_stream=True,rewrites_ignored=True,queries=len(queries)),indent=2)+'\n')
