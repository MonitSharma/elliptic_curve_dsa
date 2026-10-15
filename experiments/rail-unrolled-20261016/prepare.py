from pathlib import Path
import hashlib,shutil,struct
root=Path(__file__).resolve().parent;old=root.parent/'simd-rails-20261015'
table=(old/'steps.bin').read_bytes();assert hashlib.sha256(table).hexdigest()=='b3979902aa1635c0915fc2572c1e7a039121889a57b89c62ab3a9851e5b34309'
steps=list(struct.iter_unpack('<6I',table));assert len(steps)==138
source=(old/'rail8.c').read_text();start=source.index('static void walk(');loop=source.index(' for(size_t tick=0;tick<n;tick++){',start);finish=source.index(' I one_i=',loop);end=source.index('\nint rail8_population',finish)
prefix=source[source.index('{\n I ps=',start)+1:loop]
body=source[loop+len(' for(size_t tick=0;tick<n;tick++){'):finish];assert body.rstrip().endswith('}');body=body.rstrip()[:-1]
suffix=source[finish:end];assert suffix.rstrip().endswith('}')
fixed='static const RailStep fixed_steps[138]={\n'+''.join('{'+','.join(map(str,row))+'},\n' for row in steps)+'};\n'
functions=[]
for divide in [0,1]:
 text=f'static void walk_{divide}(I d,M *nonunit,M *overflow){{\n const RailStep *s=fixed_steps; const size_t n=138; const int divide={divide};\n'+prefix
 for tick in range(138):text+='\n { const size_t tick='+str(tick)+';\n'+body+'\n }\n'
 functions.append(text+suffix)
new=source[:start]+fixed+'\n'.join(functions)+source[end:]
new=new.replace('if(!n)return 1;','if(n!=138)return 1;for(size_t i=0;i<n;i++)if(memcmp(&s[i],&fixed_steps[i],sizeof(RailStep)))return 3;')
new=new.replace('walk(s,n,d1,1,&a,&b);walk(s,n,d2,0,&c,&d);','walk_1(d1,&a,&b);walk_0(d2,&c,&d);')
new=new.replace('#include "rail8.h"','#include "rail8.h"\n#include <string.h>')
(root/'rail8_unrolled.c').write_text(new);shutil.copyfile(old/'rail8.h',root/'rail8.h')
print('Generated fixed-table advisory specialization',len(new),'bytes')
