/* Exact value-only evaluation at the deliberately fixed all-zero MR stream.
 * Failure rejection needs an independent RNG-independence certificate. */
#include <immintrin.h>
#include "simd8wide.h"
typedef __m512i V;
static inline V ld(const uint64_t*p,size_t i){return _mm512_loadu_si512(p+8*i);}
static inline void st(uint64_t*p,size_t i,V x){_mm512_storeu_si512(p+8*i,x);}
#define A(a,b) _mm512_and_si512(a,b)
#define X(a,b) _mm512_xor_si512(a,b)
#define O(a,b) _mm512_or_si512(a,b)
#define N(a,b) _mm512_andnot_si512(a,b)
#define C() (o.c==UINT32_MAX?base:A(base,ld(bits,o.c)))
int zero8_run(const CompactOp*ops,size_t n,uint64_t*q,uint64_t*bits,uint64_t*stack,size_t cap){
 V base=_mm512_set1_epi64(-1);size_t depth=0;
 for(size_t i=0;i<n;i++){CompactOp o=ops[i];V x,y,d;
  switch(o.k){
   case 35:st(bits,o.bt,X(ld(bits,o.bt),_mm512_set1_epi64(-1)));break;
   case 36:st(bits,o.bt,_mm512_setzero_si512());break;
   case 37:st(bits,o.bt,_mm512_set1_epi64(-1));break;
   case 38:st(q,o.t,X(ld(q,o.t),_mm512_set1_epi64(-1)));break;
   case 40:st(q,o.t,X(ld(q,o.t),ld(q,o.a)));break;
   case 42:x=ld(q,o.t);y=ld(q,o.a);st(q,o.t,y);st(q,o.a,x);break;
   case 43:st(q,o.t,_mm512_setzero_si512());break;
   case 44:st(q,o.t,_mm512_setzero_si512());st(bits,o.bt,_mm512_setzero_si512());break;
   case 45:st(q,o.t,X(ld(q,o.t),A(ld(q,o.a),ld(q,o.b))));break;

   case 0:case 7:case 9:case 14:break;
   case 3:st(bits,o.bt,X(ld(bits,o.bt),C()));break;
   case 4:st(bits,o.bt,N(C(),ld(bits,o.bt)));break;
   case 5:st(bits,o.bt,O(ld(bits,o.bt),C()));break;
   case 6:st(q,o.t,X(ld(q,o.t),C()));break;
   case 8:st(q,o.t,X(ld(q,o.t),A(C(),ld(q,o.a))));break;
   case 10:x=ld(q,o.t);y=ld(q,o.a);d=A(C(),X(x,y));st(q,o.t,X(x,d));st(q,o.a,X(y,d));break;
   case 11:case 12:st(q,o.t,N(C(),ld(q,o.t)));if(o.k==12)st(bits,o.bt,N(C(),ld(bits,o.bt)));break;
   case 13:st(q,o.t,X(ld(q,o.t),A(C(),A(ld(q,o.a),ld(q,o.b)))));break;
   case 15:if(depth>=cap)return 2;st(stack,depth++,base);base=A(base,ld(bits,o.c));break;
   case 16:if(!depth)return 3;base=ld(stack,--depth);break;
   default:return 4;
  }
 }return depth?5:0;
}
