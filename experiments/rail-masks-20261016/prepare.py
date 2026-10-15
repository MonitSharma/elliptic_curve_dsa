from pathlib import Path
import shutil
root=Path(__file__).resolve().parent;old=root.parent/'simd-rails-20261015';source=(old/'rail8.c').read_text()
needle='static inline M bit(I a,unsigned n){return _mm512_test_epi64_mask(a.l[n/64],cn(UINT64_C(1)<<(n%64)));}'
replacement='''static inline V limb_at(I a,unsigned n){V out=zero();
 out=_mm512_mask_mov_epi64(out,n==0?255:0,a.l[0]);out=_mm512_mask_mov_epi64(out,n==1?255:0,a.l[1]);out=_mm512_mask_mov_epi64(out,n==2?255:0,a.l[2]);out=_mm512_mask_mov_epi64(out,n==3?255:0,a.l[3]);out=_mm512_mask_mov_epi64(out,n==4?255:0,a.l[4]);return out;}
static inline M bit(I a,unsigned n){return _mm512_test_epi64_mask(limb_at(a,n/64),cn(UINT64_C(1)<<(n%64)));}'''
assert needle in source;source=source.replace(needle,replacement)
start=source.index('static inline I sx(');end=source.index('\nstatic inline unsigned window_low',start)
mask_rows=[]
for w in range(320):
 values=[(1<<min(64,max(0,w-64*i)))-1 for i in range(5)]
 mask_rows.append('{'+','.join('UINT64_C('+str(value)+')' for value in values)+'},\n')
table='static const uint64_t width_masks[320][5]={\n'+''.join(mask_rows)+'};\n'
body='static inline I sx(I a,unsigned w){M sign=bit(a,w-1);V fill=_mm512_movm_epi64(sign);'
for i in range(5):body+=f'a.l[{i}]=_mm512_ternarylogic_epi64(a.l[{i}],fill,cn(width_masks[w][{i}]),0xe4);'
body+='return a;}'
source=source[:start]+table+body+source[end:]
source=source.replace('X(a.l[limb],flip)','X(limb_at(a,limb),flip)').replace('X(a.l[limb+1],flip)','X(limb_at(a,limb+1),flip)')
(root/'rail8_masks.c').write_text(source);shutil.copyfile(old/'rail8.h',root/'rail8.h')
verify=(root.parent/'rail-unrolled-20261016/verify.py').read_text().replace('librail8_unrolled.so','librail8_masks.so')
# This version is generic over all valid tables, as is the original kernel.
verify=verify.replace("bad=(Step*138).from_buffer_copy(sb);bad[0].anchor^=1;assert new(bad,138,data,1,out)==3;assert new(steps,137,data,1,out)==1", "bad=(Step*138).from_buffer_copy(sb);bad[0].anchor^=1;a=(c.c_uint8*1)();b=(c.c_uint8*1)();assert original(bad,138,data,1,a)==new(bad,138,data,1,b)==0;assert bytes(a)==bytes(b)")
(root/'verify.py').write_text(verify)
