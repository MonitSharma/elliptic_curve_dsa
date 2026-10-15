# Concurrent fused and early filter cost passes

Four persistent12-thread workers account for all262,144 fixed distinct nonces
in115.355seconds including startup, with no pass. Worker steady wall times are
100.560/98.378/96.062/95.870seconds. The same rare full fallback now takes1.458
seconds. All47 archived artifacts verify; no nonce is selected by this test.

At the qualified product25 census rate, measured resource cost projects a mean
19.609hours at48threads; conservative repeated startup gives23.148hours.
Ideal64-thread extrapolation is14.707–17.361hours. Both the actual48-thread
cost and ideal64-thread cost clear the about-one-day gate. Fresh-packet
independence and constant screening cost assumptions are explicit; completion
is not guaranteed in the mean time. See the separate accepted operational run.
