/* Primitive-only test entry. All values are public synthetic test data. */
int sx_population(const uint64_t *input,size_t count,unsigned width,uint64_t *output){
 if(width<1||width>319)return 2;
 for(size_t at=0;at<count;at+=8){
  uint64_t lanes[5][8]={{0}};I a;
  for(size_t j=0;j<8&&at+j<count;j++)for(unsigned k=0;k<5;k++)lanes[k][j]=input[(at+j)*5+k];
  for(unsigned k=0;k<5;k++)a.l[k]=_mm512_loadu_si512(lanes[k]);
  a=sx(a,width);
  for(unsigned k=0;k<5;k++)_mm512_storeu_si512(lanes[k],a.l[k]);
  for(size_t j=0;j<8&&at+j<count;j++)for(unsigned k=0;k<5;k++)output[(at+j)*5+k]=lanes[k][j];
 }
 return 0;
}
