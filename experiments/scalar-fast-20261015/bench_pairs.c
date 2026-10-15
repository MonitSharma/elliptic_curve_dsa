#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>
int scalar_fast_fixed_init(unsigned);
int scalar_fast_pairs(unsigned,const unsigned char*,unsigned char*);
int scalar_fast_public(const unsigned char[32],unsigned char[64]);
int scalar_fast_reference_sum(const unsigned char[32],const unsigned char[32],unsigned char[64]);
static uint64_t state=0x9e3779b97f4a7c15ULL;
static uint64_t next(void){state^=state<<13;state^=state>>7;state^=state<<17;return state;}
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+1e-9*t.tv_nsec;}
int main(int argc,char**argv){
 double initial=now();if(!scalar_fast_fixed_init(argc>2?atoi(argv[2]):16))return 2;double startup=now()-initial;
 unsigned char in[64*64],out[64*192],reference[192];unsigned long long checksum=0;
 for(int j=0;j<64*8;j++){uint64_t x=next();memcpy(in+j*8,&x,8);}
 memset(in,0,64);in[63]=1;
 if(!scalar_fast_pairs(64,in,out))return 3;
 for(int i=0;i<64;i++){
  scalar_fast_public(in+64*i,reference);scalar_fast_public(in+64*i+32,reference+64);
  scalar_fast_reference_sum(in+64*i,in+64*i+32,reference+128);
  if(memcmp(reference,out+192*i,192)){fprintf(stderr,"PAIR_MISMATCH %d\n",i);return 1;}
 }
 FILE*f=argc>1?fopen(argv[1],"w"):NULL;
 if(f){for(int i=0;i<64;i++){for(int j=0;j<64;j++)fprintf(f,"%02x",in[64*i+j]);fputc(' ',f);for(int j=0;j<192;j++)fprintf(f,"%02x",out[192*i+j]);fputc('\n',f);}fclose(f);}
 double t=now();unsigned batches=2000;
 for(unsigned j=0;j<batches;j++){
  /* Fresh inputs prevent repeatedly timing one cache-resident table subset. */
  for(unsigned k=0;k<64*8;k++){uint64_t x=next();memcpy(in+k*8,&x,8);}
  if(!scalar_fast_pairs(64,in,out))return 4;checksum+=out[j%(64*192)];
 }
 double elapsed=now()-t;
 fprintf(stderr,"PAIR_BENCH shots=%u elapsed_s=%.6f us_per_shot=%.6f startup_s=%.6f checksum=%llu\n",batches*64,elapsed,1e6*elapsed/(batches*64),startup,checksum);
 return 0;
}
