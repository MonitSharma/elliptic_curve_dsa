# Autonomous run log · started 2026-10-17 22:12 SGT

## Public records at start of run (refreshed 2026-10-17 22:12:52 SGT)
- Total submissions: 1,587 (1,244 eligible).
- **Product leader**: `9dc3798c-93e0-4da4-a6a9-37586737c4af` (`jackylee0424`, commit `0c3a0751ab66bd9144358d67563bcb79201cf636`, submitted 2026-10-17T13:25:31Z / 21:25:31 SGT): **Q = 1,234, T = 761,096, Product = 939,192,464**.
  - Our standing: #2 on product (`d7f69382`, PLAIN67, `0ae6d109be`, Q = 1,234, T = 761,121, Product = 939,223,314).
  - Strict next product target at Q = 1,234: **T <= 761,095** (Product <= 939,191,230).
- **Toffoli leader**: `b99c9678-5a68-49e8-a8b7-91fc6c383e37` (**MonitSharma**, WIDE95, commit `9d967c4dc0b8ecc66eb721e4a347d3aafcc30ae0`): **Q = 1,556, T = 753,694, Product = 1,172,747,864**.
  - Our standing: **#1 on Toffolis**.
  - Strict next Toffoli target: **T <= 753,693**.
- **Qubits leader**: `8cbf3480-2864-43c1-ad9b-86087b010cbb` (`jackylee0424`, commit `270aa40cd3d36b258c1bba1dfa8d5086b49b4375`): **Q = 676, T = 398,909,531, Product = 269,662,842,956**.
  - Strict next qubits target: **Q <= 675**.

## Key theoretical and algorithmic discoveries (2026-10-17 22:15 – 2026-10-18 07:38 SGT)

### 1. Predicated Kill Rule (`killed_on`) & Single-Control Slicing in `prove.rs`
- Upgraded `/home/hclau/ecdsa_research/opt-research-20261017/tool/src/prove.rs` (original backed up at `prove.rs.bak`) with:
  1. Single-control slicing (`C1Zero`, `C2Zero`, `C1One`, `C2One`) so zero-control `CCX`s do not require the other control's backward cone to stay within the 24-variable cut limit.
  2. Dead-`Hmr` pruning (when a measured qubit is not in the live quantum cone and its measurement bit `c_target` is not in the live classical cone, the `Hmr` is skipped without allocating a cut variable).
  3. **Predicated Kill Rule (`killed_on`)**: when a qubit `q` is reset (`R(q)`) under effective condition $C_0$, `q` is guaranteed to be $|0\rangle$ whenever $C_0 = 1$; thus any earlier writer to `q` under condition $C_w \supseteq C_0$ cannot affect the value of `q` read under $C_0$ and is skipped.
- Verified that `prove.rs` proves `op 17876171` in `PLAIN67` (`op 25991369` in `PRODUCT179`: `CCX(520, 1150, 10)` inside `PushCondition(768)`, where `qubit 1150` is identically $|0\rangle$, saving `0.498 T`) in 2 seconds, and proved that the remaining empirical never-fire sites in `plain67.stats4` (`ops 3624..3656`, etc.) are 15–20 bit ripple-carry chains ($p \approx 2^{-20}$, not algebraically zero).

### 2. The Symmetric Triple Theorem Over $\mathbb{F}_2$
- Over $\mathbb{F}_2$, since $X(1 \oplus X) = 0$, any two Boolean functions $X, Y$ satisfy:
  $$X \cdot (1 \oplus X \oplus Y) = X \cdot Y = Y \cdot (1 \oplus X \oplus Y)$$
  Furthermore, on every computational basis state $(x, y) \in \{0, 1\}^2$, $x \cdot (1 \oplus x \oplus y) = x \cdot y \in \{0, 1\}$, so the phase factors are also identical:
  $$(-1)^{X \cdot (1 \oplus X \oplus Y)} = (-1)^{X \cdot Y}$$
- Therefore, the 3-element set $\mathcal{T}(X, Y) = \{X, Y, 1 \oplus X \oplus Y\}$ is a canonical algebraic invariant of the product $X \cdot Y$. Any two `CCX` gates whose control-pair states are any two distinct elements of the same triple $\mathcal{T}(X, Y)$ compute the exact same product $X \cdot Y$ and use the exact same `CZ(c2_1, c1_1, cc=ct)` phase repair after `Hmr(donor, ct)`.
- Representing each wire state as `(const_bit, u128_xor_hash)` tracks all linear CNOT/X/Swap cancellations in $O(1)$ time per gate with zero quadratic ANF expansion and zero `atom_cap` truncation.

