"""Second isolated preparation; first attempt preserved after an overbroad match."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'prepare.py').read_text().replace("dest=root/'state-b3'","dest=root/'state2-b3'")
s=s.replace("p=base/'y15_onefold.rs';s=p.read_text()","p=base/'y15_onefold.rs';full=p.read_text();a=full.index('fn body(');z=full.index('fn body_capped(',a);s=full[a:z]")
s=s.replace("s=s[:start]+part+s[end:];p.write_text(s)","s=s[:start]+part+s[end:];p.write_text(full[:a]+s+full[z:])")
s=s.replace("root/'state.patch'","root/'state2.patch'").replace("root/'state-manifest.json'","root/'state2-manifest.json'")
exec(compile(s,str(root/'prepare-second.py'),'exec'))
