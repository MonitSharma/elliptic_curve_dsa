from pathlib import Path
import hashlib,json
r=Path(__file__).resolve().parent;t=r/'templates';old=r.parent/'census-all74-fixed67-20261016';names=['run_all74_cache67.py','consolidate_all74_cache67.py','prepare_all74_native67.py','verify_all74_native67.py']
for name in names:
 data=(old/name).read_bytes();(t/name).write_bytes(data);s=data.decode().replace('all74','preseed10').replace('ALL74','PRESEED10');(r/name.replace('all74','preseed10')).write_text(s)
(r/'TEMPLATE-PINS.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in t.iterdir()if p.is_file()},indent=2)+'\n')