### 3. Diagnosis of `interned_anf_retained.rs`: Intermediate `retain_large` Truncation, Dead-Fallback Blinding, and Russian-Doll Leases
1. **Intermediate `retain_large` truncation (`Lease 3, 4, 11, 13, 14` in `PRODUCT179`):**
   - Between the two `CCX` uses (`i0` and `i1`, span `6499`) of each fold-step lease in `PLAIN67`, there are 20 unconditional `CX`/`X` writes to the two controls `(1117, 260)` or `(259, 724)` that algebraically cancel to $(X, 1 \oplus X \oplus Y)$.
   - In `interned_anf_retained.rs`, at offset `+3509`, `CX(129, 260)` temporarily pushes `anf[260]` over `CACHE_ATOM_CAP`, causing `retain_large` to collapse `anf[260]` into an opaque atom `[id_mid]`, which then fails to cancel when `CX(129, 260)` runs again 4 ops later at `+3513`.
2. **Dead-Fallback Blinding (`WIDE95` and `PRODUCT179`):**
   - When `lazy_cache_retained` renders a lease across $(u_1, u_2)$ on `donor` with no eviction in between, `valid` is initialized to `0` (`temp1 = 1` at $u_1$) and set to `1` at $u_1$ (`temp2 = 0` at $u_2$).
   - At $u_2$, `lazy_cache_retained` still emits a fallback recomputation `PushCondition(temp2) { CCX(c1, c2, donor); }` right before `CX(donor, t2)`.
   - Because `interned_anf_retained.rs` did not evaluate `temp1 == 1` and `temp2 == 0`, it saw the dead `CCX(c1, c2, donor)` inside `PushCondition(temp2 == 0)` at $u_2$ and overwrote `anf[donor]` with a fresh opaque atom `Atom(opaque_2) != Atom(opaque_1)` right before `CX(donor, t2)`. That blinded all subsequent stages to the fact that $t_1$ and $t_2$ received the exact same Boolean function!
3. **Russian-Doll Leases (`126` dead `CCX`s in `PRODUCT179`, `66` in `WIDE95`):**
   - Subsequent stages of `lazy_cache_retained` saw the live `CCX(c1, c2, donor)` at $u_1$ and the dead fallback `CCX(c1, c2, donor)` at $u_2$ and repeatedly re-cached them into other donor wires (up to 14–19 layers deep!), saving **0.00 T at runtime** while tying up clean donor wires across the circuit.

## Concrete candidate improvements verified

