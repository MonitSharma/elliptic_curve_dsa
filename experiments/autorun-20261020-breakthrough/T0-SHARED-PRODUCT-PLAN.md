# Next exact saving: share the phase letter AND with the forms fold

Parent is completed `breakthrough-core-loan-preflight-20261020`, v2 frozen
source, control13f6, candidate d6934faaa92d07c13cbdbe0297682595f21c290ebe88e8e1297f373b36e09989,
Q1233 / builderexpected763010.2. It passed20 native tests including before-
ladder room0..4 (low-budget controls use an unconstrained1250cap reference).
Full circuit is raw only. No benchmark, final gate or nonce search.

Source inspection found a duplicate, not yet implemented:

- `t0_forms_body` currently creates `T0Phase` with no owned AND under hard1233,
  then uses direct cubic phases at expected +127T over the old owned mode.
- `fold_fwd_forms` independently computes `tt = AND(k1,k2)`, records ownership
  in its `recs`, and keeps it through the final low-window phase queries.
- Restore one owned `T0Phase.t` in the full forms body, and pass it to an
  optional-borrowed-TT variant of `fold_fwd_forms`. Return `l(q)` for that TT
  without creating another AND or recording another erase. The phase owns
  and keeps it until `ph.finish`, AFTER `pop_chain(recs)` and all CsForms
  cleanup. Controls k1/k2 remain unchanged. This is a shared immutable value.
- The original phase owns a TT before the high-row queries, so no direct
  cubic phases are needed. The forms fold borrows it later. This should save
  128 expected raw Toffolis versus d693 (127 phase penalty plus one AND),
  subject to actual chunk planning and tests. Prediction is not a result.
- Adjust `fold_wires` in the body from31+(Y15_WIN-7) to30+(Y15_WIN-7) only
  when sharing. The phase's extra owned wire and fold's one fewer wire cancel
  at the old peak. Mid-chunk planning must use actual live width; don't assume
  unchanged peak. Baseline hard1234 stays byte-exact13f6 (sharing disabled).
- Keep `T0Phase::new`'s existing direct component behavior for old tests.
  Introduce a forced-owned constructor or internal make(...,owned) wrapper
  and call it ONLY in the shared body. Do not call `new` then silently add
  a product while leaving misleading PHASE_CUBIC_DIRECT diagnostics.
- Keep original `fold_fwd_forms` API as a wrapper passing None. Add inner
  optional borrowed-Qid API. Only full t0_forms_body passes Some(ph.t).
  Its other y26-stage-b caller and all existing paths stay unchanged.

Before complete generation, compare the old duplicate-TT and new shared-TT
forms oracle n8/n56: all14 independent small-core assignments, independent
upper words and classical phase flags, guards, every physical HMR coefficient,
full input restoration and phase equality. A T0Phase owner surrounds the
forms fold and outlives pop_chain. Check peak one lower and exactly one
less unconditional AND in this component. Then all19 retained controls.
Consider a full256-bit T0-body stress/measurement-flag coefficient control
for its lifetime/plan. Full native phase output may include inherited
approximate doubling behavior; preserve any mismatches and diagnose them.

Even a full128T saving leaves roughly35 rawT above the one-qubit exchange
against oldd9ae, and public54fc is another25 roundedT ahead. Postpasses and
all statistical gates still need proper treatment. No claim of a record.

Broader next width idea, not implemented: global1232 likely needs a prefix
peak30 rather than31 at forward130. Original fin1 prefix erases c2 early.
Build a separate original-input-frame truth model excluding c2, desired
fields+C6, and native component before changing preflight again. Current
fin0 helper loan cannot honestly claim prefix30. Never reduce a preflight
bound without a verified prefix implementation. Every old assertion stays.
