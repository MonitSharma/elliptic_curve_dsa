#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
typedef struct{uint32_t kind,a,b,packed;} FusedOp;
_Static_assert(sizeof(FusedOp)==16,"fused ABI");
static int run1(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*1;switch(o.kind){
case 0:memset(d,0,1*8);break;
case 1:memset(d,255,1*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,1*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
d[0]=(a[0]^b[0]);
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
d[0]=(a[0]&b[0]);
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
d[0]=(a[0]|b[0]);
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]^b[0])^c[0]);
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]^b[0])&c[0]);
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]^b[0])|c[0]);
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]&b[0])^c[0]);
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]&b[0])&c[0]);
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]&b[0])|c[0]);
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]|b[0])^c[0]);
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]|b[0])&c[0]);
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*1,*b=v+(size_t)o.b*1;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*1;
d[0]=((a[0]|b[0])|c[0]);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*1,1*8);memset(out+i*8+1,0,(8-1)*8);}return 0;}
static int run2(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*2;switch(o.kind){
case 0:memset(d,0,2*8);break;
case 1:memset(d,255,2*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,2*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*2,*b=v+(size_t)o.b*2;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*2;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*2,2*8);memset(out+i*8+2,0,(8-2)*8);}return 0;}
static int run3(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*3;switch(o.kind){
case 0:memset(d,0,3*8);break;
case 1:memset(d,255,3*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,3*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
d[2]=(a[2]^b[2]);
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
d[2]=(a[2]&b[2]);
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
d[2]=(a[2]|b[2]);
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]^b[2])^c[2]);
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]^b[2])&c[2]);
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]^b[2])|c[2]);
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]&b[2])^c[2]);
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]&b[2])&c[2]);
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]&b[2])|c[2]);
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_xor_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]|b[2])^c[2]);
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_and_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]|b[2])&c[2]);
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*3,*b=v+(size_t)o.b*3;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*3;
_mm_storeu_si128((__m128i*)(d+0),_mm_or_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))),_mm_loadu_si128((const __m128i*)(c+0))));
d[2]=((a[2]|b[2])|c[2]);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*3,3*8);memset(out+i*8+3,0,(8-3)*8);}return 0;}
static int run4(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*4;switch(o.kind){
case 0:memset(d,0,4*8);break;
case 1:memset(d,255,4*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,4*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*4,*b=v+(size_t)o.b*4;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*4;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*4,4*8);memset(out+i*8+4,0,(8-4)*8);}return 0;}
static int run5(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*5;switch(o.kind){
case 0:memset(d,0,5*8);break;
case 1:memset(d,255,5*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,5*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
d[4]=(a[4]^b[4]);
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
d[4]=(a[4]&b[4]);
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
d[4]=(a[4]|b[4]);
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]^b[4])^c[4]);
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]^b[4])&c[4]);
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]^b[4])|c[4]);
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]&b[4])^c[4]);
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]&b[4])&c[4]);
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]&b[4])|c[4]);
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]|b[4])^c[4]);
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]|b[4])&c[4]);
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*5,*b=v+(size_t)o.b*5;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*5;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
d[4]=((a[4]|b[4])|c[4]);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*5,5*8);memset(out+i*8+5,0,(8-5)*8);}return 0;}
static int run6(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*6;switch(o.kind){
case 0:memset(d,0,6*8);break;
case 1:memset(d,255,6*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,6*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*6,*b=v+(size_t)o.b*6;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*6;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*6,6*8);memset(out+i*8+6,0,(8-6)*8);}return 0;}
static int run7(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*7;switch(o.kind){
case 0:memset(d,0,7*8);break;
case 1:memset(d,255,7*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,7*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
d[6]=(a[6]^b[6]);
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
d[6]=(a[6]&b[6]);
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
d[6]=(a[6]|b[6]);
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]^b[6])^c[6]);
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]^b[6])&c[6]);
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_xor_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_xor_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]^b[6])|c[6]);
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]&b[6])^c[6]);
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]&b[6])&c[6]);
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]&b[6])|c[6]);
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_xor_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_xor_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]|b[6])^c[6]);
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_and_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_and_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]|b[6])&c[6]);
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*7,*b=v+(size_t)o.b*7;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*7;
_mm256_storeu_si256((__m256i*)(d+0),_mm256_or_si256(_mm256_or_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))),_mm256_loadu_si256((const __m256i*)(c+0))));
_mm_storeu_si128((__m128i*)(d+4),_mm_or_si128(_mm_or_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))),_mm_loadu_si128((const __m128i*)(c+4))));
d[6]=((a[6]|b[6])|c[6]);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*7,7*8);memset(out+i*8+7,0,(8-7)*8);}return 0;}
static int run8(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns)return 3;uint64_t*d=v+(size_t)dest*8;switch(o.kind){
case 0:memset(d,0,8*8);break;
case 1:memset(d,255,8*8);break;
case 2:if(o.a>=1024)return 4;memcpy(d,ports+(size_t)o.a*8,8*8);break;
case 3:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
_mm512_storeu_si512(d+0,_mm512_xor_si512(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0)));
break;}
case 4:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
_mm512_storeu_si512(d+0,_mm512_and_si512(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0)));
break;}
case 5:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
_mm512_storeu_si512(d+0,_mm512_or_si512(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0)));
break;}
case 6:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),150));
break;}
case 7:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),40));
break;}
case 8:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),190));
break;}
case 9:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),106));
break;}
case 10:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),128));
break;}
case 11:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),234));
break;}
case 12:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),86));
break;}
case 13:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),168));
break;}
case 14:{if(o.a>=ns||o.b>=ns)return 3;const uint64_t*a=v+(size_t)o.a*8,*b=v+(size_t)o.b*8;
uint32_t ci=o.packed>>16;if(ci>=ns)return 3;const uint64_t*c=v+(size_t)ci*8;
_mm512_storeu_si512(d+0,_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),_mm512_loadu_si512(c+0),254));
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*8,8*8);memset(out+i*8+8,0,(8-8)*8);}return 0;}
int mask_fused_eval(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,size_t np,uint64_t*v,size_t capacity_words,const uint32_t*roots,size_t nr,unsigned words,uint64_t*out){
if(!ops||!ports||!v||!roots||!out||!n||!ns||ns>=65536||np!=1024||nr!=512||words<1||words>8)return 1;
if(ns>SIZE_MAX/words||capacity_words<ns*words)return 5;switch(words){
case 1:return run1(ops,n,ns,ports,v,roots,nr,out);
case 2:return run2(ops,n,ns,ports,v,roots,nr,out);
case 3:return run3(ops,n,ns,ports,v,roots,nr,out);
case 4:return run4(ops,n,ns,ports,v,roots,nr,out);
case 5:return run5(ops,n,ns,ports,v,roots,nr,out);
case 6:return run6(ops,n,ns,ports,v,roots,nr,out);
case 7:return run7(ops,n,ns,ports,v,roots,nr,out);
case 8:return run8(ops,n,ns,ports,v,roots,nr,out);
}return 1;}
