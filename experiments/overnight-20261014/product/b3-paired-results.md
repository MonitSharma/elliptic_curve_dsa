# B3 classical-factor transfer: exact finite pairing, failed qualification

Status: the coordinator's seven-CCX postpass candidate failed the unchanged official benchmark. It is not a qualified Toffoli or product record. The paired diagnostic confirms that the observed failures also occur in the clean public B3 circuit on the candidate's exact packet and measurement transcript.

The clean detached baseline is `b3c9fdd6e24bcd33450ab0d10884ab5ff9c46ab7`. Its unchanged protected builder completed with an empty source patch and stream SHA256 `0f10de57f45349c89163faf6e5ab0694aec3d3bfa720f10ee8b185a9fb2914ce`. The candidate stream is `ffcf319ca344c29e3b8cb6d04578c0a886b328fd64b4c18558d6a5ee7da9c93c`.

| Packet | Shots | All final q/classical/phase states equal | Value failures, both | Phase shots / batches, both | Ancilla batches, both |
|---|---:|---|---:|---:|---:|
| Candidate official packet and official measurement transcript | 9,024 | Yes | 15 | 15 / 14 | 0 |
| Fresh independent domain | 256 | Yes | 1 | 1 / 1 | 0 |
| Fresh structured domain | 256 | Yes | 189 | 142 / 4 | 0 |

The structured packet contains 128 admissible `P=-2A` cases and 128 admissible zero-slope cases. Both streams fail all 128 `-2A` y values and 61 zero-slope x values. The official candidate packet has13 x failures and15 y failures in both streams. The first official failure is shot249: x is correct and y is wrong in both circuits. Its complete target, offset, expected output and observed output are preserved in [b3-first249.txt](b3-first249.txt) and the complete candidate packet. [Coordinate-count correction](b3-coordinate-count-correction.md) retracts an earlier mistaken generalization from that first shot; no benchmark was rerun.

The private diagnostic reconstructs Fiat-Shamir from the **candidate** stream, makes the same 9,024 scalar-pair draws and applies the protected evaluator's skip rules. It clones the XOF after point generation and advances the measurement transcript continuously across batches for both streams. It first asserts exact equality of the entire `R`/`Hmr` operation sequence, including wires, classical slots and explicit conditions. Each batch compares every quantum slot, every classical slot and phase before clearing scratch. Independent and structured packets use fresh fixed B3 domains that do not depend on either stream hash.

The dedicated diagnostic crate is compiled against the clean B3 library; its source embeds that checkout path. Native binary SHA256 is `27c5e99e06a3779255fa6e85d0b3f8c2a49dd1641d467be8994d857527ee9aeb`. The protected evaluator, simulator and operation representation hashes are preserved in [b3-paired-receipt.json](b3-paired-receipt.json), along with packet, source, log and binary hashes. Native pairing is finite evidence, not a universal proof of the approximate point circuit. No nonce search, packet tuning, protected edits or diagnostic scores were used.

Server evidence: `/home/hclau/ecdsa_research/overnight-20261014/product-evidence/b3-paired`. Clean baseline evidence: `product-evidence/b3-baseline`; paired job PID2587484 completed exit0. The official candidate failure is owned and preserved by the coordinator separately.
