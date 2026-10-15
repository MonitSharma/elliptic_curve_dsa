"""Observe the remaining terminal-source Hmr without changing gates."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root.parent/'phase-origin-20261015/prepare.py').read_text()
changes={"root.parent/'rail-control-20261015/square-room-b3'":"root.parent/'phase-origin-20261015/terminal-b3'",'q.0==1191 && c.0==515':'q.0==562 && c.0==549','op.q_control1.0==1191 && op.q_target.0==207':'op.q_control1.0==510 && op.q_target.0==872','48e2f0d8ad9bdc492415ec2700fe5dda9edc0e6f1b3a21eb935ef61ecc3953a4':'7d4472c3bf0d5d4ee67e45e9d1f34c5e741014578a2bf17eeaa0cba06b4c83ee'}
for a,b in changes.items():assert s.count(a)==1,(a,s.count(a));s=s.replace(a,b)
exec(compile(s,str(root/'prepare-origin.py'),'exec'))
