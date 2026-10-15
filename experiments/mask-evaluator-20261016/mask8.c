#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
typedef struct { uint32_t kind,a,b,aux; } MaskNode;
_Static_assert(sizeof(MaskNode)==16,"mask DAG ABI");
static inline __m512i load(const uint64_t*p,size_t i){return _mm512_loadu_si512(p+8*i);}
static inline void save(uint64_t*p,size_t i,__m512i x){_mm512_storeu_si512(p+8*i,x);}
/* Ports and node values use8u64 words per Boolean value:512 independent inputs.
 * Every child is checked before its load; no opaque/fresh-input kind exists.
 * Roots are dependency UPPER bounds. Only their zero bits authorize knownness. */
int mask8_eval(const MaskNode*nodes,size_t n,const uint64_t*ports,size_t np,
 uint64_t*values,size_t capacity,const uint32_t*roots,size_t nr,uint64_t*out){
 if(capacity<n||np!=1024||nr!=512)return 1;
 for(size_t i=0;i<n;i++){
  MaskNode o=nodes[i];if(o.aux)return 2;__m512i x;
  switch(o.kind){
   case 0:x=_mm512_setzero_si512();break;
   case 1:x=_mm512_set1_epi64(-1);break;
   case 2:if(o.a>=np)return 3;x=load(ports,o.a);break;
   case 3:case 4:case 5:
    if(o.a>=i||o.b>=i)return 4;
    if(o.kind==3)x=_mm512_xor_si512(load(values,o.a),load(values,o.b));
    else if(o.kind==4)x=_mm512_and_si512(load(values,o.a),load(values,o.b));
    else x=_mm512_or_si512(load(values,o.a),load(values,o.b));break;
   default:return 5;
  }save(values,i,x);
 }
 for(size_t i=0;i<nr;i++){if(roots[i]>=n)return 6;save(out,i,load(values,roots[i]));}
 return 0;
}
