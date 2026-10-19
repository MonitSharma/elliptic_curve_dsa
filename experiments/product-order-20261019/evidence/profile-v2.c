#include <assert.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
extern size_t ZSTD_decompress(void*, size_t, const void*, size_t);
int main(int argc,char **argv){
 assert(argc==2);FILE *f=fopen(argv[1],"rb");assert(f);assert(!fseek(f,0,SEEK_END));long bytes=ftell(f);assert(bytes>16);rewind(f);unsigned char *input=malloc(bytes);assert(input);assert(fread(input,1,bytes,f)==(size_t)bytes);fclose(f);assert(!memcmp(input,"QECCOPSZ",8));uint64_t n;memcpy(&n,input+8,8);assert(n<20000000);uint64_t *v=malloc(n*56);assert(v);assert(ZSTD_decompress(v,n*56,input+16,bytes-16)==n*56);free(input);
 uint64_t counts[18]={0},hist[26]={0},qmax=0,bmax=0,barriers=0,len=0,maxlen=0,nonempty=0;
 for(uint64_t i=0;i<=n;i++){
  uint64_t k=i<n?v[i*7]:18;
  if(i<n){assert(k<18);counts[k]++;for(int j=1;j<=3;j++){uint64_t q=v[i*7+j];if(q!=UINT64_MAX&&q>=qmax)qmax=q+1;}for(int j=4;j<=5;j++){uint64_t b=v[i*7+j];if(b!=UINT64_MAX&&b>=bmax)bmax=b+1;}}
  if(i==n||k==0||k==1||k==2||k==15||k==16||k==17){if(i<n)barriers++;if(len){nonempty++;if(len>maxlen)maxlen=len;}unsigned bin=0;uint64_t x=len;while(x>1){x>>=1;bin++;}hist[bin]++;len=0;}else len++;
 }
 printf("{\"status\":\"SOURCE_STRUCTURE_PROFILE_ONLY\",\"ops\":%"PRIu64",\"num_qubits\":%"PRIu64",\"num_bits\":%"PRIu64",\"barriers\":%"PRIu64",\"nonempty_segments\":%"PRIu64",\"max_segment\":%"PRIu64",\"counts_by_kind\":[",n,qmax,bmax,barriers,nonempty,maxlen);
 for(int i=0;i<18;i++)printf("%s%"PRIu64,i?",":"",counts[i]);printf("],\"segment_floor_log2_histogram\":[");for(int i=0;i<26;i++)printf("%s%"PRIu64,i?",":"",hist[i]);printf("]}\n");free(v);return 0;
}
