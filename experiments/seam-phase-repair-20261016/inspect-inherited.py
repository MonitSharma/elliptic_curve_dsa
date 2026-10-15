from pathlib import Path
import json,difflib
r=Path('/home/hclau/ecdsa_research/seam-phase-repair-20261016');d=json.loads((r/'rejected-full-source-region.json').read_text());a=[tuple(x['row'])for x in d['old_middle']];b=[tuple(x['row'])for x in d['new_middle']];out=[]
for tag,a0,a1,b0,b1 in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes():
 if tag!='equal':out.append(dict(kind=tag,old=d['old_middle'][a0:a1],new=d['new_middle'][b0:b1]))
(r/'inherited-seam-differences.json').write_text(json.dumps(out,indent=2)+'\n');print('MIDDLE_LENGTHS',len(a),len(b));print(json.dumps(out,indent=2))
