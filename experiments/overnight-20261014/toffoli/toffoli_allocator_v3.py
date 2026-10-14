"""Preserve allocator v2 and test legitimate fresh quantum frontiers."""
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
AREA=ROOT/'research-output/overnight-20261014/toffoli'
SOURCE=AREA/'bank-product-v2-source/src/point_add'
TARGET=AREA/'bank-product-v3-source/src/point_add'

def main():
    TARGET.mkdir(parents=True,exist_ok=True)
    for p in SOURCE.glob('*.rs'):shutil.copyfile(p,TARGET/p.name)
    p=TARGET/'builder.rs';s=p.read_text()
    s=s.replace('pub(crate) fn toffoli_allocator_restore(&mut self,before:&(Vec<u32>,Vec<u32>,u32),after:&Self) {\n        assert_eq!(self.next_qubit,after.next_qubit,"bank allocator fresh-wire boundary");', '''pub(crate) fn toffoli_allocator_frontier(&self)->u32 {self.next_qubit}
    pub(crate) fn toffoli_allocator_restore(&mut self,before:&(Vec<u32>,Vec<u32>,u32),frontier:u32,after:&Self) {
        assert!(frontier<=self.next_qubit && self.next_qubit<=after.next_qubit,"bank allocator fresh-wire frontier bound");
        // The original body may introduce clean scratch IDs beyond the entry
        // frontier. Any unused original IDs have never appeared in a gate and
        // remain |0>; add them to metadata only to retain subsequent wire names.
        // This emits no gate, measurement, input-dependent control or reset.
        self.free_qubits.extend(self.next_qubit..after.next_qubit);
        self.next_qubit=after.next_qubit;''')
    s=s.replace('self.y42_alloc_set(before,&wanted.0,0,&wanted.1,wanted.2);', '''let mut extended=before.clone();
        extended.0.extend(frontier..after.next_qubit);
        // Unchanged setter checks both final scratch sets and classical
        // ownership, then restores the exact original emission ordering.
        self.y42_alloc_set(&extended,&wanted.0,0,&wanted.1,wanted.2);''')
    p.write_bytes(s.encode())
    p=TARGET/'y15_onefold.rs';s=p.read_text()
    s=s.replace('let before=c.y42_alloc_state();let mut fork=c.toffoli_allocator_fork();','let before=c.y42_alloc_state();let frontier=c.toffoli_allocator_frontier();let mut fork=c.toffoli_allocator_fork();')
    s=s.replace('Some((before,fork))','Some((before,frontier,fork))')
    s=s.replace('c.toffoli_allocator_restore(&before,&fork)','c.toffoli_allocator_restore(&before,frontier,&fork)')
    s=s.replace('toffoli_allocator_tests_v2.rs','toffoli_allocator_tests_v3.rs').replace('mod toffoli_allocator_tests_v2;','mod toffoli_allocator_tests_v3;')
    p.write_bytes(s.encode())
    TARGET.joinpath('toffoli_allocator_tests_v3.rs').write_bytes(HERE.joinpath('toffoli_allocator_tests_v3.rs').read_bytes().replace(b'\r\n',b'\n'))
    print('prepared allocator v3 source',TARGET)

if __name__=='__main__':main()
