import json,os,signal,time
from pathlib import Path
r=Path(__file__).resolve().parent;out=r/'product25-frozen-census-20261016'
assert not (r/'product25-native.exit').exists(), 'Native finished; re-audit before stopping anything'
assert not list(out.glob('*census.jsonl')), 'A census has started; never interrupt or replace it'
pid=int((out/'launcher.pid').read_text())
command_path=Path(f'/proc/{pid}/cmdline')
command=command_path.read_bytes().replace(b'\0',b' ').decode().strip() if command_path.exists() else 'already retired after previous SIGTERM request'
assert command in ['bash run-product25-census.sh','already retired after previous SIGTERM request'],command
if command_path.exists():os.kill(pid,signal.SIGTERM)
for _ in range(20):
    if (out/'launcher.exit').exists():break
    time.sleep(.25)
actual_exit=int((out/'launcher.exit').read_text())
assert actual_exit in [0,143]
assert not list(out.glob('*census.jsonl'))
(r/'SIMD_WATCHER_SWITCH.json').write_text(json.dumps({'retired_pid':pid,'retired_command':command,'signal_requested':'SIGTERM','old_shell_exit':actual_exit,'exit_note':'The waiting shell EXIT trap preserved status0 after SIGTERM. It produced no census rows; this marker does not constitute sample completion.','rows_started':0,'reason':'Before any rows, replace only the waiting supervisor with validated frozen SIMD census v1. Preserve label, source,32768 batches0..32767 and6workers/source. Original watcher/declaration/exit retained.','new_script':'run-product25-census-v2.sh','new_executable':'/home/hclau/ecdsa_research/simd-census-20261016/bin/simd_census_v1','new_executable_sha256':'49d99d2bf380b628550c3ed979b5bf2adfc1a962fb6fd00a5df267cde853f554'},indent=2)+'\n')
