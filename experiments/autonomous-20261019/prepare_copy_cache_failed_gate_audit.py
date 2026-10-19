"""Verify the final failure from its sealed rows; never rerun the census."""
from pathlib import Path
ws=Path(__file__).resolve().parent.parent;r=ws/'product-copy-cache-gate-audit-20261020';assert not r.exists();r.mkdir()
s=(ws/'product-classical-twelve-gate-audit-20261020/audit.py').read_text()
s=s.replace('product-classical-twelve-native-20261019','product-copy-cache-native-20261020').replace('pareto-parent4-classical12-gate-20261019-v1','pareto-parent4-copy-cache-gate-20261020-v1')
s=s.replace("assert (r/'gate.exit').read_text().strip()=='0'","assert (r/'gate.exit').read_text().strip()=='1'")
s=s.replace("assert verdict['status']=='FAILURE_GATE_PASS' and all(verdict['rules'].values())","assert verdict['status']=='FAILURE_GATE_FAIL' and not all(verdict['rules'].values())")
s=s.replace("assert rules==verdict['rules'] and all(rules.values())","assert rules==verdict['rules'] and rules=={'value_not_above_parent':True,'paired_mcnemar_p_at_least_005':False,'failed_batches_per_packet_at_most_18':True,'zero_dirty_shots':True}")
s=s.replace('SEALED_CLASSICAL12_VERDICT_AND_ALL_EXISTING_ROWS_VERIFIED','SEALED_COPY_CACHE_FINAL_FAILURE_AND_ALL_EXISTING_ROWS_VERIFIED')
s=s.replace("assert len(freeze['protected_files'])==17","assert len(freeze['protected_files'])==17 and len(freeze['source_files'])==182")
(r/'audit.py').write_text(s,newline='\n')
for name in ['run.sh','launch.py']:(r/name).write_text((ws/'product-classical-twelve-gate-audit-20261020'/name).read_text().replace('product-classical-twelve-gate-audit-20261020','product-copy-cache-gate-audit-20261020').replace('read-only-sealed-classical12-gate-audit','read-only-sealed-copy-cache-FAILED-gate-audit'),newline='\n')
(r/'STATUS.md').write_text('''# Read-only preservation of the final failed cache census

The sole262144x64 paired gate failed the exact one-sided McNemar criterion:
b2973,c2812,p0.017701059294805803. Value shots28835=28835,dirty0 and
candidate failed batches perpacket17.991291046142578 satisfy the other rules.
This verdict is FINAL. Never relabel, extend, rerun or screen this source's
nonces. Its disabled runtime watcher refused before any own-source nonce test.
Only verify existing rows, exact binomial recurrence, source/stream hashes,
unchanged verdict and full archive. No new shot, packet, nonce or rejudgment.
''')
print('Prepared read-only final-failure audit/archive; no statistical rerun')