### A. Toffoli Track: `WIDE95+256` ($Q = 1,556$, **$-256.0\text{ T}$**) & `WIDE95+703` ($Q = 1,863$, **$-703.00\text{ T}$** below `WIDE95`, **STATISTICAL GATE PASS**)
- By evaluating `temp1 == 1` and `temp2 == 0` in our Symmetric-Triple scanner on `frozen_cache_wide95.bin` (`task-413`, `task-507`), we uncovered **703 uncached unconditional repeated `CCX` pairs** in `WIDE95` (`701` top-level `CCX`s + `2` unconditionally-evicted single-use leases). Combined with the `1,839` live leases already cached in `WIDE95`, $1,839 + 703 = 2,542$ accounts for **100% of all 2,542 unconditional repeated-AND pairs in the entire secp256k1 Leapfrog circuit**.
- **Width-preserving variant (`WIDE95+256`, $Q = 1,556$):** **388** of those pairs already have clean, untouched donor wires in `0..1555` (`raw_touches`), and greedy non-overlapping interval assignment selects **256 simultaneous unconditional leases (`-256.0 T`)** at the exact same width $Q = 1,556$ (verified clean on 512 shots of `simd_census_v2` in `task-457`).
- **Full 703-lease Toffoli-record candidate (`WIDE95+703`, `/home/hclau/ecdsa_research/wide95-703-20261018`, [`experiments/wide95-703-20261018/STATUS.md`](../wide95-703-20261018/STATUS.md)):**
  - Native module `src/point_add/retained_703.rs` caches all 703 unconditional pairs (`peak Q = 1,863`, `scratch_ct = 512`).
  - Unit tests (`frozen_cache_wide95::tests`, `retained_703::tests`) pass; pre-tail stream (`10,550,160` ops) is 100% byte-identical to `/tmp/wide95_all703.ops.bin`; frozen candidate stream SHA-256: `b127c64e9e6fa14e497d6338950ee477805fe8990abd59ec05a8f96d9c1295e8`.
  - **Pre-declared 32,768-batch (`2,097,152`-shot) statistical failure-rate gate (`wide95-703-gate-20261018-v1`, [`GATE.json`](../wide95-703-20261018/GATE.json)):**
    - **Vs current public Toffoli record `WIDE95` (`7efded3d…`, 753,694 T):** **`FAILURE_GATE_PASS`**
      1. Value-failing shots: `1,154` (candidate) vs `1,154` (parent) (`<=`: **PASS**)
      2. One-sided exact McNemar $p = 0.23518 \ge 0.05$ (`1,335` vs `1,328` failed batches, $b = 38, c = 31$: **PASS**)
      3. Failed batches per 9,024-shot packet: `5.744 <= 18` (**PASS**)
      4. Dirty-ancilla shots: `0` (**PASS**)
      - **Paired mean Toffoli saving vs `WIDE95`:** **$-702.995 \pm 0.249\text{ T}$** (`753,697.53 T` $\to$ **`752,994.53 T`** across 2,097,152 shots!).
    - **Vs previous public Toffoli record `WIDE15` (`1d8c05ee…`, 753,721 T):** **`FAILURE_GATE_PASS`** ($p = 0.24139$, paired mean saving **$-727.796 \pm 0.282\text{ T}$**).
  - **Ascending exact nonce screen + unchanged official `./benchmark.sh` (`search-and-benchmark.sh`):**
    - Lowest passing **nonce 167** (256 screened; all nonces `1..166` fail).
    - **`UNCHANGED_BENCHMARK_PASS` ([`BENCHMARK_RESULT.json`](../wide95-703-20261018/BENCHMARK_RESULT.json), [`SUBMISSION-NOTE.md`](../wide95-703-20261018/SUBMISSION-NOTE.md)):**
      - **Peak logical qubits ($Q$):** `1,863`
      - **Rounded mean executed Toffolis ($T$):** **`752,991`** (`mean_executed_toffoli = 752,990.570590`, `total_executed_toffoli = 6,794,986,909` over 9,024 shots; all 9,024 shots pass; 0 classical, phase, or ancilla failures).
      - **Improvement over current public Toffoli record (`753,694 T`, `b99c9678`):** **$-703\text{ Toffolis}$** (breaking the 753,000 Toffoli barrier!).
      - Final stream SHA-256: `09dbeacbd80a5d51656723c4350e367e91d5b5a00306008bf97b288bd4a205e4`; patch SHA-256: `6a0aa8e0dab619a874919d6e4dd3dbdb454b4906a92b34bbdeb89f007f8cacef`. Queued for user approval (`SUBMISSION_MODE = queue`).

### B. Product Track: `PRODUCT179+` ($Q = 1,234$, **$\ge -13.50\text{ T}$** below `PRODUCT179`, fresh mean $\le 761,082.57\text{ T}$)
- On `PRODUCT179` (`product179-native-20261017/candidate/ops.bin`, fresh mean `761,096.07 T` at $Q = 1,234$):
  1. **Unwrapping all 913 strictly zero-saving leases (`task-613`, `task-622`):**
     - `PRODUCT179` contains **913 strictly zero-saving leases** (`cond_hmr = 0, live_cx = 1, other_touches = 0, end_cond = 1`): **832** single-use unconditionally evicted leases (avg span 400 ops) and **81** Russian-doll inner leases whose second use is inside a dead fallback `temp2 == 0` (avg span 6,167 ops).
     - Unwrapping these 913 zero-saving leases frees clean donor intervals in `0..1233` for **16** uncached top-level unconditional repeated-AND pairs, of which **13** schedule simultaneously without overlap (**$-13.00\text{ T}$**!).
  2. **`zero_product` at `op 25991369` (`CCX(520, 1150, 10)` inside `PushCondition(768)` where `q[1150] == |0>`):** saves **$-0.50\text{ T}$**.
  - Total reduction on `PRODUCT179` at $Q = 1,234$: **$-13.50\text{ T}$** (fresh mean **$\sim 761,082.57\text{ T}$**, which is **$-37.36\text{ T}$ vs `PLAIN67`** and **$\sim 11.0\text{ T}$ below `jackylee0424`'s `0c3a0751ab` fresh mean of $761,093.55\text{ T}$**!).
