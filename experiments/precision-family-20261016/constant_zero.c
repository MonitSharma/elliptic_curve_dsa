#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#define NONE UINT64_MAX
static int8_t land(int8_t a,int8_t b){return a==0||b==0?0:a==1&&b==1?1:-1;}
static int8_t lxor(int8_t a,int8_t b){return a<0||b<0?-1:a^b;}
static int8_t store(int8_t old,int8_t c,int8_t value){return c==1?value:c==0?old:old==value?old:-1;}
int constant_zeros(const uint64_t*ops,size_t n,size_t nq,size_t nb,const size_t*queries,size_t nqueries,uint8_t*out,const int8_t*initialq,const int8_t*initialb){
 int8_t*q=malloc(nq),*b=malloc(nb),*stack=malloc(n+1);if(!q||!b||!stack)return 1;
 for(size_t i=0;i<nq;i++)q[i]=initialq[i];for(size_t i=0;i<nb;i++)b[i]=initialb[i];
 int8_t base=1;size_t depth=0,query=0;
 for(size_t i=0;i<n;i++){
  while(query<nqueries&&queries[query]==i){for(size_t j=0;j<nq;j++)out[query*nq+j]=q[j]==0;query++;}
  const uint64_t*r=ops+i*7;uint64_t k=r[0],a=r[1],u=r[2],t=r[3],bt=r[4],bc=r[5];
  int8_t c=bc==NONE?base:land(base,b[bc]);
  switch(k){
   case 3:b[bt]=lxor(b[bt],c);break;
   case 4:b[bt]=store(b[bt],c,0);break;
   case 5:b[bt]=store(b[bt],c,1);break;
   case 6:q[t]=lxor(q[t],c);break;
   case 8:q[t]=lxor(q[t],land(c,q[u]));break;
   case 10:{int8_t x=q[t],y=q[u];q[t]=store(x,c,y);q[u]=store(y,c,x);break;}
   case 11:q[t]=store(q[t],c,0);break;
   case 12:q[t]=store(q[t],c,0);b[bt]=store(b[bt],c,-1);break;
   case 13:q[t]=lxor(q[t],land(c,land(q[u],q[a])));break;
   case 15:stack[depth++]=base;base=c;break;
   case 16:if(!depth)return 2;base=stack[--depth];break;
   default:break;
  }
 }
 free(q);free(b);free(stack);return query==nqueries?0:3;
}
