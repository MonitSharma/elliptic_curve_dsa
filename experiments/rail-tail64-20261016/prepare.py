from pathlib import Path
import hashlib,json,shutil,struct
root=Path(__file__).resolve().parent
old=root.parent/'rail-masks-20261016'
src=(old/'rail8_masks.c').read_text()
assert hashlib.sha256((old/'rail8_masks.c').read_bytes()).hexdigest()=='ee7adffc1c7f21a6721ede20d722a69d6e3ab8bc648db4a74c403f440b0d7ba3'
assert hashlib.sha256((old/'librail8_masks.so').read_bytes()).hexdigest()=='046dd5f1d11386550ec5234b955f6bc1974431e79a6b80499bda97da0ade3e90'
helper=r'''
/* All narrow-state values are mathematical signed integers fitting61 bits.
 * Intrinsics define every add/neg/shift, so no C signed-overflow premise. */
static inline V sx64(V a,unsigned w){unsigned n=64-w;return _mm512_srav_epi64(_mm512_sllv_epi64(a,cn(n)),cn(n));}
static inline M bit64(V a,unsigned n){return _mm512_test_epi64_mask(a,cn(UINT64_C(1)<<n));}
static inline M sign64(V a){return _mm512_movepi64_mask(a);}
static inline V cneg64(V a,M sign){return _mm512_mask_sub_epi64(a,sign,zero(),a);}
static inline V window64(V a,unsigned width,unsigned low,unsigned k){
 if(width-1<=low)return zero();
 V raw=X(a,_mm512_movm_epi64(sign64(a)));
 unsigned count=k+2;if(count>width-1-low)count=width-1-low;
 return A(_mm512_srlv_epi64(raw,cn(low)),cn((UINT64_C(1)<<count)-1));
}
static inline Choice choice64(V t,V b,unsigned tw,unsigned bw,unsigned tick,unsigned anchor,int has_before,V before,M forced,int has_old_source,M old_source){
 M dq=bit64(t,1)^bit64(b,1);M z2=bit64(t,2)^bit64(b,2)^dq,z3=bit64(t,3)^bit64(b,3)^dq,z4=bit64(t,4)^bit64(b,4)^dq;
 M eq=sign64(t)^sign64(b)^dq,a1=(M)(~z2)&(M)(~z3),a2=a1&(M)(~z4),out=dq^(M)255^a2,v3=0;
 if(tick==0){out^=eq&z2;}else{unsigned k;unsigned low=window_low(tick,anchor,&k);V wt=window64(t,tw,low,k),wb=window64(b,bw,low,k);M y;
  if(has_before){y=_mm512_cmp_epu64_mask(wt,_mm512_slli_epi64(wb,1),_MM_CMPINT_GT);if(!has_old_source)old_source=sign64(b);M not_flipped=(M)~(sign64(before)^sign64(t)^old_source^sign64(b));M added=(M)~(sign64(before)^old_source^forced);M veto=eq&(y^not_flipped);out^=veto&z2;v3=veto&(M)~z2&z3&added;out^=v3;}
  else{y=_mm512_cmp_epu64_mask(wt,_mm512_slli_epi64(wb,2),_MM_CMPINT_GT);out^=eq&(M)~y&z2;}
 }
 M k2=(M)~z2^a2^v3,dsel=out^dq,k1=dsel^(M)~z2^a1^v3;Choice c={out,O(_mm512_maskz_set1_epi64(k1,1),_mm512_maskz_set1_epi64(k2,2))};return c;
}
static void tail64(const RailStep *s,size_t n,size_t first,V r[2],int divide,M *overflow){
 M over=*overflow;
 for(size_t tick=first;tick<n;tick++){
  unsigned ti=tick%2,si=1-ti,w=s[tick].w,n0=s[tick].n0,n1=s[tick].n1,n2=s[tick].n2,nb=s[tick].nb,wn=s[min(tick+1,n-1)].w;
  int fused=divide&&tick>=42&&tick<131;unsigned forced=tick+1<n?2:0;int has_before=0,has_capture=0;V before=r[0];M lastsign=0;Choice captured={0,zero()};unsigned nk[2]={n0,n1},next[2]={n1,n2};
  for(unsigned j=0;j<forced;j++){
   V v=sx64(r[ti],nk[j]);over|=_mm512_cmpneq_epi64_mask(v,r[ti]);r[ti]=v;v=sx64(r[si],bw(nk[j],fused,w,wn));over|=_mm512_cmpneq_epi64_mask(v,r[si]);r[si]=v;
   V old=r[ti];M sign=bit64(r[ti],1)^bit64(r[si],1);v=_mm512_srai_epi64(_mm512_add_epi64(r[ti],cneg64(r[si],sign)),1);r[ti]=sx64(v,nk[j]-1);over|=_mm512_cmpneq_epi64_mask(r[ti],v);
   if(j==1){before=old;has_before=1;lastsign=sign;if(tick!=0){unsigned tw=nk[j]-1,sw=min(bw(nk[j],fused,w,wn),tw);captured=choice64(r[ti],sx64(r[si],sw),max(tw,6),max(sw,6),tick,s[tick].anchor,1,old,sign,1,sign64(r[si]));has_capture=1;}}
   if(fused&&j==0){r[ti]=sx64(r[ti],min(nk[j]-1,next[j]));r[si]=sx64(r[si],min(bw(nk[j],fused,w,wn),min(w,wn)));}
  }
  r[ti]=sx64(r[ti],n2);r[si]=sx64(r[si],bw(n2,fused,w,wn));Choice c=has_capture?captured:choice64(r[ti],r[si],max(n2,6),max(bw(n2,fused,w,wn),6),tick,s[tick].anchor,has_before,before,lastsign,0,0);
  V v=_mm512_srai_epi64(_mm512_add_epi64(r[ti],cneg64(r[si],c.sign)),1);r[ti]=sx64(v,n2-1);over|=_mm512_cmpneq_epi64_mask(r[ti],v);
  r[ti]=_mm512_srav_epi64(sx64(r[ti],nb),c.extra);for(unsigned side=0;side<2;side++){v=sx64(r[side],wn);over|=_mm512_cmpneq_epi64_mask(v,r[side]);r[side]=v;}
  if(fused&&tick<130){RailStep next=s[tick+1];unsigned wnn=s[min(tick+2,n-1)].w;r[ti]=sx64(r[ti],min(next.n0,min(next.w,wnn)));}
 }
 *overflow=over;
}
/* A whole-suffix predicate handles changed/nonmonotone tables conservatively. */
static size_t narrow_first(const RailStep *s,size_t n){size_t first=n;for(size_t i=n;i>1;i--){RailStep t=s[i-1];if(t.w>61||t.n0>61||t.n1>61||t.n2>61||t.nb>61)break;first=i-1;}return first;}
'''
# Helpers depend only on the unchanged width/window/min/max definitions.
pos=src.index('static void walk(')
src=src[:pos]+helper+'\n'+src[pos:]
src=src.replace('I d,int divide,M *nonunit,M *overflow){','I d,int divide,size_t first,M *nonunit,M *overflow){',1)
needle=' for(size_t tick=0;tick<n;tick++){\n'
replacement=''' for(size_t tick=0;tick<n;tick++){
  if(tick==first){V nr[2]={r[0].l[0],r[1].l[0]};tail64(s,n,tick,nr,divide,&over);for(unsigned side=0;side<2;side++){r[side].l[0]=nr[side];for(unsigned k=1;k<5;k++)r[side].l[k]=_mm512_srai_epi64(nr[side],63);}break;}
'''
assert src.count(needle)==1;src=src.replace(needle,replacement)
needle=' V idx=_mm512_set_epi64'
assert src.count(needle)==1;src=src.replace(needle,' size_t first=narrow_first(s,n);\n V idx=_mm512_set_epi64')
src=src.replace('walk(s,n,d1,1,&a,&b);walk(s,n,d2,0,&c,&d);','walk(s,n,d1,1,first,&a,&b);walk(s,n,d2,0,first,&c,&d);')
# A second entry is test-only and exercises the unchanged generic path.
src+='\nint rail8_tail_first(const RailStep *s,size_t n){return (int)narrow_first(s,n);}\n'
# Test wrappers compare the complete independent generic loop body with the
# narrow loop for arbitrary signed entry rails, not only physical input pairs.
baseline=(old/'rail8_masks.c').read_text()
loop_start=baseline.index(' for(size_t tick=0;tick<n;tick++){')
loop_end=baseline.index('\n I one_i=',loop_start)
generic_loop=baseline[loop_start:loop_end].replace('tick=0;','tick=first;',1)
src+='''
int rail8_test_suffix(const RailStep *s,size_t n,size_t first,const uint64_t *in,uint64_t *out,int divide,int narrow){
 V a=_mm512_loadu_si512(in),b=_mm512_loadu_si512(in+8);M over=0;
 if(narrow){V r[2]={a,b};tail64(s,n,first,r,divide,&over);_mm512_storeu_si512(out,r[0]);_mm512_storeu_si512(out+8,r[1]);}
 else{I r[2];r[0].l[0]=a;r[1].l[0]=b;for(unsigned k=1;k<5;k++){r[0].l[k]=_mm512_srai_epi64(a,63);r[1].l[k]=_mm512_srai_epi64(b,63);}
'''+generic_loop+'''
 _mm512_storeu_si512(out,r[0].l[0]);_mm512_storeu_si512(out+8,r[1].l[0]);
 }
 return over;
}
'''
(root/'rail8_tail64.c').write_text(src);shutil.copyfile(old/'rail8.h',root/'rail8.h')
sb=(root.parent/'simd-rails-20261015/steps.bin').read_bytes();steps=list(struct.iter_unpack('<6I',sb))
first=len(steps)
for i in range(len(steps)-1,0,-1):
 if max(steps[i][:5])>61:break
 first=i
result={'first_tick':first,'tail_ticks':len(steps)-first,'table_sha256':hashlib.sha256(sb).hexdigest(),'first_row':steps[first],'max_suffix_width':max(max(row[:5]) for row in steps[first:]),'all_suffix_widths_nonincreasing':all(all(steps[i+1][j]<=steps[i][j] for j in range(5)) for i in range(first,len(steps)-1)),'source_sha256':hashlib.sha256(src.encode()).hexdigest()}
(root/'SOURCE_PLAN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
