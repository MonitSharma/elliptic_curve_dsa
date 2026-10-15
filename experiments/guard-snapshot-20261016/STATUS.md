# Guard restoration component passes; no circuit candidate

Exact Boolean ANF identities:4,160 through depth64. Unchanged protected
simulator:69,120 packed cases /4,423,680 lanes through depth8, every boundary,
arbitrary dirty quantum/classical inputs and mutable measurement guards.
All original quantum/classical/phase state and MR positions match; private
snapshots are clean. Restoring overwritten original guard bits fails55,880
negative controls. See THEOREM.md for the identity and required framing.

The21-artifact source/dependency/test archive independently verifies locally.
Its immutable protected test contains a two-CCX identity payload solely to
confirm that the temporary scope is global. This is a scope-control component,
not a generated cache candidate or resource result. The separate
global-scope-proposals-20261016 experiment checks source-only feasibility.
