"""Adapt only the replay wrapper's classical storage size to the actual stream."""
from pathlib import Path
import hashlib,json,subprocess,sys
library,dest=map(Path,sys.argv[1:3]);root=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(root/'prepare-fixed-input-replay.py'),str(library),str(dest)],check=True)
p=dest/'src/main.rs';s=p.read_text(encoding='utf8')
s=s.replace('QubitOrBit,NO_QUBIT','QubitOrBit,NO_QUBIT,NO_BIT')
needle='reader.read_exact(&mut raw).unwrap();let op=decode(&raw);';assert s.count(needle)==1
s=s.replace(needle,needle+'''
  for bit in [op.c_target,op.c_condition]{if bit!=NO_BIT{let need=bit.0 as usize+1;assert!(need<=16_777_216,"refuse excessive classical storage");if need>simulator.bits.len(){simulator.bits.resize(need,0);simulator.num_bits=need;}}}
''')
s=s.replace('"maximum_chunk_ops":max_chunk,','"maximum_chunk_ops":max_chunk,"classical_storage_bits":simulator.bits.len(),')
p.write_text(s,encoding='utf8')
binding=json.loads((dest/'source-binding.json').read_text(encoding='utf8'));binding['program_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();binding['wrapper_change']='Grow zero-initialized classical storage when the actual stream references another bit; protected simulator unchanged; at most 16M bits.'
(dest/'source-binding.json').write_text(json.dumps(binding,indent=2)+'\n',encoding='utf8')
