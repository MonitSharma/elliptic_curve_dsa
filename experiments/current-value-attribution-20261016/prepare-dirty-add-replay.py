from pathlib import Path
import json,hashlib
r=Path('/home/hclau/ecdsa_research/current-value-attribution-20261016')
assert (r/'add-replay.exit').read_text().strip()=='0'
s=(r/'tool/src/add_runtime.rs').read_text()
needle='if m.before{add_entries.insert';assert s.count(needle)==1
s=s.replace(needle,'if m.before{if m.id==780{for &lane in &tracked{let nonzero:Vec<_>=s.qubits.iter().enumerate().filter_map(|(q,v)|((v>>lane&1)!=0).then_some(q)).collect();eprintln!("ADD_ENTRY shot={} at={} nonzero={nonzero:?}",batch*64+lane,m.at);}}add_entries.insert')
(r/'tool/src/dirty_add_runtime.rs').write_text(s)
s=(r/'tool/src/bin/current_adds.rs').read_text().replace('../add_runtime.rs','../dirty_add_runtime.rs');(r/'tool/src/bin/current_dirty_add.rs').write_text(s)
(r/'dirty-add-source.json').write_text(json.dumps({str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [r/'tool/src/dirty_add_runtime.rs',r/'tool/src/bin/current_dirty_add.rs']},indent=2)+'\n')
