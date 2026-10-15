#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
typedef struct{uint64_t h;size_t i;} Key;
static int cmp(const void*a,const void*b){uint64_t x=((const Key*)a)->h,y=((const Key*)b)->h;return(x>y)-(x<y);}
static uint64_t token(const uint8_t*p){uint64_t h=0x7265736561726368ull,x;for(int i=0;i<7;i++){memcpy(&x,p+8*i,8);h=(h^x)*0x9e3779b185ebca87ull;h^=h>>31;}return h;}
static int scan(const uint8_t*body,size_t n,const uint8_t*anchors,size_t count,size_t width,uint64_t*first,uint32_t*counts,uint64_t*hits,size_t cap){if(!width||width>64||n<width)return -1;Key*keys=malloc(count*sizeof(Key));if(!keys)return-2;const uint64_t P=0xd6e8feb86659fd93ull;uint64_t power=1;for(size_t j=1;j<width;j++)power*=P;for(size_t i=0;i<count;i++){uint64_t h=0;for(size_t j=0;j<width;j++)h=h*P+token(anchors+(i*width+j)*56);keys[i]=(Key){h,i};first[i]=UINT64_MAX;counts[i]=0;}qsort(keys,count,sizeof(Key),cmp);uint64_t ring[64],h=0;for(size_t i=0;i<n;i++){uint64_t x=token(body+i*56);if(i>=width)h-=ring[i%width]*power;ring[i%width]=x;h=h*P+x;if(i+1<width)continue;size_t lo=0,hi=count;while(lo<hi){size_t m=lo+(hi-lo)/2;if(keys[m].h<h)lo=m+1;else hi=m;}while(lo<count&&keys[lo].h==h){size_t id=keys[lo++].i,at=i+1-width;if(!memcmp(body+at*56,anchors+id*width*56,width*56)){if(!counts[id])first[id]=at;if(counts[id]<cap)hits[id*cap+counts[id]]=at;if(counts[id]!=UINT32_MAX)counts[id]++;}}}free(keys);return 0;}
int anchor_find56(const uint8_t*b,size_t n,const uint8_t*a,size_t c,size_t w,uint64_t*f,uint32_t*k){return scan(b,n,a,c,w,f,k,NULL,0);}
int anchor_find56_many(const uint8_t*b,size_t n,const uint8_t*a,size_t c,size_t w,uint64_t*f,uint32_t*k,uint64_t*h,size_t cap){return scan(b,n,a,c,w,f,k,h,cap);}
