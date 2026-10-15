/* Batch public-input P, A, P+A preparation. Initialize fixed table once.
   Each pair occupies64inputbytes and192outputbytes, all big endian. */
static void public_fixed_projective(const unsigned char in[32],secp256k1_gej *result){
 secp256k1_scalar k;secp256k1_scalar_set_b32(&k,in,NULL);secp256k1_gej_set_infinity(result);
 for(unsigned row=0;row<public_fixed_rows;row++){
  unsigned bits=256-row*public_fixed_window;if(bits>public_fixed_window)bits=public_fixed_window;
  unsigned index=secp256k1_scalar_get_bits_var(&k,row*public_fixed_window,bits);
  if(index){secp256k1_ge point;secp256k1_ge_from_storage(&point,&public_fixed_table[(size_t)row*public_fixed_stride+index]);secp256k1_gej_add_ge_var(result,result,&point,NULL);}
 }
}
int scalar_fast_pairs(unsigned count,const unsigned char *scalar_pairs_be,unsigned char *output_points_be){
 if(count>64||!public_fixed_table)return 0;
 secp256k1_gej work[192];secp256k1_ge affine[192];
 for(unsigned i=0;i<count;i++){
  public_fixed_projective(scalar_pairs_be+64*i,&work[3*i]);
  public_fixed_projective(scalar_pairs_be+64*i+32,&work[3*i+1]);
  secp256k1_gej_add_var(&work[3*i+2],&work[3*i],&work[3*i+1],NULL);
 }
 secp256k1_ge_set_all_gej_var(affine,work,3*count);
 for(unsigned i=0;i<3*count;i++){
  if(affine[i].infinity){memset(output_points_be+64*i,0,64);continue;}
  secp256k1_fe_normalize_var(&affine[i].x);secp256k1_fe_normalize_var(&affine[i].y);
  secp256k1_fe_get_b32(output_points_be+64*i,&affine[i].x);
  secp256k1_fe_get_b32(output_points_be+64*i+32,&affine[i].y);
 }
 return 1;
}
int scalar_fast_reference_sum(const unsigned char a[32],const unsigned char b[32],unsigned char out[64]){
 secp256k1_scalar ka,kb,sum;unsigned char canonical[32];
 secp256k1_scalar_set_b32(&ka,a,NULL);secp256k1_scalar_set_b32(&kb,b,NULL);
 secp256k1_scalar_add(&sum,&ka,&kb);secp256k1_scalar_get_b32(canonical,&sum);
 return scalar_fast_public(canonical,out);
}
