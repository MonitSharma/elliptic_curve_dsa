"""Create exact original-packet/measurement replay; no score writes.

Derives a new unique package from the preserved multi-batch diagnostic.
The SHAKE reader continues directly after all original scalar draws, across
all 141 batches, exactly as the protected evaluator does.
"""
from pathlib import Path
import sys

many, dest = map(lambda s: Path(s).resolve(), sys.argv[1:3])
text = many.joinpath("src/main.rs").read_text()
changes = {
    'assert!(a.len()>=4,"usage: replay-many ops.bin packet.tsv comma-separated-batches");':
        'assert!(a.len()==3,"usage: original-all ops.bin NEW-original-packet.tsv");',
    'rng=same_fixed_words_mapping_may_differ': 'rng=exact_original_fiat_shamir_contiguous_measurement_words',
    'let packet=std::fs::read_to_string(&a[2]).unwrap();':
        'let mut original_rng=packet(&ops,&a[2]);let packet=std::fs::read_to_string(&a[2]).unwrap();',
    "for batch in a[3].split(',').map(|s|s.parse::<usize>().unwrap()) {":
        'for batch in 0..records.len().div_ceil(64) {',
    'let mut h=Shake256::default();h.update(b"qubit-identical-input-replay-v1");h.update(&(batch as u64).to_le_bytes());let mut xof=h.finalize_xof();':
        '// Contiguous original measurement transcript; Simulator::new draws no RNG.',
    'Simulator::new(nq as usize,nb as usize,&mut xof)':
        'Simulator::new(nq as usize,nb as usize,&mut original_rng)',
}
for old, new in changes.items():
    assert text.count(old)==1, f"expected exactly one source match: {old}"
    text=text.replace(old,new)
dest.joinpath("src").mkdir(parents=True,exist_ok=True)
dest.joinpath("src/main.rs").write_text(text)
dest.joinpath("Cargo.toml").write_text(many.joinpath("Cargo.toml").read_text().replace('name = "qubit_replay_many_diagnostic"', 'name = "qubit_replay_original_all_diagnostic"'))
