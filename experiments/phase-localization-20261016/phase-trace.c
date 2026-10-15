#define _POSIX_C_SOURCE 200809L
#include "simd8.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>
static void *readall(const char *name,size_t *n){FILE*f=fopen(name,"rb");assert(f);fseek(f,0,SEEK_END);*n=ftell(f);rewind(f);void*p=malloc(*n);assert(fread(p,1,*n,f)==*n);fclose(f);return p;}
static unsigned differs(uint64_t x){return (x^(x>>1))&1;}
#define STORE(t,v) do{qd-=differs(q[t]);q[t]=(v);qd+=differs(q[t]);}while(0)
int main(int argc,char**argv){assert(argc==5);unsigned lane=atoi(argv[1]);size_t selected=strtoull(argv[2],0,10);unsigned background=atoi(argv[3]);size_t limit=strtoull(argv[4],0,10);size_t bytes;CompactOp*ops=readall("compact.bin",&bytes);size_t n=bytes/12;uint32_t*map=readall("mr-map.bin",&bytes);size_t nr=bytes/4;uint64_t*iq=readall("initial-q.bin",&bytes);size_t nq=bytes/8;uint64_t*ib=readall("initial-b.bin",&bytes);size_t nb=bytes/8;uint64_t*q=calloc(nq,8),*b=calloc(nb,8),*rng=calloc(nr,8),stack[128],base=UINT64_MAX,phase=0,state=0x73796d626f6c6963ULL;size_t depth=0,ri=0;unsigned qd=0;
 for(size_t i=0;i<nq;i++)q[i]=-((iq[i]>>lane)&1);
 for(size_t i=0;i<nb;i++)b[i]=-((ib[i]>>lane)&1);
 if(background)for(size_t i=0;i<nr;i++){state^=state<<13;state^=state>>7;state^=state<<17;rng[i]=-(state&1);}
 rng[selected]^=2;
 for(size_t i=0;i<n;i++){CompactOp o=ops[i];uint64_t c=base&(o.c==UINT16_MAX?UINT64_MAX:b[o.c]),oldphase=phase,x,y,d,w,qt=o.t==UINT16_MAX?0:q[o.t];unsigned oldqd=qd;switch(o.k){
 case 0:phase^=c;break;case 3:b[o.bt]^=c;break;case 4:b[o.bt]&=~c;break;case 5:b[o.bt]|=c;break;
 case 6:STORE(o.t,q[o.t]^c);break;case 7:phase^=c&q[o.t];break;
 case 8:STORE(o.t,q[o.t]^(c&q[o.a]));break;case 9:phase^=c&q[o.a]&q[o.t];break;
 case 10:x=q[o.t];y=q[o.a];d=c&(x^y);STORE(o.t,x^d);STORE(o.a,y^d);break;
 case 11:case 12:w=rng[ri++];phase^=c&q[o.t]&w;STORE(o.t,q[o.t]&~c);if(o.k==12)b[o.bt]=(b[o.bt]&~c)^(w&c);break;
 case 13:STORE(o.t,q[o.t]^(c&q[o.a]&q[o.b]));break;case 14:phase^=c&q[o.t]&q[o.a]&q[o.b];break;
 case 15:stack[depth++]=base;base&=b[o.c];break;case 16:base=stack[--depth];break;default:abort();}
 if((differs(oldphase)!=differs(phase))||((o.k==11||o.k==12)&&ri==selected+1)||(!qd&&oldqd&&differs(phase)))printf("{\"compact_op\":%zu,\"kind\":%u,\"target\":%u,\"control1\":%u,\"condition\":%u,\"depth\":%zu,\"mr_consumed\":%zu,\"phase_pair\":%u,\"phase_delta_pair\":%u,\"pre_target_pair\":%u,\"active_pair\":%u,\"different_quantum_wires\":%u}\n",i,o.k,o.t,o.a,o.c,depth,ri,(unsigned)(phase&3),(unsigned)((phase^oldphase)&3),(unsigned)(qt&3),(unsigned)(c&3),qd);
 if(i==limit){FILE*f=fopen("phase-trace-snapshot.bin","wb");fwrite(q,8,nq,f);fwrite(b,8,nb,f);fwrite(&phase,8,1,f);fclose(f);}
 }
 assert(ri==nr&&depth==0);printf("{\"type\":\"summary\",\"phase_pair\":%u,\"quantum_differences\":%u,\"selected_mr\":%zu,\"original_op\":%u}\n",(unsigned)(phase&3),qd,selected,map[selected]);return 0;}
