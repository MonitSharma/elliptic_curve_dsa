from pathlib import Path
import hashlib, json, re, shutil
root=Path(__file__).resolve().parent
old=root.parent/'zero-mr-slice-20261016'
for name in ['zero8.c','simd8wide.h']:
    shutil.copyfile(old/'tool'/name, root/('original.c' if name=='zero8.c' else name))
s=(root/'original.c').read_text()
needle='V c=base;if(o.c!=UINT32_MAX)c=A(c,ld(bits,o.c));V x,y,d;'
assert s.count(needle)==1
s=s.replace(needle,'V x,y,d;')
s=re.sub(r'(?<![.\w])c(?!\w)', 'C()', s)
s=s.replace('int zero8_run(', '#define C() (o.c==UINT32_MAX?base:A(base,ld(bits,o.c)))\nint zero8_run(')
(root/'lazy.c').write_text(s)
# Preserve each original opcode body, including scope validation and conditional
# stores. Only interpreter dispatch changes; unknown opcodes return the same4.
start=' for(size_t i=0;i<n;i++){CompactOp o=ops[i];V x,y,d;\n  switch(o.k){'
assert s.count(start)==1
cases=set(map(int,re.findall(r'case (\d+):',s)))
table=','.join('&&OP'+str(k) if k in cases else '&&BAD' for k in range(46))
replacement=' static void *jump[46]={'+table+'};\n size_t i=0;CompactOp o;V x,y,d;\n NEXT:if(i>=n)return depth?5:0;o=ops[i++];if(o.k>45)return 4;goto *jump[o.k];\n'
t=s.replace(start,replacement)
t=re.sub(r'case (\d+):',lambda m:'OP'+m[1]+':',t)
t=t.replace('break;','goto NEXT;').replace('default:return 4;','BAD:return 4;')
assert t.count('  }\n }return depth?5:0;')==1
t=t.replace('  }\n }return depth?5:0;','')
(root/'threaded.c').write_text(t)
(root/'source-hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.c')},indent=2)+'\n')
