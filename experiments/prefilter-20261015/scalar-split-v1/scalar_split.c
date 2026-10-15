/* Public benchmark inputs only. Research tooling; not submission code.
 * Immutable original scalar_batch_original.c and pinned secp256k1 v0.7.1.
 * Initialize scalar_fast_fixed_init(window) once before creating threads.
 */
#include "scalar_batch_original.c"
static void split_store(const secp256k1_ge *point,unsigned char output[64]){
 if(point->infinity){memset(output,0,64);return;}
 secp256k1_ge p=*point;secp256k1_fe_normalize_var(&p.x);secp256k1_fe_normalize_var(&p.y);
 secp256k1_fe_get_b32(output,&p.x);secp256k1_fe_get_b32(output+32,&p.y);
}
/* Input count*64bytes scalar pairs; output count*192bytes P,A,dummySum=0.
 * Dummy sum MUST NOT be used as expected data. Caller tracks readiness.
 * Count0 succeeds without touching pointers or requiring initialization.
 */
int scalar_fast_inputs(unsigned count,const unsigned char *scalar_pairs_be,unsigned char *output_triples_be){
 if(count>64)return 0;if(count==0)return 1;
 if(!public_fixed_table||!scalar_pairs_be||!output_triples_be)return 0;
 secp256k1_gej work[128];secp256k1_ge affine[128];
 for(unsigned i=0;i<count;i++){
  public_fixed_projective(scalar_pairs_be+64*i,&work[2*i]);
  public_fixed_projective(scalar_pairs_be+64*i+32,&work[2*i+1]);
 }
 secp256k1_ge_set_all_gej_var(affine,work,2*count);
 for(unsigned i=0;i<count;i++){
  split_store(&affine[2*i],output_triples_be+192*i);
  split_store(&affine[2*i+1],output_triples_be+192*i+64);
  memset(output_triples_be+192*i+128,0,64);
 }
 return 1;
}
static int split_read(const unsigned char input[64],secp256k1_ge *point){
 unsigned char any=0;for(unsigned i=0;i<64;i++)any|=input[i];
 if(!any){secp256k1_ge_set_infinity(point);return 1;}
 secp256k1_fe x,y;
 if(!secp256k1_fe_set_b32_limit(&x,input)||!secp256k1_fe_set_b32_limit(&y,input+32))return 0;
 secp256k1_ge_set_xy(point,&x,&y);return secp256k1_ge_is_valid_var(point);
}
/* Input count*128bytes canonical affine P,A; output count*64bytes P+A.
 * Infinity encoding is (0,0). Finite inputs must be canonical on-curve points.
 * Count0 succeeds without touching pointers; no fixed table needed.
 * Any invalid point/count/pointer returns0 without changing output memory.
 */
int scalar_fast_add_pairs(unsigned count,const unsigned char *point_pairs_be,unsigned char *expected_be){
 if(count>64)return 0;if(count==0)return 1;if(!point_pairs_be||!expected_be)return 0;
 secp256k1_gej work[64];secp256k1_ge affine[64];
 for(unsigned i=0;i<count;i++){
  secp256k1_ge p,a;
  if(!split_read(point_pairs_be+128*i,&p)||!split_read(point_pairs_be+128*i+64,&a))return 0;
  secp256k1_gej_set_ge(&work[i],&p);secp256k1_gej_add_ge_var(&work[i],&work[i],&a,NULL);
 }
 secp256k1_ge_set_all_gej_var(affine,work,count);
 for(unsigned i=0;i<count;i++)split_store(&affine[i],expected_be+64*i);
 return 1;
}
