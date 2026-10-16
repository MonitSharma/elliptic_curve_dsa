"""Replace an unlaunched analysis watcher, preserving its exact four-case plan."""
import json,os,signal
from pathlib import Path
r=Path(__file__).resolve().parent;d=r/'recursive-unfold-20261016';assert not list(d.glob('*.bin'))
assert 'test result: ok.' in (d/'support-native-tests.log').read_text() and 'test result: ok.' in (d/'cache-native-tests.log').read_text()
pid=int((d/'launcher.pid').read_text());p=Path('/proc')/str(pid)
assert p.exists() and (p/'cwd').resolve()==r and 'bash run-recursive-unfold.sh' in (p/'cmdline').read_bytes().replace(b'\0',b' ').decode() and os.getpgid(pid)==pid
members=[]
for path in Path('/proc').iterdir():
    if not path.name.isdigit():continue
    try:
        if os.getpgid(int(path.name))!=pid:continue
        cmd=(path/'cmdline').read_bytes().replace(b'\0',b' ').decode();assert 'bash run-recursive-unfold.sh' in cmd or cmd.startswith('sleep '),'Analysis already launched; do not retire'
        members.append({'pid':int(path.name),'command':cmd})
    except ProcessLookupError:pass
row={'pid':pid,'group':members,'analysis_rows_created':0,'reason':'Retire waiting launcher only; same fixed four-case plan will launch from v2 after universal certificate work, rather than waiting all factored cases. Native tests/old declaration/logs retained.'}
(d/'RETIRED_BEFORE_ANALYSIS.json').write_text(json.dumps(row,indent=2)+'\n');os.killpg(pid,signal.SIGTERM);print(json.dumps(row))
old=(r/'run-recursive-unfold.sh').read_text();start=old.index('for family in product53 wide43;do')
header='''#!/usr/bin/env bash
set -euo pipefail
root=/home/hclau/ecdsa_research/product-exact-20261015
cd "$root"
out=recursive-unfold-v2-20261016
mkdir -p "$out"
echo $$ > "$out/launcher.pid"
trap 'rc=$?; echo "$rc" > "$root/$out/launcher.exit"' EXIT
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 12582912
cp recursive-unfold-20261016/DECLARATION.txt "$out/DECLARATION.txt"
printf '%s\\n' 'Scheduling-only v2: unchanged fixed4 cases; native tests already passed, wait complete universal audit then start at12GiB virtual instead24. Preserve resource failures, no outcome-selected case/stage count.' > "$out/SCHEDULING.txt"
while [ ! -f cache-certificate-v2-20261016/launcher.exit ];do sleep 30;done
python3 /home/hclau/ecdsa_research/server-preflight.py > "$out/preflight.json"
'''
(r/'run-recursive-unfold-v2.sh').write_text(header+old[start:])
