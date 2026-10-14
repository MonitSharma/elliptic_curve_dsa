# Source-bound arithmetic boundary replay

The two gate-inert observers reproduce the original complete C5/B3 circuit streams exactly, with all binding assertions retained. Both emitted and finalized prefix hash domains are verified. A copy of the unchanged Y33 cleanup must reproduce the entire finalized raw operation vector exactly before any point is interpreted. Its exact insert/remove events remap each boundary; pending cleaned wires receive a logical overlay reconstructed from their old unconditional writes. One native overlay/source-mutation fault test passes. Final coordinates and phase on all271 points per source equal the separately archived whole-raw replay.

| Source | Packet | Boundary | Shots | Wrong x | Wrong y | Nonuniform sign |
|---|---|---|---:|---:|---:|---:|
| c5_raw | official_known_bad | coord-y-sub | 15 | 0 | 0 | 0 |
| c5_raw | official_known_bad | divide-seamed | 15 | 7 | 7 | 0 |
| c5_raw | official_known_bad | sub-square | 15 | 7 | 7 | 0 |
| c5_raw | official_known_bad | multiply-seamed | 15 | 12 | 14 | 0 |
| c5_raw | official_known_bad | final-coordinates | 15 | 12 | 14 | 0 |
| c5_raw | official_known_bad | before-y33 | 15 | 12 | 14 | 0 |
| c5_raw | official_known_bad | after-y33 | 15 | 12 | 14 | 0 |
| c5_raw | official_known_bad | before-finalize-records | 15 | 12 | 14 | 0 |
| c5_raw | official_known_bad | after-finalize-records | 15 | 12 | 14 | 0 |
| c5_raw | independent | coord-y-sub | 256 | 0 | 0 | 0 |
| c5_raw | independent | divide-seamed | 256 | 0 | 1 | 0 |
| c5_raw | independent | sub-square | 256 | 1 | 1 | 0 |
| c5_raw | independent | multiply-seamed | 256 | 1 | 1 | 0 |
| c5_raw | independent | final-coordinates | 256 | 1 | 1 | 0 |
| c5_raw | independent | before-y33 | 256 | 1 | 1 | 0 |
| c5_raw | independent | after-y33 | 256 | 1 | 1 | 0 |
| c5_raw | independent | before-finalize-records | 256 | 1 | 1 | 0 |
| c5_raw | independent | after-finalize-records | 256 | 1 | 1 | 0 |
| b3_raw | official_known_bad | coord-y-sub | 15 | 0 | 0 | 0 |
| b3_raw | official_known_bad | divide-seamed | 15 | 7 | 8 | 0 |
| b3_raw | official_known_bad | sub-square | 15 | 8 | 8 | 0 |
| b3_raw | official_known_bad | multiply-seamed | 15 | 13 | 15 | 0 |
| b3_raw | official_known_bad | final-coordinates | 15 | 13 | 15 | 0 |
| b3_raw | official_known_bad | before-y33 | 15 | 13 | 15 | 0 |
| b3_raw | official_known_bad | after-y33 | 15 | 13 | 15 | 0 |
| b3_raw | official_known_bad | before-finalize-records | 15 | 13 | 15 | 0 |
| b3_raw | official_known_bad | after-finalize-records | 15 | 13 | 15 | 0 |
| b3_raw | independent | coord-y-sub | 256 | 0 | 0 | 0 |
| b3_raw | independent | divide-seamed | 256 | 0 | 1 | 0 |
| b3_raw | independent | sub-square | 256 | 1 | 1 | 0 |
| b3_raw | independent | multiply-seamed | 256 | 1 | 1 | 0 |
| b3_raw | independent | final-coordinates | 256 | 1 | 1 | 0 |
| b3_raw | independent | before-y33 | 256 | 1 | 1 | 0 |
| b3_raw | independent | after-y33 | 256 | 1 | 1 | 0 |
| b3_raw | independent | before-finalize-records | 256 | 1 | 1 | 0 |
| b3_raw | independent | after-finalize-records | 256 | 1 | 1 | 0 |

First failing arithmetic boundary for the two requested cases:
- c5_raw point 249: multiply-seamed; wrong y.
- c5_raw point 8033: all documented boundary contracts pass.
- b3_raw point 249: multiply-seamed; wrong y.
- b3_raw point 8033: divide-seamed; wrong y.

All sampled boundaries have zero pending Y33 sites; the logical overlay therefore equals the physical values at these boundaries. The full copied transformation and prefix hash checks are still necessary because completed Y33 rewrites alter earlier operation content. Every sign extension is uniform, and all classical input words remain intact.

Final stream SHA256: C5 `49b35cf7640ebd529d76894eb8bef93ebf57e7e970fe14b3c27c8c5feb6e73e4`; B3 `0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce`. Exact observer patches, protected-file checks and source bindings are in the paired `c5/b3-body-boundaries-v2` receipts. Runtime replay binary: `7dcf3f9cbe43d35e06a72dacba3c43afa624ec754ec4326417ecf018df171466`.

Arithmetic expectations follow the actual seamed caller: subtraction leaves y=Ty−Ay; division leaves y=lambda and x=Tx+2Ax+squareOffset; signed square frame leaves x=Tx+2Ax−lambda²; multiplication leaves the final x and y=expectedFinalY+Ay; final subtraction yields final coordinates. At the square boundary the actual extra sign wires are checked and the signed residue is decoded using 2^256≡2^32+977 mod p.

These are finite, source-bound value observations. Phase uses the exact continuous finalized raw measurement transcript within each source, and final phase equals the archived raw replay. Intermediate phase can carry legitimate deferred correction; cross-source measurement transcripts are unaligned. No scored resource result or global arithmetic correctness is claimed. The first failed v1 mapping assertion and its source/binary/log remain preserved separately.
