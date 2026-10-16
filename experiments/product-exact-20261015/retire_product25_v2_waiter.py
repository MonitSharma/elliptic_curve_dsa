import json,os,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'product25-frozen-census-v2-20261016'
assert not (r/'product25-native.exit').exists()
assert not list(out.glob('*census.jsonl'))
pid=int((out/'launcher.pid').read_text());cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode().strip()
assert cmd=='bash run-product25-census-v2.sh',cmd
os.kill(pid,signal.SIGTERM)
for _ in range(20):
    if (out/'launcher.exit').exists():break
    time.sleep(.25)
actual=int((out/'launcher.exit').read_text());assert actual in [0,143]
assert not list(out.glob('*census.jsonl'))
(r/'SIMD_WATCHER_SWITCH_V3.json').write_text(json.dumps({'retired_pid':pid,'retired_command':cmd,'signal_requested':'SIGTERM','old_shell_exit':actual,'rows_started':0,'reason':'Before any rows, switch to fully validated frozen SIMDv2 exactSHAKE8. Original label product25-frozen-20261016,32768 batches/source6workers/source and both sources unchanged. Previous waiting protocol, marker and failed local newline transport retained. Only v3 complete fixed-row counts qualify.','new_script':'run-product25-census-v3.sh','new_executable':'/home/hclau/ecdsa_research/simd-census-v2-20261016/bin/simd_census_v2','new_executable_sha256':'790e92266ea67ec54ef701b2deed76fe8d0b766b411ca9eab877f82ae2c11a66'},indent=2)+'\n')
