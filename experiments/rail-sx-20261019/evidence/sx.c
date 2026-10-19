static inline I sx(I a,unsigned w){
 unsigned k,top;
 if(w>256){k=4;top=320;}else if(w>192){k=3;top=256;}
 else if(w>128){k=2;top=192;}else if(w>64){k=1;top=128;}
 else{k=0;top=64;}
 V shift=cn(top-w);
 V v=_mm512_srav_epi64(_mm512_sllv_epi64(a.l[k],shift),shift);
 a.l[k]=v;V fill=_mm512_srai_epi64(v,63);
 for(unsigned j=k+1;j<5;j++)a.l[j]=fill;
 return a;
}
