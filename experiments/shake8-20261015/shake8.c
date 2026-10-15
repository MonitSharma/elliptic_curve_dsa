/* Research SHAKE256 x8 wrapper. XKCP dependency is CC0; see pinned provenance. */
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "KeccakP-1600-times8-AVX512.h"
typedef struct { KeccakP1600times8_SIMD512_states s; size_t pos; int finalized; } Shake8;
#define RATE 136
void *shake8_create(void) {
    Shake8 *p=aligned_alloc(64,(sizeof(Shake8)+63)&~(size_t)63);
    if(p){memset(p,0,sizeof(*p));KeccakP1600times8_AVX512_InitializeAll(&p->s);}return p;
}
void shake8_free(void *p){free(p);}
void *shake8_clone(const void *v){Shake8 *p=shake8_create();if(p)memcpy(p,v,sizeof(*p));return p;}
int shake8_absorb8(void *v,const unsigned char *data,size_t n,size_t stride){
    Shake8 *p=v;if(p->finalized)return -1;
    size_t off=0;
    while(off<n){size_t take=RATE-p->pos;if(take>n-off)take=n-off;
        for(unsigned i=0;i<8;i++)KeccakP1600times8_AVX512_AddBytes(&p->s,i,data+i*stride+off,p->pos,take);
        p->pos+=take;off+=take;
        if(p->pos==RATE){KeccakP1600times8_AVX512_PermuteAll_24rounds(&p->s);p->pos=0;}
    }return 0;
}
int shake8_absorb_same(void *v,const unsigned char *data,size_t n){
    Shake8 *p=v;if(p->finalized)return -1;size_t off=0;
    if(p->pos==0&&n>=RATE){
        /* Parallel instance offset zero broadcasts each input block. */
        size_t done=KeccakF1600times8_AVX512_FastLoop_Absorb(&p->s,17,0,17,data,n);
        off=done;
    }
    return shake8_absorb8(p,data+off,n-off,0);
}
int shake8_finalize(void *v){
    Shake8 *p=v;if(p->finalized)return -1;
    for(unsigned i=0;i<8;i++){
        KeccakP1600times8_AVX512_AddByte(&p->s,i,0x1f,p->pos);
        KeccakP1600times8_AVX512_AddByte(&p->s,i,0x80,RATE-1);
    }
    KeccakP1600times8_AVX512_PermuteAll_24rounds(&p->s);p->pos=0;p->finalized=1;return 0;
}
int shake8_squeeze8(void *v,unsigned char *out,size_t n,size_t stride){
    Shake8 *p=v;if(!p->finalized)return -1;size_t off=0;
    while(off<n){if(p->pos==RATE){KeccakP1600times8_AVX512_PermuteAll_24rounds(&p->s);p->pos=0;}
        size_t take=RATE-p->pos;if(take>n-off)take=n-off;
        for(unsigned i=0;i<8;i++)KeccakP1600times8_AVX512_ExtractBytes(&p->s,i,out+i*stride+off,p->pos,take);
        p->pos+=take;off+=take;
    }return 0;
}
/* Output is word-major: out[word*8+instance], for eight SIMD simulation lanes. */
int shake8_words8(void *v,uint64_t *out,size_t n){
    Shake8 *p=v;if(!p->finalized||p->pos%8)return -1;
    while(n){if(p->pos==RATE){KeccakP1600times8_AVX512_PermuteAll_24rounds(&p->s);p->pos=0;}
        size_t take=(RATE-p->pos)/8;if(take>n)take=n;
        memcpy(out,((unsigned char*)&p->s)+(p->pos/8)*64,take*64);
        out+=take*8;p->pos+=take*8;n-=take;
    }return 0;
}
/* One-shot selection from eight different word offsets. Clone before use if
   the caller needs to resume the unselected streams afterward. */
int shake8_select_words8(void *v,const size_t offsets[8],uint64_t *out,size_t n){
    Shake8 *p=v;if(!p->finalized||p->pos%8)return -1;
    size_t end=0,at=0;
    for(unsigned i=0;i<8;i++){if(offsets[i]>SIZE_MAX-n)return -1;if(offsets[i]+n>end)end=offsets[i]+n;}
    while(at<end){
        if(p->pos==RATE){KeccakP1600times8_AVX512_PermuteAll_24rounds(&p->s);p->pos=0;}
        size_t take=(RATE-p->pos)/8;if(take>end-at)take=end-at;
        const uint64_t *state=(const uint64_t*)&p->s;
        for(unsigned i=0;i<8;i++){
            size_t lo=at>offsets[i]?at:offsets[i],hi=at+take;
            if(hi>offsets[i]+n)hi=offsets[i]+n;
            for(size_t j=lo;j<hi;j++)out[(j-offsets[i])*8+i]=state[(p->pos/8+j-at)*8+i];
        }
        at+=take;p->pos+=take*8;
    }return 0;
}
