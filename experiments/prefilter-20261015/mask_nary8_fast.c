#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
typedef struct{uint32_t kind,a,b,packed;} FusedOp;
_Static_assert(sizeof(FusedOp)==16,"fused ABI");
static int run1(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*1;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
uint64_t acc0=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if(bb!=65535)return 7;
acc0=(acc0^a[0]);
}
break;
}
d[0]=acc0;
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
uint64_t acc0=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*1;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*1;
acc0=(acc0^(a[0]&b[0]));
}
break;
}
d[0]=acc0;
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*1,1*8);memset(out+i*8+1,0,(8-1)*8);}return 0;}
static int run2(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*2;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m128i acc0=_mm_setzero_si128();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
}
break;
}
_mm_storeu_si128((__m128i*)(d+0),acc0);
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m128i acc0=_mm_setzero_si128();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*2;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*2;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
}
break;
}
_mm_storeu_si128((__m128i*)(d+0),acc0);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*2,2*8);memset(out+i*8+2,0,(8-2)*8);}return 0;}
static int run3(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*3;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m128i acc0=_mm_setzero_si128();
uint64_t acc2=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if(bb!=65535)return 7;
acc0=_mm_xor_si128(acc0,_mm_loadu_si128((const __m128i*)(a+0)));
acc2=(acc2^a[2]);
}
break;
}
_mm_storeu_si128((__m128i*)(d+0),acc0);
d[2]=acc2;
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m128i acc0=_mm_setzero_si128();
uint64_t acc2=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*3;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*3;
acc0=_mm_xor_si128(acc0,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+0)),_mm_loadu_si128((const __m128i*)(b+0))));
acc2=(acc2^(a[2]&b[2]));
}
break;
}
_mm_storeu_si128((__m128i*)(d+0),acc0);
d[2]=acc2;
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*3,3*8);memset(out+i*8+3,0,(8-3)*8);}return 0;}
static int run4(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*4;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*4;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*4;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*4,4*8);memset(out+i*8+4,0,(8-4)*8);}return 0;}
static int run5(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*5;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
uint64_t acc4=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=(acc4^a[4]);
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
d[4]=acc4;
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
uint64_t acc4=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*5;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*5;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=(acc4^(a[4]&b[4]));
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
d[4]=acc4;
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*5,5*8);memset(out+i*8+5,0,(8-5)*8);}return 0;}
static int run6(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*6;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
__m128i acc4=_mm_setzero_si128();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
_mm_storeu_si128((__m128i*)(d+4),acc4);
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
__m128i acc4=_mm_setzero_si128();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*6;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*6;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
_mm_storeu_si128((__m128i*)(d+4),acc4);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*6,6*8);memset(out+i*8+6,0,(8-6)*8);}return 0;}
static int run7(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*7;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
__m128i acc4=_mm_setzero_si128();
uint64_t acc6=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if(bb!=65535)return 7;
acc0=_mm256_xor_si256(acc0,_mm256_loadu_si256((const __m256i*)(a+0)));
acc4=_mm_xor_si128(acc4,_mm_loadu_si128((const __m128i*)(a+4)));
acc6=(acc6^a[6]);
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
_mm_storeu_si128((__m128i*)(d+4),acc4);
d[6]=acc6;
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m256i acc0=_mm256_setzero_si256();
__m128i acc4=_mm_setzero_si128();
uint64_t acc6=0;
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*7;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*7;
acc0=_mm256_xor_si256(acc0,_mm256_and_si256(_mm256_loadu_si256((const __m256i*)(a+0)),_mm256_loadu_si256((const __m256i*)(b+0))));
acc4=_mm_xor_si128(acc4,_mm_and_si128(_mm_loadu_si128((const __m128i*)(a+4)),_mm_loadu_si128((const __m128i*)(b+4))));
acc6=(acc6^(a[6]&b[6]));
}
break;
}
_mm256_storeu_si256((__m256i*)(d+0),acc0);
_mm_storeu_si128((__m128i*)(d+4),acc4);
d[6]=acc6;
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*7,7*8);memset(out+i*8+7,0,(8-7)*8);}return 0;}
static int run8(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,uint64_t*v,const uint32_t*roots,size_t nr,uint64_t*out,const uint32_t*pool,size_t npool){
for(size_t i=0;i<n;i++){FusedOp o=ops[i];uint32_t dest=o.kind>=6?(o.packed&65535):o.packed;if(dest>=ns||(!dest&&i))return 3;uint64_t*d=v+(size_t)dest*8;switch(o.kind){
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
case 15:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m512i acc0=_mm512_setzero_si512();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if(bb!=65535)return 7;
acc0=_mm512_xor_si512(acc0,_mm512_loadu_si512(a+0));
}
break;
}
_mm512_storeu_si512(d+0,acc0);
break;}
case 16:{if(o.a>npool||o.b>npool-o.a||o.b<2||o.b>8)return 6;
__m512i acc0=_mm512_setzero_si512();
switch(o.b){
case 8:
{uint32_t p=pool[(size_t)o.a+7],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
case 7:
{uint32_t p=pool[(size_t)o.a+6],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
case 6:
{uint32_t p=pool[(size_t)o.a+5],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
case 5:
{uint32_t p=pool[(size_t)o.a+4],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
case 4:
{uint32_t p=pool[(size_t)o.a+3],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
case 3:
{uint32_t p=pool[(size_t)o.a+2],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
case 2:
{uint32_t p=pool[(size_t)o.a+1],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
{uint32_t p=pool[(size_t)o.a+0],aa=p&65535,bb=p>>16;if(aa>=ns)return 3;const uint64_t*a=v+(size_t)aa*8;
if((bb>=ns)&(bb!=65535))return 3;bb&=0u-(uint32_t)(bb!=65535);const uint64_t*b=v+(size_t)bb*8;
acc0=_mm512_ternarylogic_epi64(_mm512_loadu_si512(a+0),_mm512_loadu_si512(b+0),acc0,106);
}
break;
}
_mm512_storeu_si512(d+0,acc0);
break;}
default:return 2;}}
for(size_t i=0;i<nr;i++){if(roots[i]>=ns)return 3;memcpy(out+i*8,v+(size_t)roots[i]*8,8*8);memset(out+i*8+8,0,(8-8)*8);}return 0;}
int mask_nary8_fast_eval(const FusedOp*ops,size_t n,size_t ns,const uint64_t*ports,size_t np,uint64_t*v,size_t capacity_words,const uint32_t*roots,size_t nr,unsigned words,uint64_t*out,const uint32_t*pool,size_t npool){
if(!ops||!ports||!v||!roots||!out||!pool||!npool||!n||!ns||ns>=65536||np!=1024||nr!=512||words<1||words>8)return 1;
if(ops[0].kind!=1||ops[0].packed!=0)return 8;
if(ns>SIZE_MAX/words||capacity_words<ns*words)return 5;switch(words){
case 1:return run1(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 2:return run2(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 3:return run3(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 4:return run4(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 5:return run5(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 6:return run6(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 7:return run7(ops,n,ns,ports,v,roots,nr,out,pool,npool);
case 8:return run8(ops,n,ns,ports,v,roots,nr,out,pool,npool);
}return 1;}
