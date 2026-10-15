from pathlib import Path
import subprocess
import sys
base,dest,helper=map(Path,sys.argv[1:])
subprocess.run([sys.executable,str(Path(__file__).with_name('prepare-cache-audit.py')),str(base),str(dest),str(helper)],check=True)
(dest/'src/cache_audit.rs').write_bytes(Path(__file__).with_name('lazy_cache_audit.rs').read_bytes()+Path(__file__).with_name('lazy_cache_tests.rs').read_bytes())
