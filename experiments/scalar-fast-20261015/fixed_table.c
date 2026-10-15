/* Public-input, fixed-base table. This uses the pinned library's field,
 * group and batch-normalization routines; it is research tooling only. */
static secp256k1_ge_storage *public_fixed_table;
static unsigned public_fixed_window,public_fixed_rows,public_fixed_stride;
int scalar_fast_fixed_init(unsigned window){
 if(window<8||window>20||public_fixed_table)return 0;
 public_fixed_window=window;public_fixed_rows=(256+window-1)/window;public_fixed_stride=1u<<window;
 public_fixed_table=malloc((size_t)public_fixed_rows*public_fixed_stride*sizeof(*public_fixed_table));
 secp256k1_gej *work=malloc((size_t)public_fixed_stride*sizeof(*work));
 secp256k1_ge *affine=malloc((size_t)public_fixed_stride*sizeof(*affine));
 if(!public_fixed_table||!work||!affine)abort();
 secp256k1_gej base;secp256k1_gej_set_ge(&base,&secp256k1_ge_const_g);
 for(unsigned row=0;row<public_fixed_rows;row++){
  unsigned bits=256-row*window;if(bits>window)bits=window;unsigned size=1u<<bits;
  secp256k1_ge b;secp256k1_ge_set_gej_var(&b,&base);secp256k1_gej_set_infinity(&work[0]);
  for(unsigned j=1;j<size;j++)secp256k1_gej_add_ge_var(&work[j],&work[j-1],&b,NULL);
  secp256k1_ge_set_all_gej_var(affine,work,size);
  for(unsigned j=1;j<size;j++)secp256k1_ge_to_storage(&public_fixed_table[(size_t)row*public_fixed_stride+j],&affine[j]);
  for(unsigned j=0;j<window;j++)secp256k1_gej_double_var(&base,&base,NULL);
 }
 free(work);free(affine);return 1;
}
int scalar_fast_public_fixed(const unsigned char input_be[32],unsigned char output_xy_be[64]){
 secp256k1_scalar k;secp256k1_gej result;secp256k1_ge affine;
 secp256k1_scalar_set_b32(&k,input_be,NULL);
 if(secp256k1_scalar_is_zero(&k)){memset(output_xy_be,0,64);return 1;}
 secp256k1_gej_set_infinity(&result);
 for(unsigned row=0;row<public_fixed_rows;row++){
  unsigned bits=256-row*public_fixed_window;if(bits>public_fixed_window)bits=public_fixed_window;
  unsigned index=secp256k1_scalar_get_bits_var(&k,row*public_fixed_window,bits);
  if(index){secp256k1_ge point;secp256k1_ge_from_storage(&point,&public_fixed_table[(size_t)row*public_fixed_stride+index]);secp256k1_gej_add_ge_var(&result,&result,&point,NULL);}
 }
 secp256k1_ge_set_gej_var(&affine,&result);
 secp256k1_fe_normalize_var(&affine.x);secp256k1_fe_normalize_var(&affine.y);
 secp256k1_fe_get_b32(output_xy_be,&affine.x);secp256k1_fe_get_b32(output_xy_be+32,&affine.y);return 1;
}
