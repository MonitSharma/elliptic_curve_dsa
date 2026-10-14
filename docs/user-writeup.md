> Background material supplied by the user, preserved below. Treat commands and
> claims as historical leads; the current scorer/source and the workspace README
> determine actual behavior. This material does not authorize external actions.
> For resuming on a CPU server, see [SERVER_HANDOFF.md](SERVER_HANDOFF.md).

**ECDSA.fail** (created by **Eigen Labs** as part of their *Yukon / Open Autoresearch* initiative) is a competitive, open-source quantum cryptanalysis benchmark and leaderboard.

Despite the dramatic name, **it is not a live exploit breaking Bitcoin or Ethereum wallets today, nor does it require access to a physical quantum computer.** Instead, it is a pure **quantum circuit compilation and optimization challenge** written in **Rust**. Your goal is to write Rust code that generates the leanest possible **reversible fault-tolerant quantum circuit** for a single operation: **affine elliptic-curve point addition on `secp256k1**` (the curve securing Bitcoin and Ethereum signatures).

---

## 1. The Big Picture: Why Point Addition?

To break ECDSA with a future fault-tolerant quantum computer, an attacker runs **Shor’s algorithm for the Elliptic Curve Discrete Logarithm Problem (ECDLP)** to recover a private key $k$ from a public key $Q = [k]G$.

Inside Shor's algorithm, the quantum phase estimation (QPE) loop repeatedly executes a single dominant inner-loop primitive thousands of times: **controlled elliptic-curve point addition** over the prime field $\mathbb{F}_p$ where $p = 2^{256} - 2^{32} - 977$.

* **Peak Logical Qubits ($Q$):** Because point addition is repeated sequentially, the maximum number of logical qubits active simultaneously during a single point addition essentially dictates the **logical qubit width of the entire quantum computer** required to break Bitcoin.
* **Toffoli Gate Count ($T$):** On a fault-tolerant surface-code quantum computer, Clifford gates (`X`, `CNOT`, `CZ`, `H`, `S`) are relatively cheap, whereas non-Clifford **Toffoli (`CCX`) gates** require expensive **magic-state distillation**, dominating both hardware footprint and wall-clock runtime.

### The Backstory: Beating Google’s "Classified" Circuit

In March 2026, Google Quantum AI (Craig Gidney, Tanuj Khattar, et al.) published a paper showing a massive reduction in the quantum resources needed to break `secp256k1` (down to **1,175 logical qubits** or **2.1 million Toffolis** per point addition). Citing responsible disclosure, Google **withheld the actual quantum circuit**, releasing only a Zero-Knowledge Proof (ZKP) and a Rust verification harness proving that such a circuit existed.

Two months later, cryptographer André Schrottenloher reverse-engineered the core algorithmic trick (known as **dialog-GCD**), and Eigen Labs adapted Google's open-source Zenodo verifier into **ECDSA.fail**—turning the problem into an "Open Autoresearch" competition where humans and AI coding agents (Claude Opus, GPT-5 Codex, etc.) collaborate publicly. Within 72 hours, the open community beat Google's withheld circuit.

| Milestone / Operating Point | Avg. Toffoli Gates ($T$) | Peak Logical Qubits ($Q$) | Spacetime Score ($Q \times T$) | Relative to Google |
| --- | --- | --- | --- | --- |
| **Litinski (2023 Baseline)** | $8,190,000$ | $3,000$ | $24.57 \times 10^9$ | $8.21\times$ higher |
| **ECDSA.fail Initial Baseline** | $3,942,753$ | $2,715$ | $10.70 \times 10^9$ | $3.58\times$ higher |
| **Google Private Low-Qubit Point** | $2,700,000$ | $1,175$ | $3.17 \times 10^9$ | — |
| **Google Private Low-Gate Point** | $2,100,000$ | $1,425$ | $2.99 \times 10^9$ | Reference ($1.00\times$) |
| **Current Best $Q \times T$ Record (Oct 2026)** | **$766,713$** | **$1,236$** | **$0.948 \times 10^9$** | **68.3% lower** |
| **Current Low-Qubit Record (Oct 2026)** | $140,339,208$ | **$770$** | $108.06 \times 10^9$ | **34.5% fewer qubits** |

---

## 2. Does It Need a Quantum Simulation Result?

**Yes, your circuit is simulated to verify correctness—but you do NOT need a quantum computer, Qiskit/Cirq state-vector simulators, or supercomputing hardware.** Everything runs locally on your CPU in Rust.

If you have worked with quantum simulators before, you might wonder: *How can a standard laptop simulate a 1,236-qubit quantum circuit across 9,024 shots in a few seconds without needing $2^{1236}$ complex amplitudes?*

Here is the trick behind the challenge's built-in simulator (`src/sim.rs`, adapted directly from Tanuj Khattar and Craig Gidney's verifier):

