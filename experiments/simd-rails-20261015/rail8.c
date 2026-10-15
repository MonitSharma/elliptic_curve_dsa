#include "rail8.h"
#include <immintrin.h>
typedef __m512i V;typedef __mmask8 M;typedef struct{V l[5];} I;
typedef struct{M sign;V extra;} Choice;
#define A(x,y) _mm512_and_si512(x,y)
#define X(x,y) _mm512_xor_si512(x,y)
#define O(x,y) _mm512_or_si512(x,y)
#define N(x) X(x,_mm512_set1_epi64(-1))
static inline V zero(void){return _mm512_setzero_si512();}
static inline V one(void){return _mm512_set1_epi64(1);}
static inline V cn(uint64_t x){return _mm512_set1_epi64((long long)x);}
static inline I add(I a,I b){I r;M carry=0;for(int i=0;i<5;i++){V s=_mm512_add_epi64(a.l[i],b.l[i]);M c=_mm512_cmp_epu64_mask(s,a.l[i],_MM_CMPINT_LT);V t=_mm512_mask_add_epi64(s,carry,s,one());carry=c|_mm512_cmp_epu64_mask(t,s,_MM_CMPINT_LT);r.l[i]=t;}return r;}
static inline I neg(I a){I b;for(int i=0;i<5;i++)b.l[i]=N(a.l[i]);I c={{one(),zero(),zero(),zero(),zero()}};return add(b,c);}
static inline I select_i(M m,I a,I b){I r;for(int i=0;i<5;i++)r.l[i]=_mm512_mask_blend_epi64(m,a.l[i],b.l[i]);return r;}
static inline I conditional_neg(I a,M m){return select_i(m,a,neg(a));}
static inline M negative(I a){return _mm512_movepi64_mask(a.l[4]);}
static inline M bit(I a,unsigned n){return _mm512_test_epi64_mask(a.l[n/64],cn(UINT64_C(1)<<(n%64)));}
static inline M different(I a,I b){M m=0;for(int i=0;i<5;i++)m|=_mm512_cmpneq_epi64_mask(a.l[i],b.l[i]);return m;}
static inline I arv(I a,V n){I r;V inv=_mm512_sub_epi64(cn(64),n);for(int i=0;i<4;i++)r.l[i]=O(_mm512_srlv_epi64(a.l[i],n),_mm512_sllv_epi64(a.l[i+1],inv));r.l[4]=_mm512_srav_epi64(a.l[4],n);return r;}
static inline I ar(I a,unsigned n){return arv(a,cn(n));}
static inline I sx(I a,unsigned w){M sign=bit(a,w-1);V fill=_mm512_movm_epi64(sign);for(unsigned i=0;i<5;i++){unsigned k=w>64*i?w-64*i:0;uint64_t m=k>=64?UINT64_MAX:((UINT64_C(1)<<k)-1);a.l[i]=O(A(a.l[i],cn(m)),A(fill,cn(~m)));}return a;}
static inline unsigned window_low(unsigned tick,unsigned anchor,unsigned *k){unsigned length=22;if(tick>=1)length=13;if(tick>=6)length=17;if(tick>=11)length=22;if(tick>=90)length=19;if(tick>=100)length=17;if(tick>=112)length=15;if(tick>=118)length=13;if(tick>=124)length=11;*k=length-2;return anchor>*k?anchor-*k:0;}
static inline V window(I a,unsigned width,unsigned low,unsigned k){if(width-1<=low)return zero();M sign=negative(a);V flip=_mm512_movm_epi64(sign);unsigned limb=low/64,off=low%64;V raw=X(a.l[limb],flip);V v=_mm512_srlv_epi64(raw,cn(off));if(limb<4)v=O(v,_mm512_sllv_epi64(X(a.l[limb+1],flip),cn(64-off)));unsigned count=k+2;if(count>width-1-low)count=width-1-low;return A(v,cn((UINT64_C(1)<<count)-1));}
static inline Choice choice(I t,I b,unsigned tw,unsigned bw,unsigned tick,unsigned anchor,int has_before,I before,M forced,int has_old_source,M old_source){
 M dq=bit(t,1)^bit(b,1);M z2=bit(t,2)^bit(b,2)^dq,z3=bit(t,3)^bit(b,3)^dq,z4=bit(t,4)^bit(b,4)^dq;
 M eq=negative(t)^negative(b)^dq,a1=(M)(~z2)&(M)(~z3),a2=a1&(M)(~z4),out=dq^(M)255^a2,v3=0;
 if(tick==0){out^=eq&z2;}else{unsigned k;unsigned low=window_low(tick,anchor,&k);V wt=window(t,tw,low,k),wb=window(b,bw,low,k);M y;
  if(has_before){y=_mm512_cmp_epu64_mask(wt,_mm512_slli_epi64(wb,1),_MM_CMPINT_GT);if(!has_old_source)old_source=negative(b);M not_flipped=(M)~(negative(before)^negative(t)^old_source^negative(b));M added=(M)~(negative(before)^old_source^forced);M veto=eq&(y^not_flipped);out^=veto&z2;v3=veto&(M)~z2&z3&added;out^=v3;}
  else{y=_mm512_cmp_epu64_mask(wt,_mm512_slli_epi64(wb,2),_MM_CMPINT_GT);out^=eq&(M)~y&z2;}
 }
 M k2=(M)~z2^a2^v3,dsel=out^dq,k1=dsel^(M)~z2^a1^v3;Choice c={out,O(_mm512_maskz_set1_epi64(k1,1),_mm512_maskz_set1_epi64(k2,2))};return c;
}
static inline unsigned min(unsigned a,unsigned b){return a<b?a:b;}
static inline unsigned max(unsigned a,unsigned b){return a>b?a:b;}
static inline unsigned bw(unsigned n,int fused,unsigned w,unsigned wn){return fused?min(n,min(w,wn)):n;}
static void walk(const RailStep *s,size_t n,I d,int divide,M *nonunit,M *overflow){
 I ps={{cn(UINT64_C(0xfffffffefffffc2f)),cn(UINT64_MAX),cn(UINT64_MAX),cn(UINT64_MAX),zero()}};
 I minusps=neg(ps);I r[2];r[0]=select_i(bit(d,0),add(d,minusps),d);r[1]=ar(add(r[0],select_i(bit(r[0],1),minusps,ps)),1);M over=0;
 for(size_t tick=0;tick<n;tick++){
  unsigned ti=tick%2,si=1-ti,w=s[tick].w,n0=s[tick].n0,n1=s[tick].n1,n2=s[tick].n2,nb=s[tick].nb,wn=s[min(tick+1,n-1)].w;
  int fused=divide&&tick>=42&&tick<131;unsigned forced=tick+1<n?2:0;int has_before=0,has_capture=0;I before=r[0];M lastsign=0;Choice captured={0,zero()};unsigned nk[2]={n0,n1},next[2]={n1,n2};
  for(unsigned j=0;j<forced;j++){
   I v=sx(r[ti],nk[j]);over|=different(v,r[ti]);r[ti]=v;v=sx(r[si],bw(nk[j],fused,w,wn));over|=different(v,r[si]);r[si]=v;
   I old=r[ti];M sign=bit(r[ti],1)^bit(r[si],1);v=ar(add(r[ti],conditional_neg(r[si],sign)),1);r[ti]=sx(v,nk[j]-1);over|=different(r[ti],v);
   if(j==1){before=old;has_before=1;lastsign=sign;if(tick!=0){unsigned tw=nk[j]-1,sw=min(bw(nk[j],fused,w,wn),tw);captured=choice(r[ti],sx(r[si],sw),max(tw,6),max(sw,6),tick,s[tick].anchor,1,old,sign,1,negative(r[si]));has_capture=1;}}
   if(fused&&j==0){r[ti]=sx(r[ti],min(nk[j]-1,next[j]));r[si]=sx(r[si],min(bw(nk[j],fused,w,wn),min(w,wn)));}
  }
  r[ti]=sx(r[ti],n2);r[si]=sx(r[si],bw(n2,fused,w,wn));Choice c=has_capture?captured:choice(r[ti],r[si],max(n2,6),max(bw(n2,fused,w,wn),6),tick,s[tick].anchor,has_before,before,lastsign,0,0);
  I v=ar(add(r[ti],conditional_neg(r[si],c.sign)),1);r[ti]=sx(v,n2-1);over|=different(r[ti],v);
  /* Arithmetic shift of a sign-extended nb-bit value is already sign-extended
   * at nb-extra bits, so the reference's final variable-width sx is redundant. */
  r[ti]=arv(sx(r[ti],nb),c.extra);for(unsigned side=0;side<2;side++){v=sx(r[side],wn);over|=different(v,r[side]);r[side]=v;}
  if(fused&&tick<130){RailStep next=s[tick+1];unsigned wnn=s[min(tick+2,n-1)].w;r[ti]=sx(r[ti],min(next.n0,min(next.w,wnn)));}
 }
 I one_i={{one(),zero(),zero(),zero(),zero()}},minusone=neg(one_i);M unit0=(M)~different(r[0],one_i)|(M)~different(r[0],minusone),unit1=(M)~different(r[1],one_i)|(M)~different(r[1],minusone);*nonunit=(M)~(unit0&unit1);*overflow=over;
}
int rail8_population(const RailStep *s,size_t n,const uint64_t *pairs,size_t count,uint8_t *flags){
 if(!n)return 1;for(size_t i=0;i<n;i++){if(s[i].w<1||s[i].w>319||s[i].n0<2||s[i].n0>319||s[i].n1<2||s[i].n1>319||s[i].n2<2||s[i].n2>319||s[i].nb<4||s[i].nb>319||s[i].anchor>319)return 2;}
 V idx=_mm512_set_epi64(56,48,40,32,24,16,8,0);for(size_t at=0;at<count;at+=8){I d1,d2;uint64_t padded[64]={0};const uint64_t *ptr=pairs+at*8;if(count-at<8){for(size_t j=0;j<count-at;j++)for(int k=0;k<8;k++)padded[8*j+k]=ptr[8*j+k];ptr=padded;}
  for(int k=0;k<4;k++){d1.l[k]=_mm512_i64gather_epi64(idx,ptr+k,8);d2.l[k]=_mm512_i64gather_epi64(idx,ptr+4+k,8);}d1.l[4]=d2.l[4]=zero();M a,b,c,d;walk(s,n,d1,1,&a,&b);walk(s,n,d2,0,&c,&d);M nonunit=a|c,overflow=b|d;for(size_t j=0;j<8&&at+j<count;j++)flags[at+j]=((nonunit>>j)&1)|(((overflow>>j)&1)<<1);
 }return 0;
}
