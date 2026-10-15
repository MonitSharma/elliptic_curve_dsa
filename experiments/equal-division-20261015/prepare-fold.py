"""Uniform forward fold headroom control; preserve the original observer."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'prepare.py').read_text().replace("dest=root/'observer-b3'","dest=root/'fold-b3'").replace("root/'observer.patch'","root/'fold.patch'")
needle="(root/'fold.patch').write_bytes"
extra="""p=base/'y15_onefold.rs';s=p.read_text();a='if !rev && ((PAYLOAD_FOLD_PREFIX && t <= 55) || t == 104) { 57 } else { Y15_WIN }';assert s.count(a)==1;p.write_text(s.replace(a,'if !rev { 57 } else { Y15_WIN }'))
"""
s=s.replace(needle,extra+needle)
exec(compile(s,str(root/'prepare-fold.py'),'exec'))
