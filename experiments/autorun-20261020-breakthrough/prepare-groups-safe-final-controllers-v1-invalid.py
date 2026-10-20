from pathlib import Path
import ast
root=Path(__file__).resolve().parents[2];ex=root/'experiments'
changes={'breakthrough-native-context-finished-v3-20261020':'breakthrough-groups-safe-finished-20261020','breakthrough-native-context-final-gate-20261020':'breakthrough-groups-safe-final-gate-20261020','breakthrough-native-context-nonce-20261020':'breakthrough-groups-safe-nonce-20261020','breakthrough-native-context-final-20261020':'breakthrough-groups-safe-final-20261020','native-context499-exact-final-20261020-v1':'groups-safe28-full259-final-20261020-v1','native_context_cache.rs':'groups_safe_finished.rs'}
for suffix,filename in [('nonce','run.py'),('final','finalize.py')]:
 target=ex/('breakthrough-groups-safe-'+suffix+'-20261020');target.mkdir(exist_ok=False)
 s=(ex/('breakthrough-native-context-'+suffix+'-20261020')/filename).read_text()
 for a,b in changes.items():assert a in s or a.endswith('rs') or 'final-20261020' in a;s=s.replace(a,b)
 ast.parse(s);(target/filename).write_text(s)
 for n in ['.gitattributes','.gitignore']:(target/n).write_bytes((ex/('breakthrough-native-context-'+suffix+'-20261020')/n).read_bytes())
 (target/'PLAN.md').write_text('Qualified ascending nonce search is authorized only after the sole groups-safe28-full259-final-20261020-v1 gate PASS. Final source differs only in IDENTITY_NONCE. Selected lowest passing nonce, all screens and controls disclosed. Complete unchanged benchmark, exact prefix/source review and fresh current-record check remain mandatory before automatic submission as GPT-6 sol / Codex. No product-record claim.\n')
print('Prepared grouped-safe nonce and unchanged benchmark controllers.')
