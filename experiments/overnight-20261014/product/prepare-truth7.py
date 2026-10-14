"""Create the exact seven-atom extension in an isolated source snapshot."""
from pathlib import Path
import sys

source = Path(sys.argv[1])
truth = (source / 'truth_simplify.rs').read_text()
truth = truth.replace('six', 'seven').replace('Six', 'Seven')
truth = truth.replace('SUPPORT_CAP: usize = 6', 'SUPPORT_CAP: usize = 7')
truth = truth.replace('table: u64', 'table: u128')
truth = truth.replace('-> u64', '-> u128')
truth = truth.replace('u64::MAX', 'u128::MAX').replace('1u64', '1u128')
truth = truth.replace('u64::from(value)', 'u128::from(value)')
truth = truth.replace('#[path = "product_simplify.rs"]', '#[path = "product7_simplify.rs"]')
(source / 'truth7_simplify.rs').write_text(truth, newline='\n')
(source / 'product7_simplify.rs').write_text((source / 'product_simplify.rs').read_text(), newline='\n')
mod = (source / 'mod.rs').read_text()
mod = mod.replace('mod truth_simplify;', 'mod truth_simplify;\nmod truth7_simplify;')
needle = '    let nonce: u64 = required_env("TAIL_NONCE");'
replacement = '''    // Exact extra pass after all position-bound public rewrites. No nonce search.
    let before = ops.len();
    ops = truth7_simplify::simplify_products(ops);
    eprintln!("PRODUCT_TRUTH7 before={before} after={} removed={}", ops.len(), before - ops.len());
'''
assert mod.count(needle) == 1
mod = mod.replace(needle, replacement + needle)
(source / 'mod.rs').write_text(mod, newline='\n')
