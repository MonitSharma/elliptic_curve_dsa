# Direct dispatch in the disabled full pipeline

All 4,096 nonce dispositions match the frozen baseline. Protected zero-MR
shadow checks pass on 128 nonces and a partial window. Rejection remains
disabled; no nonce is selected and no production file changed.

Three alternating paired trials, 4,096 nonces and eight threads each:

| Trial | Original seconds | Direct dispatch seconds |
|---|---:|---:|
| 0 | 11.384474 | 11.147785 |
| 1 | 9.969237 | 9.258027 |
| 2 | 9.719929 | 8.743500 |

Median time falls 7.13%, from 9.969237 to 9.258027 seconds. Preparation dominates
the remaining work. This small loaded-server comparison does not establish a
new 48-thread search projection. No scored resource count follows.

Only the zero-MR C dispatch library differs; compact operations, source-bound
mask/transfer, scalar preparation, exact fallback and candidate-own Fiat inputs
remain the same. The component comparison separately checks every quantum and
classical word on 8,192 arbitrary lanes and 512 actual inputs. The new library
is pinned at SHA256
`1444e146e9359940123af3b951069c768313947f601d201b4bc391d8ac45cb95`.
