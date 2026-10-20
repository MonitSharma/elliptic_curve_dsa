
#[cfg(test)]mod grouped_plan_shape_tests{
use super::*;
fn check(rows:&[[i16;9]])->usize{let mut count=0;let mut last=0;for(i,r)in rows.iter().enumerate(){assert!(r[0]>=last&&r[0]<259);last=r[0];for(k,j)in[(r[1],r[2]),(r[3],r[4])]{if k==0{assert!((0..129).contains(&j));}else if k==1{assert!(j>=0&&(j as usize)<i);assert_ne!(rows[j as usize][8],0);assert!(rows[j as usize][1]>=0||rows[j as usize][3]>=0);}else{assert!(k<0);}}for j in[r[5],r[6],r[7]]{assert!(j<129);}assert!([0,1].contains(&r[8]));count+=usize::from(r[8]!=0&&(r[1]>=0||r[3]>=0));}assert_eq!(rows.last().unwrap()[0],258);assert_eq!(rows.last().unwrap()[8],0);count}
#[test]fn every_grouped_carry_parent_frame_and_full_tail_is_structurally_valid_and_bad_parent_is_detected(){let counts:Vec<_>=[G0,G1,G2,G3,G4,G5,G6,G7,G8,G9,G10,G11,G12,G13,G14,G15].iter().map(|r|check(r)).collect();assert_eq!(counts.iter().sum::<usize>(),9216);assert_eq!(*counts.iter().max().unwrap(),656);let mut bad=G0.to_vec();bad[1][3]=1;bad[1][4]=30000;assert!(std::panic::catch_unwind(||check(&bad)).is_err());}
}
