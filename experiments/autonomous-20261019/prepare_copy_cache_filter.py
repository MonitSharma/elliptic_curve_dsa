"""Build a disabled exact-transfer port; no nonce evaluation before own gate."""
from pathlib import Path
import hashlib,json
ws=Path(__file__).resolve().parent.parent;old=ws/'product-classical-twelve-filter-20261019';r=ws/'product-copy-cache-filter-20261020'
assert not r.exists();r.mkdir()
s=(old/'prepare.py').read_text()
changes={"old=ws/'product-classical-nine-filter-20261019'":"old=ws/'product-classical-twelve-filter-20261019'", "n=ws/'product-classical-twelve-native-20261019'":"n=ws/'product-copy-cache-native-20261020'", "proof=ws/'product-classical-twelve-proof-20261019'":"proof=ws/'product-copy-cache-proof-20261020'", "h=='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'":"h=='26dc60ee329a6cf448143eebc9f1f218efd73ffeaaef92213a75e7d31f3e7cc1'", 'CLASSICAL_TWELVE_VALUE_PHASE_AND_RNG_TRANSFER_AUDIT_PASS':'COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS', "['status']=='DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS'":"['status']=='DISABLED_CLASSICAL_TWELVE_PIPELINE_QUALIFICATION_PASS'", "before='76271c7d66785b62ec4077ec241e80d3645841ba898cf8b633c377099da687c1'":"before='17c767f514ca98ad02d4da9e5b1dbedf67189e5c70b7b15916adc0f0c2f0a7f7'", "('assert_eq!(n,17_889_627)','assert_eq!(n,17_889_635)')":"('assert_eq!(n,17_889_635)','assert_eq!(n,17_889_637)')", "product-classical-nine-20261019/candidate/ops.bin":"product-classical-twelve-native-20261019/candidate/ops.bin", "product-classical-twelve-native-20261019/candidate/ops.bin')\").replace(before,h)":"product-copy-cache-native-20261020/candidate/ops.bin')\").replace(before,h)", ".replace('DISABLED_CLASSICAL_NINE_PIPELINE_QUALIFICATION_PASS','DISABLED_CLASSICAL_TWELVE_PIPELINE_QUALIFICATION_PASS')":".replace('DISABLED_CLASSICAL_TWELVE_PIPELINE_QUALIFICATION_PASS','DISABLED_COPY_CACHE_PIPELINE_QUALIFICATION_PASS')"}
for a,b in changes.items():assert a in s,a;s=s.replace(a,b)
(r/'prepare.py').write_text(s,newline='\n')
for name in ['validate_gate.py','after_gate.py','run-build.sh','run-qualify.sh','launch_waiter.py']:
 s=(old/name).read_text().replace('product-classical-twelve-native-20261019','product-copy-cache-native-20261020').replace('product-classical-twelve-filter-20261019','product-copy-cache-filter-20261020').replace('pareto-parent4-classical12-gate-20261019-v1','pareto-parent4-copy-cache-gate-20261020-v1').replace('preflight_v14.py','preflight_v15.py').replace('sole classical12 gate','sole copy-cache gate')
 if name=='run-build.sh':
  s=s.replace('cd "$r/tool"','(\ncd "$r/tool"')+'\n)\n'
 (r/name).write_text(s,newline='\n')
(r/'launch_build.py').write_text('''import json,subprocess
from pathlib import Path
r=Path(__file__).resolve().parent;assert not (r/'build.pid').exists()
assert json.loads((r.parent/'product-copy-cache-proof-20261020/TRANSFER.json').read_text())['status']=='COPY_CACHE_VALUE_PHASE_AND_PHYSICAL_RNG_TRANSFER_AUDIT_PASS'
with (r/'build-nohup.log').open('xb') as f:p=subprocess.Popen(['nohup','bash','run-build.sh'],cwd=r,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
(r/'build.pid').write_text(str(p.pid)+'\\n');print(json.dumps({'build_pid':p.pid,'new_source_nonce_tests_allowed':False}))
''',newline='\n')
(r/'STATUS.md').write_text('''# Disabled runtime port for the frozen copy-cache source

Only candidate stream hash/opcount and exact proof bindings change from the
qualified source12 runtime. Universal full final-q/c/phase/physical-RNG equality
composes with its old value-mask transfer, including arbitrary boundary values.
Temporary storage differences inside the held interval are permitted only
because the complete final-state proof closes every wire and RNG continuation.
Own-seed/full9024/zero-MR/partial/4096-prefix controls remain mandatory after
this source's sole final census PASS. Build is allowed first; nonce evaluation,
authoritative rejection and production are disabled. Never relabel a gate or
retry a statistical failure. The build leader stays root; compiler in subshell.
''')
print('Prepared disabled copy-cache runtime build and gate-blocked qualification')
