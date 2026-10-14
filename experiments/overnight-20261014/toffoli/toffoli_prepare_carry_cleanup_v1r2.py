"""Repair fixture assumptions; preserve failed native v1r1 source and evidence."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
old=root/'research-output/overnight-20261014/toffoli/carry-cleanup-v1r1-source'
out=root/'research-output/overnight-20261014/toffoli/carry-cleanup-v1r2-source';out.mkdir(parents=True,exist_ok=True)
for file in old.iterdir():
    value=file.read_bytes();text=value.decode()
    if file.name=='y15_onefold.rs':
        assert hashlib.sha256(value).hexdigest()=='7aa6232013c934c3e77cc83369c12519fdf9d8f35502e988e2e83d51f7e8f385'
        text+='\n#[cfg(test)]\n#[path="toffoli_phase_linear_blocks_v1.rs"]\nmod toffoli_phase_linear_blocks_v1;\n'
    if file.name=='toffoli_native_fold.rs':
        begin=text.index('    let mut depth = 0usize;');end=text.index('    if inject_fault {',begin)
        text=text[:begin]+'''    let (blocks,linear_ops)=super::toffoli_phase_linear_blocks_v1::check(&ops);
    eprintln!("TOFFOLI_NATIVE_PHASE_STRUCTURE blocks={blocks} linear_conjugation_ops={linear_ops} conditioned_block_values_identity=true");
'''+text[end:]
    if file.name=='toffoli_carry_cleanup_tests_v1.rs':
        text=text.replace('            sim.clear_for_shot();','            sim.clear_for_shot();sim.xof.0=0x93AB_CDEF_6789_4521^(base as u64)^high.rotate_left(17);')
        # Preserve values on each case and compare identical pre-cleanup MR draws.
    (out/file.name).write_bytes(text.encode())
(out/'toffoli_phase_linear_blocks_v1.rs').write_bytes((here/'toffoli_phase_linear_blocks_v1.rs').read_bytes().replace(b'\r\n',b'\n'))
receipt={'status':'native_fixture_prepared_after_phase_structure_and_rng_pairing_assertion_failures',
         'failed_v1r1_source_sha256':'7aa6232013c934c3e77cc83369c12519fdf9d8f35502e988e2e83d51f7e8f385',
         'source_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
         'scope':'Candidate physical cleanup gates unchanged. Phase validator independently proves every conditioned linear block valueidentity. Each64-shot batch uses identical old/new initial RNG seed, keeping all pre-cleanup MR draws matched. Native pending, no fullrecord.'}
(here/'carry-cleanup-v1r2-preparation.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
