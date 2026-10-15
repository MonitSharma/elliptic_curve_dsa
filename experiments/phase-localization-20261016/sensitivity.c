#define _POSIX_C_SOURCE 200809L
#include "simd8.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <assert.h>
static void *readall(const char *name,size_t *n){FILE*f=fopen(name,"rb");assert(f);fseek(f,0,SEEK_END);*n=ftell(f);rewind(f);void*p=malloc(*n);assert(fread(p,1,*n,f)==*n);fclose(f);return p;}
static double seconds(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec*1e-9;}
int main(int argc,char**argv){assert(argc==3);assert(__builtin_cpu_supports("avx512f")&&__builtin_cpu_supports("avx512dq")&&__builtin_cpu_supports("avx512bw")&&__builtin_cpu_supports("avx512vl"));unsigned lane=atoi(argv[1]);unsigned base=atoi(argv[2]);assert(lane<64&&base<2);size_t bytes;CompactOp*ops=readall("compact.bin",&bytes);size_t n=bytes/12;uint32_t*map=readall("mr-map.bin",&bytes);size_t nr=bytes/4;uint64_t*inputq=readall("initial-q.bin",&bytes);size_t nq=bytes/8;uint64_t*inputb=readall("initial-b.bin",&bytes);size_t nb=bytes/8;uint64_t*iq=calloc(nq*8,8),*ib=calloc(nb*8,8),*q=calloc(nq*8,8),*b=calloc(nb*8,8),*rng=calloc(nr*8,8),*stack=calloc(128*8,8),*reference=calloc(nq*8,8);uint64_t phase[8];size_t used;
 for(size_t i=0;i<nq;i++)for(unsigned j=0;j<8;j++)iq[i*8+j]=-(uint64_t)((inputq[i]>>lane)&1);
 for(size_t i=0;i<nb;i++)for(unsigned j=0;j<8;j++)ib[i*8+j]=-(uint64_t)((inputb[i]>>lane)&1);
 /* Base1 uses a fixed deterministic measurement-bit sequence replicated across
  * all512 copies. It is a diagnostic assignment, never a packet or nonce. */
 if(base){uint64_t state=0x73796d626f6c6963ULL;for(size_t i=0;i<nr;i++){state^=state<<13;state^=state>>7;state^=state<<17;for(unsigned j=0;j<8;j++)rng[i*8+j]=-(state&1);}}
 memcpy(q,iq,nq*64);memcpy(b,ib,nb*64);memset(phase,0,sizeof phase);assert(!simd8_run(ops,n,q,b,phase,rng,nr,stack,128,&used));assert(used==nr);uint64_t baseline=phase[0];for(unsigned j=1;j<8;j++)assert(phase[j]==baseline);assert(baseline==0||baseline==UINT64_MAX);memcpy(reference,q,nq*64);double start=seconds();size_t count=0,phase_only=0;printf("{\"type\":\"start\",\"input_lane\":%u,\"base\":%u,\"baseline_phase\":%u,\"mr\":%zu}\n",lane,base,baseline!=0,nr);fflush(stdout);
 for(size_t first=0;first<nr;first+=512){size_t take=nr-first<512?nr-first:512;for(size_t j=0;j<take;j++)rng[(first+j)*8+j/64]^=1ULL<<(j%64);memcpy(q,iq,nq*64);memcpy(b,ib,nb*64);memset(phase,0,sizeof phase);assert(!simd8_run(ops,n,q,b,phase,rng,nr,stack,128,&used));assert(used==nr);uint64_t change[8]={0};for(size_t k=0;k<nq;k++)for(unsigned j=0;j<8;j++)change[j]|=q[k*8+j]^reference[k*8+j];for(size_t j=0;j<take;j++){unsigned p=((phase[j/64]^baseline)>>(j%64))&1;unsigned v=(change[j/64]>>(j%64))&1;if(p||v){count++;phase_only+=p&&!v;printf("{\"type\":\"sensitivity\",\"mr\":%zu,\"op\":%u,\"phase_change\":%u,\"quantum_change\":%u}\n",first+j,map[first+j],p,v);}}for(size_t j=0;j<take;j++)rng[(first+j)*8+j/64]^=1ULL<<(j%64);if(first%(512*128)==0){fprintf(stderr,"PROGRESS first=%zu seconds=%.3f\n",first,seconds()-start);fflush(stdout);}}
 printf("{\"type\":\"summary\",\"input_lane\":%u,\"base\":%u,\"sensitive\":%zu,\"phase_only\":%zu,\"seconds\":%.6f}\n",lane,base,count,phase_only,seconds()-start);return 0;}
