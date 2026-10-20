from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'run.sh').read_bytes().replace(b'python3 prepare.py > prepare.log',b'python3 prepare-v2.py > prepare-v2.log').replace(b'tests.log',b'tests-v2.log').replace(b'build.out',b'build-v2.out').replace(b'build.log',b'build-v2.log').replace(b'> run.exit',b'> run-v2.exit')
(r/'run-v2.sh').write_bytes(s)
