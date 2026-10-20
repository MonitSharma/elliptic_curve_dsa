from pathlib import Path
a=Path(__file__).parent
old=a.parent/'breakthrough-de8-generic-repeat-v2-20261020'
(old/'STATUS.md').write_text('# Setup stopped before tests or generation\n\nThe preserved point_add tree includes binary assets. UTF-8 alone cannot decode every source asset for a text patch. V3 compares original/current bytes first and only decodes changed Rust files; binary assets remain byte-identical. No input/gate/nonce work ran.\n',encoding='utf-8')
s=(a/'prepare-de8-generic-repeat.py').read_text(encoding='utf-8').replace('breakthrough-de8-generic-repeat-20261020','breakthrough-de8-generic-repeat-v3-20261020')
needle="before=(old/'candidate'/rel).read_text()if(old/'candidate'/rel).exists()else'';after=(t/rel).read_text()\n if before!=after:patch.extend(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))"
assert s.count(needle)==1
s=s.replace(needle,"before=(old/'candidate'/rel).read_bytes()if(old/'candidate'/rel).exists()else b'';after=(t/rel).read_bytes()\n if before!=after:patch.extend(difflib.unified_diff(before.decode('utf-8').splitlines(True),after.decode('utf-8').splitlines(True),fromfile='a/'+rel,tofile='b/'+rel))")
exec(compile(s,str(a/'prepare-de8-generic-repeat.py'),'exec'))
