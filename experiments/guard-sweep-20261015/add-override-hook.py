"""Research-only hook for guard-sweep-20261015: apply GUARD_SWEEP_OVR after recipes."""
import sys
p = sys.argv[1]
s = open(p).read()
old = """pub fn build() -> Vec<Op> {
    clear_process_env();
    install_skywalk_submission_recipe();
    std::env::set_var("EXACT_PAIR_CARRY", "1");
    if LEAPFROG_SUBMISSION {
        leapfrog::install_recipe();
    }
"""
new = """pub fn build() -> Vec<Op> {
    // RESEARCH ONLY (guard-sweep-20261015): capture an explicit override list before the environment is cleared.
    let guard_sweep_ovr = std::env::var("GUARD_SWEEP_OVR").ok();
    clear_process_env();
    install_skywalk_submission_recipe();
    std::env::set_var("EXACT_PAIR_CARRY", "1");
    if LEAPFROG_SUBMISSION {
        leapfrog::install_recipe();
    }
    if let Some(ov) = guard_sweep_ovr {
        for kv in ov.split(';').filter(|k| !k.is_empty()) {
            let (k, v) = kv.split_once('=').unwrap();
            eprintln!("GUARD_SWEEP_OVR {k}={v}");
            std::env::set_var(k, v);
        }
    }
"""
assert s.count(old) == 1, "anchor not found exactly once"
open(p, "w").write(s.replace(old, new))
print("patched")
