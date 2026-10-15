#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <immintrin.h>
typedef struct { uint32_t kind,a,b,dest; } SlotOp;
_Static_assert(sizeof(SlotOp)==16,"slot instruction ABI");
#define MAKE_EVAL(W) \
static int run##W(const SlotOp*ops,size_t n,const uint64_t*ports,uint64_t*v,size_t ns,const uint32_t*roots,size_t nr,uint64_t*out){ \
 for(size_t i=0;i<n;i++){SlotOp o=ops[i];if(o.dest>=ns)return 3;uint64_t*d=v+(size_t)o.dest*W; \
 switch(o.kind){ \
 case 0:for(size_t j=0;j<W;j++)d[j]=0;break; \
 case 1:for(size_t j=0;j<W;j++)d[j]=UINT64_MAX;break; \
 case 2:if(o.a>=1024)return 4;for(size_t j=0;j<W;j++)d[j]=ports[(size_t)o.a*8+j];break; \
 case 3:case 4:case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*W,*b=v+(size_t)o.b*W; \
 if(o.kind==3){for(size_t j=0;j<W;j++)d[j]=a[j]^b[j];} \
 else if(o.kind==4){for(size_t j=0;j<W;j++)d[j]=a[j]&b[j];} \
 else{for(size_t j=0;j<W;j++)d[j]=a[j]|b[j];}break;} \
 default:return 2;} } \
 for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;for(size_t j=0;j<W;j++)out[i*8+j]=v[(size_t)roots[i]*W+j];for(size_t j=W;j<8;j++)out[i*8+j]=0;}return 0;}
MAKE_EVAL(1) MAKE_EVAL(2) MAKE_EVAL(3) MAKE_EVAL(4) MAKE_EVAL(5) MAKE_EVAL(6) MAKE_EVAL(7) MAKE_EVAL(8)
int mask_slot_eval(const SlotOp*ops,size_t n,size_t ns,const uint64_t*ports,size_t np,uint64_t*v,size_t capacity_words,const uint32_t*roots,size_t nr,unsigned words,uint64_t*out){
 if(!ops||!ports||!v||!roots||!out||!n||!ns||np!=1024||nr!=512||words<1||words>8)return 1;
 if(ns>SIZE_MAX/words||capacity_words<ns*words)return 5;
 switch(words){
 #define CASE(W) case W:return run##W(ops,n,ports,v,ns,roots,nr,out);
 CASE(1) CASE(2) CASE(3) CASE(4) CASE(5) CASE(6) CASE(7) CASE(8)
 #undef CASE
 }return 1;
}
