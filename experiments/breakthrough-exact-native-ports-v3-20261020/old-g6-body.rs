        // x257's bit set: the chain now. x257 = AND(S'1[255] ^ h1, g0 ^ h1) ^ h1, so its fix is a CZ of the two forms
        // (the second is the wire m0) and a Z on h1: no Toffoli. Then m0 = g0
        c.push_condition(bitx);
        let (ra, rra) = chain(c);
        let ha = rra.last().expect("y21: the rebuilt chain is not empty").0;
        for w in [b[N - 1], s[2], s[1], ha] {
            c.cz(w, m0);
        }
        c.cz(ha, ha);
        c.cx(ha, m0);
        c.pop_condition();
        let bit0 = c.alloc_bit();
        c.hmr(m0, bit0);
        c.release_clean(m0);
        c.push_condition(bitx);
        c.push_condition(bit0);
        cmp0(c, &ra);
        c.pop_condition();
        unchain(c, rra);
        c.pop_condition();
        // x257's bit clear: m0 was measured as g0 ^ h1; with its bit set the chain, a Z on its top (h1), g0's compare
        c.push_condition(nbx);
        c.push_condition(bit0);
        let (rb, rrb) = chain(c);
        let hb = rrb.last().expect("y21: the rebuilt chain is not empty").0;
        c.cz(hb, hb);
        cmp0(c, &rb);
        unchain(c, rrb);
        c.pop_condition();
        c.pop_condition();
        e_m0 = c.expected_total();
        c.free_bit(nbx);
        c.free_bit(bitx);