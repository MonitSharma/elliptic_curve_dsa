import json,hashlib,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;f=r.parent/'product-classical-factors-refresh-20261019'
assert (f/'control.exit').read_text().strip()=='0'
assert json.loads((f/'CONTROL-parent4.json').read_text())['status']=='PROTECTED_SIMULATOR_CLASSICAL_FACTOR_FULL_TRANSCRIPT_CONTROL_PASS'
binary=Path('/home/hclau/ecdsa_research/product-order-20261019/target/release/refresh_classical_factors')
expected=next(x.split()[0] for x in (f/'BINARY.sha256').read_text().splitlines() if x.split()[-1]==str(binary))
assert hashlib.file_digest(binary.open('rb'),'sha256').hexdigest()==expected
capture=json.loads((r/'captured.json').read_text());assert capture['input_full_sha3_256']=='97c40ed1dd3f5123c9554ebf29c54c433960804c0effce63dc7bba52844ae9ae'
subprocess.run([str(binary),str(r/'captured.ops.bin'),str(r/'factored'),capture['output_full_sha3_256']],check=True)
(r/'FACTOR-BINARY-BINDING.json').write_text(json.dumps({'binary':str(binary),'sha256':expected,'captured_input_sha3_256':capture['output_full_sha3_256']},indent=2)+'\n')
