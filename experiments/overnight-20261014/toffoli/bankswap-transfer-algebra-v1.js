// Independent Boolean audit; no server/native circuit workload or synthesis.
function audit() {
  let mcxCases = 0;
  for (let row = 0; row < 512; row++) {
    const controls = Array.from({length: 5}, (_, i) => (row >> i) & 1);
    let target = (row >> 5) & 1;
    const dirty = Array.from({length: 3}, (_, i) => (row >> (6 + i)) & 1);
    const incomingTarget = target, incomingDirty = dirty.slice();
    for (let round = 0; round < 2; round++) {
      target ^= controls[4] & dirty[2];
      for (let i = 2; i >= 1; i--) dirty[i] ^= controls[i + 1] & dirty[i - 1];
      dirty[0] ^= controls[0] & controls[1];
      for (let i = 1; i <= 2; i++) dirty[i] ^= controls[i + 1] & dirty[i - 1];
    }
    const wanted = incomingTarget ^ controls.reduce((a, b) => a & b, 1);
    if (target !== wanted || dirty.some((x, i) => x !== incomingDirty[i])) throw Error('MCX mismatch');
    mcxCases++;
  }
  let fredkinCases = 0;
  for (let row = 0; row < 8; row++) {
    const control = row & 1, incomingA = (row >> 1) & 1, incomingB = (row >> 2) & 1;
    let a = incomingA, b = incomingB;
    a ^= b; b ^= control & a; a ^= b;
    if (a !== (control ? incomingB : incomingA) || b !== (control ? incomingA : incomingB)) throw Error('Fredkin mismatch');
    fredkinCases++;
  }
  const small = [[127, 1], [126, 2], [124, 4], [120, 8], [112, 16], [96, 32], [96, 64]];
  let selectedWords = 0;
  for (let word = 0; word < 256; word++) {
    const low = word & 127, bank = (low & 120) === 96;
    const count = small.filter(([mask, value]) => (low & mask) === value).length + Number(bank);
    if (count > 1) throw Error('selector overlap');
    if (bank) selectedWords++;
    if (word >= 1 && word <= 128 && ((count === 1) !== (word <= 103))) throw Error('active partition mismatch');
  }
  return {status: 'exact_transfer_permutation_algebra_verified', mcx_basis_cases: mcxCases,
    fredkin_basis_cases: fredkinCases, selector_words: 256, bank_selected_words: selectedWords,
    clean_selector_flag_required: true, measurement_operations_in_transfer: 0,
    transfer_CCX: 32, conjugating_pair_CCX: 64,
    limits: 'Transfer algebra only; admitted reserve cleanliness and reciprocal native/ALLMR phase remain separate.'};
}
if (typeof module !== 'undefined') module.exports = {audit};
if (typeof require !== 'undefined' && require.main === module) console.log(JSON.stringify(audit()));
