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
