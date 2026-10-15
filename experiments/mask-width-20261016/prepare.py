from pathlib import Path
root=Path(__file__).resolve().parent
source='''#include <immintrin.h>
#include <stdint.h>
#include <stddef.h>
typedef struct {uint32_t kind,a,b,aux;} MaskNode;
'''
for width,typ,load,store,zero,ones,xor,and_,or_ in [
 (1,'uint64_t','*(p)','*(p)=x','0','UINT64_MAX','(a^b)','(a&b)','(a|b)'),
 (2,'__m128i','_mm_loadu_si128((const __m128i*)p)','_mm_storeu_si128((__m128i*)p,x)','_mm_setzero_si128()','_mm_set1_epi64x(-1)','_mm_xor_si128(a,b)','_mm_and_si128(a,b)','_mm_or_si128(a,b)'),
 (4,'__m256i','_mm256_loadu_si256((const __m256i*)p)','_mm256_storeu_si256((__m256i*)p,x)','_mm256_setzero_si256()','_mm256_set1_epi64x(-1)','_mm256_xor_si256(a,b)','_mm256_and_si256(a,b)','_mm256_or_si256(a,b)'),
 (8,'__m512i','_mm512_loadu_si512(p)','_mm512_storeu_si512(p,x)','_mm512_setzero_si512()','_mm512_set1_epi64(-1)','_mm512_xor_si512(a,b)','_mm512_and_si512(a,b)','_mm512_or_si512(a,b)')]:
 source+=f'''static inline {typ} load{width}(const uint64_t*p){{return {load};}}
static inline void store{width}(uint64_t*p,{typ} x){{{store};}}
static int eval{width}(const MaskNode*nodes,size_t n,const uint64_t*ports,uint64_t*values,const uint32_t*roots,uint64_t*out){{
 for(size_t i=0;i<n;i++){{MaskNode o=nodes[i];if(o.aux)return 2;{typ} x;
 switch(o.kind){{case 0:x={zero};break;case 1:x={ones};break;
 case 2:if(o.a>=1024)return 3;x=load{width}(ports+o.a*8);break;
 case 3:case 4:case 5:{{if(o.a>=i||o.b>=i)return 4;{typ} a=load{width}(values+o.a*{width}),b=load{width}(values+o.b*{width});
 x=o.kind==3?{xor}:o.kind==4?{and_}:{or_};break;}}default:return 5;}}store{width}(values+i*{width},x);}}
 for(size_t i=0;i<512;i++){{if(roots[i]>=n)return 6;store{width}(out+i*8,load{width}(values+roots[i]*{width}));}}return 0;}}
'''
source+='''int mask8_eval_width(const MaskNode*nodes,size_t n,const uint64_t*ports,size_t np,uint64_t*values,size_t capacity,const uint32_t*roots,size_t nr,uint64_t*out,size_t words){
 if(capacity<n||np!=1024||nr!=512)return 1;
 switch(words){case 1:return eval1(nodes,n,ports,values,roots,out);case 2:return eval2(nodes,n,ports,values,roots,out);case 4:return eval4(nodes,n,ports,values,roots,out);case 8:return eval8(nodes,n,ports,values,roots,out);default:return 7;}}
'''
(root/'mask_width.c').write_text(source)