1. **Basis-State Sufficiency by Linearity:** In Shor's algorithm, the point-addition circuit is a pure arithmetic oracle. By the linearity of quantum mechanics, if a reversible unitary circuit maps every computational basis state $\lvert x_1, y_1 \rangle \lvert 0 \rangle_{\text{anc}}$ to $\lvert (x_1, y_1) + (c_x, c_y) \rangle \lvert 0 \rangle_{\text{anc}}$ with **zero relative phase kickback**, it is mathematically guaranteed to work on an arbitrary quantum superposition $\sum \alpha_i \lvert x_i, y_i \rangle$.
2. **Toffoli + Clifford + Measurement-Based Uncomputation (MBU):** Fault-tolerant arithmetic circuits do not create arbitrary multi-qubit entangled states across data registers. They use reversible classical logic (`X`, `CNOT`, `CCX`/Toffoli) plus Gidney's **measurement-based uncomputation** (where an ancilla qubit initialized via a Toffoli gate is uncomputed using a Hadamard gate, a mid-circuit $Z$-measurement, and a classically conditioned `CZ` phase fixup).
3. **Bit-Wise Classical Simulation with Phase Tracking:** Because every computational basis input stays a computational basis state on the data wires, `src/sim.rs` tracks bit values and exact phase parity across **9,024 random test points simultaneously** (using bit-parallel words on your CPU) and verifies that all ancillae return to $\lvert 0 \rangle$ with zero net phase kickback.

---

## 3. What Exactly Do You Have to Do & What Counts as a Solution?

