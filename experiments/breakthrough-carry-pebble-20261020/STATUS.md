# Early carry erasure with regeneration

Three native component tests pass. Plain affine/parity addition with live
incoming carry and n>=5 saves one clean carry by erasing the first after the
second is built, then regenerating it after higher carries are released.
The trade is one additional CCX and HMR. Shared/empty rows, independent
constant terms, inverse and every physical RNG phase coefficient pass;
unsafe aliases reject before emission. All16 archive members verify locally.

The later phase-pebble component avoids regeneration using direct phase
repair. Neither component is a complete resource record or novelty claim.
