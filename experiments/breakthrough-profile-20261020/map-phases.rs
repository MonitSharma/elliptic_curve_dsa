include!("io.rs");

fn locate(pre: &[Op], final_ops: &[Op], boundary: usize) -> (usize, usize) {
    if boundary == 0 { return (0, 0); }
    for width in [32usize, 64, 128, 256, 512] {
        let before = (width / 2).min(boundary);
        let start = boundary - before;
        let end = (start + width).min(pre.len());
        let needle = &pre[start..end];
        if needle.len() < 16 { continue; }
        let mut hits = Vec::new();
        for (i, window) in final_ops.windows(needle.len()).enumerate() {
            if window[0] == needle[0] && window[needle.len()-1] == needle[needle.len()-1]
                && window == needle {
                hits.push(i + before);
                if hits.len() > 1 { break; }
            }
        }
        if hits.len() == 1 { return (hits[0], needle.len()); }
    }
    panic!("No unique unchanged anchor spans prepass boundary {boundary}; no phase attribution allowed");
}

fn main() {
    let args: Vec<_> = std::env::args().collect();
    assert_eq!(args.len(), 5, "PREPASS FINAL INPUT_TSV OUTPUT_TSV");
    let pre = load_ops(&args[1]);
    let final_ops = load_ops(&args[2]);
    let mut text = String::new();
    let mut previous = 0;
    for line in std::fs::read_to_string(&args[3]).unwrap().lines() {
        let parts: Vec<_> = line.split('\t').collect();
        assert_eq!(parts.len(), 2);
        let b: usize = parts[1].parse().unwrap();
        let (mapped, anchor) = locate(&pre, &final_ops, b);
        assert!(previous <= mapped && mapped <= final_ops.len());
        previous = mapped;
        text += &format!("{}\t{mapped}\t{b}\t{anchor}\n", parts[0]);
    }
    assert!(previous <= final_ops.len());
    assert_eq!(final_ops.len()-previous, 96, "Only the frozen identity tail may follow final phase");
    text += &format!("identity_tail\t{}\t{}\t0\n",final_ops.len(),pre.len());
    std::fs::write(&args[4], &text).unwrap();
    print!("{text}");
}

#[cfg(test)] mod tests {
    use super::*;
    fn op(i:u64)->Op { let mut x=Op::empty();x.kind=OperationType::X;x.q_target=QubitId(i);x }
    #[test] fn shifted_unique_boundaries_are_exact() {
        let pre:Vec<_>=(0..400).map(op).collect();
        let mut post=pre.clone();post.splice(1..1,[op(999),op(998)]);
        assert_eq!(locate(&pre,&post,200).0,202);
        assert_eq!(locate(&pre,&post,400).0,402);
        assert_eq!(locate(&pre,&post,0).0,0);
    }
    #[test] #[should_panic] fn changed_seam_is_not_invented() {
        let pre:Vec<_>=(0..400).map(op).collect();
        let mut post=pre.clone();post[200]=op(999);
        locate(&pre,&post,200);
    }
    #[test] #[should_panic] fn repeated_anchor_is_not_unique() {
        let pre:Vec<_>=(0..400).map(op).collect();
        let post:Vec<_>=pre.iter().chain(pre.iter()).copied().collect();
        locate(&pre,&post,200);
    }
}
