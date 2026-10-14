"""Technical QubitId alias-assertion repair; preserve failed v1 source."""
import hashlib
import json
from pathlib import Path
root=Path(__file__).resolve().parents[3];here=Path(__file__).parent
old=root/'research-output/overnight-20261014/toffoli/carry-cleanup-v1-source'
out=root/'research-output/overnight-20261014/toffoli/carry-cleanup-v1r1-source';out.mkdir(parents=True,exist_ok=True)
for file in old.iterdir():
    value=file.read_bytes()
    if file.name=='y15_onefold.rs':
        assert hashlib.sha256(value).hexdigest()=='60850ae813ad9c20ee20ec2d39b1d6f95bbb91bcb40601b5f72f6bc01eb5fea5'
        text=value.decode().replace('HashSet<_>=bank.iter().copied().collect()','HashSet<u64>=bank.iter().map(|q|q.0).collect()')
        text=text.replace('unique.contains(&c3)','unique.contains(&c3.0)').replace('unique.contains(input)','unique.contains(&input.0)')
        assert text!=value.decode();value=text.encode()
    (out/file.name).write_bytes(value)
receipt={'status':'native_source_prepared_after_compile_only_alias_assertion_failure','failed_v1_source_sha256':'60850ae813ad9c20ee20ec2d39b1d6f95bbb91bcb40601b5f72f6bc01eb5fea5',
         'source_sha256':{file.name:hashlib.sha256(file.read_bytes()).hexdigest() for file in out.iterdir()},
         'proof_sha256':hashlib.sha256((here/'carry-cleanup-rebase-v1.json').read_bytes()).hexdigest(),
         'scope':'Same gates and physical mapping as v1; only alias assertion compares integer IDs. No protected edits, native pending.'}
(here/'carry-cleanup-v1r1-preparation.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode());print(json.dumps(receipt))
