#ifndef SCALAR_SPLIT_V1_H
#define SCALAR_SPLIT_V1_H
#ifdef __cplusplus
extern "C" {
#endif
int scalar_fast_fixed_init(unsigned window);
/* count<=64; scalar input count*64; output triples count*192.
   P(64),A(64),dummy expected(64 zero bytes). Track expected readiness. */
int scalar_fast_inputs(unsigned count,const unsigned char *scalars_be,unsigned char *triples_be);
/* count<=64; input affine P,A pairs count*128; output expected count*64.
   Infinity=(0,0); finite inputs canonical/oncurve. Invalid returns0. */
int scalar_fast_add_pairs(unsigned count,const unsigned char *points_be,unsigned char *expected_be);
#ifdef __cplusplus
}
#endif
#endif
