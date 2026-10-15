"""Public-input direct-index comb, derived from the pinned MIT source."""
from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'secp256k1/src/ecmult_gen_impl.h').read_text()
s=s[s.index('static void secp256k1_ecmult_gen('):s.index('/* Setup blinding values')]
s=s.replace('static void secp256k1_ecmult_gen(', 'static void secp256k1_ecmult_gen_public(')
old='''            for (index = 0; index < COMB_POINTS; ++index) {
                secp256k1_ge_storage_cmov(&adds, &secp256k1_ecmult_gen_prec_table[block][index], index == abs);
            }'''
assert s.count(old)==1
s=s.replace(old,'''            /* Every scalar is a public benchmark input. */
            adds = secp256k1_ecmult_gen_prec_table[block][abs];''')
s=s.replace('secp256k1_gej_add_ge(r, r, &add);','secp256k1_gej_add_ge_var(r, r, &add, NULL);')
s=s.replace('secp256k1_gej_add_ge(r, r, &ctx->ge_offset);','secp256k1_gej_add_ge_var(r, r, &ctx->ge_offset, NULL);')
(root/'public_comb.h').write_text('/* Derived from bitcoin-core/secp256k1 v0.7.1, MIT; see COPYING.secp256k1. Public inputs only. */\n'+s)
p=root/'scalar_fast.c'
s=p.read_text()
if '#include "public_comb.h"' not in s:
 s+='''
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
'''
 p.write_text(s)
p=root/'bench.c'
s=p.read_text().replace('int scalar_fast_public(const unsigned char[32],unsigned char[64]);','int scalar_fast_public(const unsigned char[32],unsigned char[64]);\nint scalar_fast_public_comb(const unsigned char[32],unsigned char[64]);\nint scalar_fast_init(void);')
s=s.replace(' unsigned char *in=', ' scalar_fast_init();\n unsigned char *in=')
s=s.replace(' for(int j=0;j<4096;j++){scalar_fast_public(in+32*j,out);',' for(int j=0;j<4096;j++){unsigned char reference[64];scalar_fast_public(in+32*j,reference);scalar_fast_public_comb(in+32*j,out);if(memcmp(reference,out,64)){fprintf(stderr,"MISMATCH %d\\n",j);return 1;}')
s=s.replace('scalar_fast_public(in+32*(j%4096),out);','scalar_fast_public_comb(in+32*(j%4096),out);')
(root/'bench_comb.c').write_text(s)
