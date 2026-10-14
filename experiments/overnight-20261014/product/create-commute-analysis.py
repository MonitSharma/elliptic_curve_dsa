"""Reuse the external analysis runner for a conservative commutation pass."""
from pathlib import Path
import sys,runpy
runpy.run_path(str(Path(__file__).with_name('create-anf-analysis.py')),run_name='__main__')
dest=Path(sys.argv[3]);p=dest/'src/main.rs';t=p.read_text()
t=t.replace('bounded_anf.rs','commute_cancel.rs').replace('bounded_anf','commute_cancel')
t=t.replace('ANF_DIAGNOSTIC','COMMUTE_DIAGNOSTIC')
p.write_text(t,newline='\n')