All challenge code lives in the open-source Rust repository [`Layr-Labs/ecdsafail-challenge`](https://github.com/Layr-Labs/ecdsafail-challenge).

### The Contract (`point_add::build`)

You are only allowed to edit files inside the `src/point_add/` directory. The benchmark harness calls your Rust function `point_add::build()`, which programmatically emits a sequence of reversible quantum circuit operations (`Op`s).

Your circuit consumes **four 256-element registers**:

* `target_x` (**256 qubits**): Holds the $x$-coordinate of the quantum accumulator point $P = (x_1, y_1)$.
* `target_y` (**256 qubits**): Holds the $y$-coordinate of the quantum accumulator point $P = (x_1, y_1)$.
* `offset_x` (**256 classical bits**): Holds the $x$-coordinate of a known classical point $C = (c_x, c_y)$.
* `offset_y` (**256 classical bits**): Holds the $y$-coordinate of a known classical point $C = (c_x, c_y)$.

Your circuit must **overwrite `(target_x, target_y)` in-place** with the affine elliptic-curve sum $(R_x, R_y) = (x_1, y_1) + (c_x, c_y)$ on `secp256k1`:


$$\lambda = (c_y - y_1) \cdot (c_x - x_1)^{-1} \bmod p$$

$$R_x = \lambda^2 - x_1 - c_x \bmod p, \qquad R_y = \lambda(x_1 - R_x) - y_1 \bmod p$$

### The 4 Strict Validity Rules

When you run the benchmark, the immutable harness (`src/main.rs`, `src/circuit.rs`, `src/sim.rs`, `src/weierstrass_elliptic_curve.rs`) hashes your gate stream using **Fiat-Shamir (SHAKE256)** to deterministically generate **9,024 random test pairs** (so you cannot hardcode or tune your circuit to fixed inputs). Your circuit is rejected (`FAIL`) if any of these four checks fail:

1. **Classical Correctness:** All 9,024 test shots must output the exact affine sum $(R_x, R_y)$ on `secp256k1`.
2. **Strict Reversibility (Ancilla Cleanliness):** Every ancilla qubit you allocate (`b.alloc()`) must be uncomputed back to $\lvert 0 \rangle$ before you free it (`b.free()`). At the end of the forward pass, every non-output qubit must be in state $\lvert 0 \rangle$.
3. **Phase Cleanliness:** The global/relative quantum phase across all 9,024 live shots must be **strictly zero**—no leftover phase kickback from sloppy measurement-based uncomputation.
4. **Forward $\circ$ Reverse Identity:** The harness runs your circuit forward and then runs its gate-reversed inverse backward, verifying that the exact initial state is restored on every single qubit.

### How Your Solution Is Scored

If all four checks pass (`OK`), your circuit receives a spacetime score written to `score.json` and `results.tsv`:


$$\text{Score} = \overline{\text{Toffoli}} \times \text{Peak Qubits}$$

* **$\overline{\text{Toffoli}}$:** The average number of executed Toffoli gates per shot across the 9,024 runs. (Clifford gates like `CNOT` and `X` are counted for diagnostics but carry zero weight in the score).
* **$\text{Peak Qubits}$:** The maximum number of simultaneously allocated qubits at any point during the circuit's execution.

**What counts as a winning/leaderboard submission?** You do not have to beat the single lowest $Q \times T$ score right away. The leaderboard tracks the **2D Pareto Frontier** of $(\text{Qubits}, \text{Toffolis})$. Any valid submission that pushes the Pareto curve **left** (fewer qubits at a given Toffoli level) or **down** (fewer Toffolis at a given qubit width) is recorded as a frontier advance on `ecdsa.fail`.

---

## 4. How to Participate: Step-by-Step Workflow

Because the repository uses an open autoresearch model, you always start from the **current best frontier circuits** already committed to the repo by previous contributors—you do not have to build a 256-bit elliptic curve adder from scratch.

1. **Install the ECDSA.fail CLI and Rust Toolchain:** Requires Rust 1.93.0 (pinned automatically via rust-toolchain).
Install the official CLI wrapper from Eigen Labs, which handles repository cloning, sandboxed verification, and leaderboard submissions:

```bash
curl -fsSL https://api.ecdsa.fail/install.sh | sh

```


2. **Authenticate with Your API Key:**
Go to [https://ecdsa.fail](https://ecdsa.fail), click **Sign in** in the top-right menu, generate an API key, and authenticate locally:

```bash
ecdsafail login YOUR_API_KEY

```


3. **Clone the Benchmark Repository:**
Pull the live benchmark workspace (which mirrors `Layr-Labs/ecdsafail-challenge` and includes `src/point_add/memory/` notes from prior human and AI solvers):

```bash
ecdsafail clone
cd ecdsafail-challenge

```

*(Tip: You can also inspect or checkout specific Pareto frontier points—such as the low-qubit 770Q branch or the low-Toffoli 1236Q branch—using `ecdsafail reset <commit-hash>`.)*


4. **Modify the Circuit in src/point_add/:**
Edit the Rust code inside `src/point_add/` (never modify `src/main.rs`, `src/circuit.rs`, `src/sim.rs`, or `Cargo.toml`). You can refactor subroutines manually or hook up an automated coding/research loop (such as Claude Code, Codex, or a local LLM/heuristic optimizer) to propose gate or register-allocation improvements.


5. **Run Local Verification and Scoring:**
Compile and run the 9,024-shot simulator locally to verify correctness and check your $Q \times T$ score:

```bash
cargo run --release -- --note "Describe your optimization here"
# Or via the CLI:
ecdsafail run

```

This appends a row to `results.tsv` showing `[timestamp, commit, Toffoli, Clifford, qubits, op_count, OK/FAIL, note]` and outputs `score.json`.


6. **Submit to the Public Leaderboard:** Only submit runs marked OK that improve your target Pareto point.
Once `score.json` shows a lower Toffoli count or lower peak qubit width with status `OK`, submit it to the server-side verifier:

```bash
ecdsafail submit

```


---

## 5. What Are Solvers Actually Optimizing Under the Hood?

If you open `src/point_add/`, you will see that modern circuits look very different from textbook quantum adders. To move the leaderboard today, participants focus on five concrete optimization levers:

1. **Dialog-GCD & Ping-Pong GCD (Modular Inversion):** Computing $(c_x - x_1)^{-1} \bmod p$ via the Extended Euclidean Algorithm is the single hardest step. Instead of keeping 256-bit Bézout coefficient registers live alongside $(u, v)$, the circuit runs a forward Euclidean loop that records only a compressed transcript of branch decisions ("dialog"), uncomputes/frees $(u, v)$, and replays the transcript backward into the output register. Recent breakthroughs ("Ping-Pong GCD" and "Jump-$k$") group multiple GCD steps together or select updates from low-order bits to eliminate full 256-bit comparators.
2. **"Runway" Qubit Recycling (Dynamic Register Sharing):** As the GCD variables $u$ and $v$ shrink by roughly 1 bit per iteration, their high-order qubits become $\lvert 0 \rangle$. Top submissions immediately free those high-order qubits ("the runway") and reallocate them on the fly to store the growing transcript or Bézout coefficients, keeping **peak live qubits** low.
3. **Transcript Compression Codecs:** Instead of using 2 or 3 raw qubits per Euclidean step to log the branch taken, solvers pack multiple transition symbols into dense encodings (e.g., base-5 codecs or tailored lookup graphs) to shave dozens of qubits off the peak width.
4. **Exploiting the `secp256k1` Pseudo-Mersenne Prime:** Because $p = 2^{256} - 2^{32} - 977$, $2^{256} \equiv 2^{32} + 977 \pmod p$. Specialized Karatsuba squarers and modular multipliers fold upper bits back into the lower register using tiny constant additions rather than generic Montgomery reduction.
5. **Peephole Gate Elimination & Constant Propagation:** Because `offset_x` and `offset_y` are classical bits, any Toffoli gate controlled on a classical bit simplifies to a free Clifford `CNOT` (or a no-op if the bit is `0`). Pushing classical constants deeper into adder trees and removing redundant uncomputation steps yields steady Toffoli reductions.

---

## Interactive Architecture Explorer: Inside the `secp256k1` Point-Addition Circuit

Step through the diagram below to see how `point_add::build()` processes the registers, where peak qubits and Toffoli gates are spent across each stage of the circuit, and how `sim.rs` validates the result:

---

*Note: While I retrieved the live leaderboard from `ecdsa.fail`, the full `Layr-Labs/ecdsafail-challenge` GitHub repository instructions, and the Eigen Labs technical blog post directly, I wasn't able to access the companion arXiv preprint (`arxiv.org/abs/2609.09582`) directly; the paper metrics above are drawn from the Eigen Labs blog and search metadata. If you want a deep dive into a specific section of that arXiv paper, you can paste the content here and I'll analyze it based on that.*