from pathlib import Path
root=Path(__file__).resolve().parent
(root/'scalar_fixed.c').write_text((root/'scalar_fast.c').read_text()+'\n'+(root/'fixed_table.c').read_text())
s=(root/'bench_comb.c').read_text().replace('scalar_fast_public_comb','scalar_fast_public_fixed')
s=s.replace('int scalar_fast_init(void);','int scalar_fast_fixed_init(unsigned);')
s=s.replace(' scalar_fast_init();',' if(!scalar_fast_fixed_init(argc>2?atoi(argv[2]):16))return 2;')
(root/'bench_fixed.c').write_text(s)
