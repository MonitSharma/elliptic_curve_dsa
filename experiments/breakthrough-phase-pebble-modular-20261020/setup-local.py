from pathlib import Path
r=Path(__file__).resolve().parent;old=r.parent/'breakthrough-phase-pebble-integration-20261020'
for name in['launch.py','sweep.py']:(r/name).write_bytes((old/name).read_bytes())
s=(old/'run.sh').read_bytes().replace(b'breakthrough-phase-pebble-integration-20261020',b'breakthrough-phase-pebble-modular-20261020')
needle=b' if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 build --release --bin build_circuit';assert s.count(needle)==1
s=s.replace(needle,b' if [ "$rc" -eq 0 ]; then /home/hclau/.cargo/bin/cargo +1.93.0 test --release --bin build_circuit zero_carry -- --nocapture >> ../tests.log 2>&1; rc=$?; fi\n'+needle)
(r/'run.sh').write_bytes(s)
