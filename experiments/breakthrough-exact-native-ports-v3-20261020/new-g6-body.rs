        // G6' (round-10 gate, own copy): x257's fix without the chain.  Top-column identity (exact): with u = m0 =
        // g0 ^ h1, the column sum at bit 255 gives h1 = MAJ(S'0[255], S'1[254], ~X1[255]) whenever g0 = h1, so
        // x257 = S'1[255]*u ^ (1 ^ u)*MAJ(S'0[255], S'1[254], ~X1[255]); tg[N - 1] holds X1[255] here (open ripple).
        // Its fix: CZ(S'1[255], m0), and Z * CZ(m0) on one MAJ wire (one Toffoli, measured erase).
        c.push_condition(bitx);
        for w in [b[N - 1], s[2], s[1]] {
            c.cz(w, m0);
        }
        let (fx, fy) = (Lin::of(&[b[N - 1], s[2], s[0]]), Lin::of(&[b[N - 2], s[2], s[1]]));
        let fc = Lin::of(&[tg[N - 1]]).x(&Lin::k(true));
        let q = maj_wire(c, &fx, &fy, &fc);
        c.cz(q, q);
        c.cz(q, m0);
        maj_wire_erase(c, q, &fx, &fy, &fc);
        c.pop_condition();
        let bit0 = c.alloc_bit();
        c.hmr(m0, bit0);
        c.release_clean(m0);
        // m0 = g0 ^ h1 with its bit set, whatever x257's bit: the chain, a Z on its top (h1), g0's compare
        c.push_condition(bit0);
        let (rb, rrb) = chain(c);
        let hb = rrb.last().expect("y21: the rebuilt chain is not empty").0;
        c.cz(hb, hb);
        cmp0(c, &rb);
        unchain(c, rrb);
        c.pop_condition();
        e_m0 = c.expected_total();
        c.free_bit(nbx);
        c.free_bit(bitx);