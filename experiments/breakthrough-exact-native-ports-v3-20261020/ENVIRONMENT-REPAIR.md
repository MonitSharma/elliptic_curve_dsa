The original v3 runner omitted PEBBLE_HARD_CAP for retained native tests.
The first rail strip test passes6,416,896 lanes, then retained tests0..11 pass;
tests12 stop at phase_fit::cap NotPresent before arithmetic execution. Original
run.exit1 and all logs remain. Resume sets the already required baseline1234
environment, changes NO source byte or guard, and reruns all16 filters under new
tests-env-* logs before the four originally declared cases. Source-freeze and
protected hashes must remain equal throughout. Result status is resumed.exit;
the original failed controller status remains recorded. No final gate/nonce.
