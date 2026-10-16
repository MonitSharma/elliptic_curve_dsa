"""Retire only the owned slow implementation after the exact replacement tests pass."""
import json,os,signal
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'recursive-unfold-v2-20261016';fast=r/'recursive-unfold-fast-20261016'
for name in ['support-native-tests.log','cache-native-tests.log']:assert 'test result: ok.' in (fast/name).read_text()
assert 'sorted_vector_normalization_matches_ordered_set_oracle ... ok' in (fast/'support-native-tests.log').read_text()
assert not (d/'launcher.exit').exists(),'Old implementation already terminal; investigate rather than replace'
pid=int((d/'launcher.pid').read_text());p=Path('/proc')/str(pid)
assert p.exists() and (p/'cwd').resolve()==r and 'bash run-recursive-unfold-v2.sh' in (p/'cmdline').read_bytes().replace(b'\0',b' ').decode() and os.getpgid(pid)==pid
members=[]
for path in Path('/proc').iterdir():
    if not path.name.isdigit():continue
    try:
        if os.getpgid(int(path.name))==pid:
            cmd=(path/'cmdline').read_bytes().replace(b'\0',b' ').decode();assert '/target-recursive-unfold/' in cmd or 'bash run-recursive-unfold-v2.sh' in cmd or '/usr/bin/time' in cmd
            members.append({'pid':int(path.name),'command':cmd})
    except ProcessLookupError:pass
row={'retired_group':pid,'members':members,'reason':'CPU-expensive ordered-set normalization replaced by exact same descending/budgeted algorithm using sorted-vector symmetric difference, after5120 oracle cases plus prior native value/phase/cache tests pass. Same fixed4 inputs/configurations retained; no packet-driven change.','new_directory':fast.name,'old_generated_streams':[p.name for p in d.glob('*.bin')]}
(d/'RETIRED_FOR_EXACT_SPEEDUP.json').write_text(json.dumps(row,indent=2)+'\n');os.killpg(pid,signal.SIGTERM);print(json.dumps(row))
old=(r/'run-recursive-unfold-v2.sh').read_text();body=old[old.index('for family in product53 wide43;do'):].replace('target-recursive-unfold/','target-recursive-unfold-fast/')
(r/'run-recursive-unfold-fast-analysis.sh').write_text('''#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=recursive-unfold-fast-20261016
echo $$ > "$out/analysis.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/analysis.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 12582912
cp recursive-unfold-20261016/DECLARATION.txt "$out/DECLARATION.txt"
'''+body)
