"""Source-derived seed/tick0 integer contracts for frozen public4b.

Research arithmetic only. These helpers do not constitute a complete rejection
certificate and are not called by the nonce screener.
"""
P=(1<<256)-(1<<32)-977
F=(1<<32)+977
MASK=(1<<256)-1
def seed_half_word(T,width=53):
    assert 0<=T<=MASK and 33<=width<=256
    lowmask=(1<<width)-1
    corrected=(T&~lowmask)|((T-(F if T&1 else 0))&lowmask)
    return (corrected>>1)|((T&1)<<255)
def forward_fold_word(X,Nm,extra,width):
    assert 0<=X<(1<<259) and 0<=Nm<8 and 0<=extra<=3
    shift=3+extra;E=X>>256;L=X&MASK
    A=L+E+(E-Nm)*(F-1)
    digit=A*pow(F,-1,1<<shift)&((1<<shift)-1)
    C=E+(E-Nm-digit)*(F-1)
    lowmask=(1<<width)-1
    W=(L&~lowmask)|((L+C)&lowmask)
    return (W>>shift)|(digit<<(256-shift))
def tick0_oneadd_word(T,S,signs,extra,width=57):
    n0,n1,n2=signs
    a0=n2&(1-n1);a1=a0&n0
    j=1 if n1 else 0 if a0 else 2
    sc=n0^a0;tc=n2^a0^a1
    X=((MASK-T if tc else T)<<j)+(MASK-S if sc else S)
    return forward_fold_word(X,sc+(tc<<j),extra,width)
def t0_ideal_contract(T,signs,extra):
    """Conservative gate-admission facts; never a whole-circuit certificate."""
    S=seed_half_word(T)
    ideal=(T+(P if T&1 else 0))//2
    raw=tick0_oneadd_word(T,S,signs,extra)
    d=9-2*signs[0]-4*signs[1]-8*signs[2]
    ideal_result=(d*ideal*pow(1<<(3+extra),-1,P))%P
    return dict(seed_ideal=S==ideal,raw_oneadd=raw,
                oneadd_ideal=raw<P and raw==ideal_result)
