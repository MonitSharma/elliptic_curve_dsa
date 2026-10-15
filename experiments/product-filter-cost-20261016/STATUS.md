# First concurrent candidate filter cost

Four12-thread processes account for262,144 fixed distinct nonces, with no pass.
Whole elapsed time including startup is157.384seconds. Worker wall times are
142.693/123.274/128.053/104.215seconds. One rare full fallback costs35.245seconds.
This identified the exact early-exit opportunity tested separately. All46
archived artifacts verify. This is a disabled timing test, not nonce selection
or a resource result. The later fused/early timing supersedes it operationally.
