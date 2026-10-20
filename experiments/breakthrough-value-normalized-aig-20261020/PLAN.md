# Exact Boolean proof after complete semantic guard normalization

The prior one-round AIG had 3.13m variables and its proof checker timed out.
The exact semantic/cofactor IR removes most live measurement dependencies.
Run complete normalization on the same frozen6192 circuit, then apply the
byte-identical qualified AIG/CNF producer to the SAME first preserved failure.
Keep all original RNG outcomes arbitrary. Native29 plus24+3 protected value
comparisons required before treating the export as valid. No solver result
alone is a checked proof. No nonce screened/rejected, no statistical gate
rerun or circuit tuning. Numeric IR cache saved for future backend research;
it is not read or trusted by this experiment. All counts are verifier-only.
