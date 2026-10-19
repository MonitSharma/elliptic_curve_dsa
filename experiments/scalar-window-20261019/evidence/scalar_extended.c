/* Research-only public-input scalar preparation. Not submission code.
 * Uses bitcoin-core/secp256k1 v0.7.1 (MIT), pinned in VENDOR.txt.
 */
#include "secp256k1/src/secp256k1.c"

int scalar_fast_public(const unsigned char input_be[32], unsigned char output_xy_be[64]) {
    secp256k1_scalar k, zero;
    secp256k1_gej infinity, result;
    secp256k1_ge affine;
    secp256k1_scalar_set_b32(&k, input_be, NULL);
    if (secp256k1_scalar_is_zero(&k)) {
        memset(output_xy_be, 0, 64);
        return 1;
    }
    secp256k1_scalar_set_int(&zero, 0);
    secp256k1_gej_set_infinity(&infinity);
    /* All scalars here are public benchmark inputs. This variable-time
       routine must not be repurposed for signing or secret-key handling. */
    secp256k1_ecmult(&result, &infinity, &zero, &k);
    secp256k1_ge_set_gej_var(&affine, &result);
    secp256k1_fe_normalize_var(&affine.x);
    secp256k1_fe_normalize_var(&affine.y);
    secp256k1_fe_get_b32(output_xy_be, &affine.x);
    secp256k1_fe_get_b32(output_xy_be + 32, &affine.y);
    return 1;
}

#include "public_comb.h"
static secp256k1_ecmult_gen_context public_context;
/* Call once before creating worker threads. The initialized context is immutable. */
int scalar_fast_init(void){secp256k1_ecmult_gen_context_build(&public_context);return 1;}
int scalar_fast_public_comb(const unsigned char input_be[32],unsigned char output_xy_be[64]){
 secp256k1_scalar k;secp256k1_gej result;secp256k1_ge affine;
 secp256k1_scalar_set_b32(&k,input_be,NULL);
 if(secp256k1_scalar_is_zero(&k)){memset(output_xy_be,0,64);return 1;}
 secp256k1_ecmult_gen_public(&public_context,&result,&k);
 secp256k1_ge_set_gej_var(&affine,&result);
 secp256k1_fe_normalize_var(&affine.x);secp256k1_fe_normalize_var(&affine.y);
 secp256k1_fe_get_b32(output_xy_be,&affine.x);secp256k1_fe_get_b32(output_xy_be+32,&affine.y);return 1;
}

/* Public-input, fixed-base table. This uses the pinned library's field,
 * group and batch-normalization routines; it is research tooling only. */
static secp256k1_ge_storage *public_fixed_table;
static unsigned public_fixed_window,public_fixed_rows,public_fixed_stride;
int scalar_fast_fixed_init(unsigned window){
 if(window<8||window>24||public_fixed_table)return 0;
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
