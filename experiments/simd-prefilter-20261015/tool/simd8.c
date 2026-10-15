#include <immintrin.h>
#include "simd8.h"
_Static_assert(sizeof(CompactOp)==12,"CompactOp ABI");
typedef __m512i V;
static inline V ld(const uint64_t *p,size_t i){return _mm512_loadu_si512(p+8*i);}
static inline void st(uint64_t *p,size_t i,V x){_mm512_storeu_si512(p+8*i,x);}
#define AND(a,b) _mm512_and_si512(a,b)
#define XOR(a,b) _mm512_xor_si512(a,b)
#define OR(a,b) _mm512_or_si512(a,b)
#define ANDNOT(a,b) _mm512_andnot_si512(a,b)
/* q and bit rows are physical wire ID * 8 words; RNG rows are MR ordinal * 8.
 * Every R/HMR consumes one row, even under an all-zero classical condition.
 * Stack stores values, never references to mutable classical controls. */
int simd8_run(const CompactOp *ops,size_t n,uint64_t *q,uint64_t *bits,
 uint64_t *phase,const uint64_t *rng,size_t nr,uint64_t *stack,size_t cap,size_t *used){
 V ph=ld(phase,0),base=_mm512_set1_epi64(-1);size_t depth=0,ri=0;
 for(size_t i=0;i<n;i++){
  const CompactOp o=ops[i];V c=base;if(o.c!=UINT16_MAX)c=AND(c,ld(bits,o.c));
  V x,y,d,w;
  switch(o.k){
   case 0:ph=XOR(ph,c);break;
   case 3:st(bits,o.bt,XOR(ld(bits,o.bt),c));break;
   case 4:st(bits,o.bt,ANDNOT(c,ld(bits,o.bt)));break;
   case 5:st(bits,o.bt,OR(ld(bits,o.bt),c));break;
   case 6:st(q,o.t,XOR(ld(q,o.t),c));break;
   case 7:ph=XOR(ph,AND(c,ld(q,o.t)));break;
   case 8:st(q,o.t,XOR(ld(q,o.t),AND(c,ld(q,o.a))));break;
   case 9:ph=XOR(ph,AND(c,AND(ld(q,o.a),ld(q,o.t))));break;
   case 10:x=ld(q,o.t);y=ld(q,o.a);d=AND(c,XOR(x,y));st(q,o.t,XOR(x,d));st(q,o.a,XOR(y,d));break;
   case 11:case 12:
    if(ri>=nr){*used=ri;return 1;}w=ld(rng,ri++);x=ld(q,o.t);
    ph=XOR(ph,AND(c,AND(x,w)));st(q,o.t,ANDNOT(c,x));
    if(o.k==12)st(bits,o.bt,XOR(ANDNOT(c,ld(bits,o.bt)),AND(c,w)));break;
   case 13:st(q,o.t,XOR(ld(q,o.t),AND(c,AND(ld(q,o.a),ld(q,o.b)))));break;
   case 14:ph=XOR(ph,AND(c,AND(ld(q,o.t),AND(ld(q,o.a),ld(q,o.b)))));break;
   case 15:if(depth>=cap){*used=ri;return 2;}st(stack,depth++,base);base=AND(base,ld(bits,o.c));break;
   case 16:if(!depth){*used=ri;return 3;}base=ld(stack,--depth);break;
   default:*used=ri;return 4;
  }
 }
 st(phase,0,ph);*used=ri;if(depth)return 5;if(ri!=nr)return 6;return 0;
}
