static inline __attribute__((always_inline)) V sx_word(V v,unsigned bits){
 V n=cn(64-bits);return _mm512_srav_epi64(_mm512_sllv_epi64(v,n),n);
}
static inline __attribute__((always_inline)) I sx(I a,unsigned w){
 if(w>256){a.l[4]=sx_word(a.l[4],w-256);return a;}
 if(w>192){a.l[3]=sx_word(a.l[3],w-192);a.l[4]=_mm512_srai_epi64(a.l[3],63);return a;}
 if(w>128){a.l[2]=sx_word(a.l[2],w-128);a.l[3]=a.l[4]=_mm512_srai_epi64(a.l[2],63);return a;}
 if(w>64){a.l[1]=sx_word(a.l[1],w-64);a.l[2]=a.l[3]=a.l[4]=_mm512_srai_epi64(a.l[1],63);return a;}
 a.l[0]=sx_word(a.l[0],w);a.l[1]=a.l[2]=a.l[3]=a.l[4]=_mm512_srai_epi64(a.l[0],63);return a;
}
