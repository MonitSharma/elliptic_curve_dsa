#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
int scalar_fast_public(const unsigned char[32],unsigned char[64]);
static uint64_t state=0x9e3779b97f4a7c15ULL;
static uint64_t next(void){state^=state<<13;state^=state>>7;state^=state<<17;return state;}
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
int main(int argc,char **argv){
 unsigned char *in=malloc(4096*32),out[64];unsigned long long checksum=0;
 for(int j=0;j<4096*4;j++){uint64_t x=next();memcpy(in+j*8,&x,8);}
 memset(in,0,32);memset(in+32,0,32);in[63]=1;
 for(int j=0;j<4096;j++){scalar_fast_public(in+32*j,out);if(argc>1){for(int k=0;k<32;k++)printf("%02x",in[32*j+k]);putchar(' ');for(int k=0;k<64;k++)printf("%02x",out[k]);putchar('\n');}}
 double t=now();int count=100000;
 for(int j=0;j<count;j++){scalar_fast_public(in+32*(j%4096),out);checksum+=out[j%64];}
 double elapsed=now()-t;
 fprintf(stderr,"SCALAR_BENCH count=%d elapsed_s=%.6f us_per_scalar=%.6f checksum=%llu\n",count,elapsed,1e6*elapsed/count,checksum);
 free(in);return 0;
}
