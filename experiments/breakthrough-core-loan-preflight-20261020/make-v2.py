from pathlib import Path
r=Path(__file__).resolve().parent
raw=(r/'run.sh').read_bytes()
for a,b in [(b'prepare.py',b'prepare-v2.py'),(b'sweep.py',b'sweep-v2.py'),(b'prepare.log',b'prepare-v2.log'),(b'tests.log',b'tests-v2.log'),(b'build.out',b'build-v2.out'),(b'build.log',b'build-v2.log'),(b'sweep.log',b'sweep-v2.log'),(b'run.exit',b'run-v2.exit')]:raw=raw.replace(a,b)
(r/'run-v2.sh').write_bytes(raw);(r/'sweep-v2.py').write_bytes((r/'sweep.py').read_bytes().replace(b'SOURCE_FREEZE.json',b'SOURCE_FREEZE-v2.json'));(r/'launch-v2.py').write_bytes((r/'launch.py').read_bytes().replace(b'run.pid',b'run-v2.pid').replace(b'nohup.log',b'nohup-v2.log').replace(b'run.sh',b'run-v2.sh'))
