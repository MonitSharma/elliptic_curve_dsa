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
 static void *jump[46]={&&OP0,&&BAD,&&BAD,&&OP3,&&OP4,&&OP5,&&OP6,&&OP7,&&OP8,&&OP9,&&OP10,&&OP11,&&OP12,&&OP13,&&OP14,&&OP15,&&OP16,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&BAD,&&OP35,&&OP36,&&OP37,&&OP38,&&BAD,&&OP40,&&BAD,&&OP42,&&OP43,&&OP44,&&OP45};
 size_t i=0;CompactOp o;V x,y,d;
 NEXT:if(i>=n)return depth?5:0;o=ops[i++];if(o.k>45)return 4;goto *jump[o.k];

   OP35:st(bits,o.bt,X(ld(bits,o.bt),_mm512_set1_epi64(-1)));goto NEXT;
   OP36:st(bits,o.bt,_mm512_setzero_si512());goto NEXT;
   OP37:st(bits,o.bt,_mm512_set1_epi64(-1));goto NEXT;
   OP38:st(q,o.t,X(ld(q,o.t),_mm512_set1_epi64(-1)));goto NEXT;
   OP40:st(q,o.t,X(ld(q,o.t),ld(q,o.a)));goto NEXT;
   OP42:x=ld(q,o.t);y=ld(q,o.a);st(q,o.t,y);st(q,o.a,x);goto NEXT;
   OP43:st(q,o.t,_mm512_setzero_si512());goto NEXT;
   OP44:st(q,o.t,_mm512_setzero_si512());st(bits,o.bt,_mm512_setzero_si512());goto NEXT;
   OP45:st(q,o.t,X(ld(q,o.t),A(ld(q,o.a),ld(q,o.b))));goto NEXT;

   OP0:OP7:OP9:OP14:goto NEXT;
   OP3:st(bits,o.bt,X(ld(bits,o.bt),C()));goto NEXT;
   OP4:st(bits,o.bt,N(C(),ld(bits,o.bt)));goto NEXT;
   OP5:st(bits,o.bt,O(ld(bits,o.bt),C()));goto NEXT;
   OP6:st(q,o.t,X(ld(q,o.t),C()));goto NEXT;
   OP8:st(q,o.t,X(ld(q,o.t),A(C(),ld(q,o.a))));goto NEXT;
   OP10:x=ld(q,o.t);y=ld(q,o.a);d=A(C(),X(x,y));st(q,o.t,X(x,d));st(q,o.a,X(y,d));goto NEXT;
   OP11:OP12:st(q,o.t,N(C(),ld(q,o.t)));if(o.k==12)st(bits,o.bt,N(C(),ld(bits,o.bt)));goto NEXT;
   OP13:st(q,o.t,X(ld(q,o.t),A(C(),A(ld(q,o.a),ld(q,o.b)))));goto NEXT;
   OP15:if(depth>=cap)return 2;st(stack,depth++,base);base=A(base,ld(bits,o.c));goto NEXT;
   OP16:if(!depth)return 3;base=ld(stack,--depth);goto NEXT;
   BAD:return 4;

}
