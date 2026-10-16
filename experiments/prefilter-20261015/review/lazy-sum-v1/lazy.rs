impl LazyPacket{
 fn expected_one(&mut self,batch:usize,shot:usize,curve:&FastCurveC){
  assert!(shot<self.batches[batch].len());if self.expected_ready[batch]&(1u64<<shot)==0{let value=curve.expected_points(&[self.batches[batch][shot]])[0];self.batches[batch][shot].2=value;self.expected_ready[batch]|=1u64<<shot;}
 }
 fn expected_all(&mut self,curve:&FastCurveC){
  for batch in 0..self.batches.len(){let missing=(0..self.batches[batch].len()).filter(|shot|self.expected_ready[batch]&(1u64<<shot)==0).collect::<Vec<_>>();if missing.is_empty(){continue;}let points=missing.iter().map(|shot|self.batches[batch][*shot]).collect::<Vec<_>>();let values=curve.expected_points(&points);assert_eq!(values.len(),missing.len());for(shot,value)in missing.into_iter().zip(values){self.batches[batch][shot].2=value;self.expected_ready[batch]|=1u64<<shot;}}
 }
 fn assert_expected(&self,batch:usize,shot:usize){assert_ne!(self.expected_ready[batch]&(1u64<<shot),0,"unprepared expected curve sum");}
}
fn validate_lazy_packet(prefix:&Shake256,tail:&[Op],curve:&FastCurveC){
 assert!(curve.deferred());for(nonce,next)in[(1u64,0usize),(17,NUM_TESTS-11)]{
  let mut h=prefix.clone();for op in nonce_tail(tail,nonce){h.update(&record49(&op));}let reader=h.finalize_xof();
  let mut full=LazyPacket{reader:reader.clone(),next,batches:Vec::new(),expected_ready:Vec::new(),defer:false};let mut lazy=LazyPacket{reader,next,batches:Vec::new(),expected_ready:Vec::new(),defer:true};
  assert!(lazy.ensure(0,curve));assert_eq!(lazy.expected_ready[0],0);let last=lazy.batches[0].len()-1;lazy.expected_one(0,last,curve);lazy.assert_expected(0,last);assert_eq!(lazy.expected_ready[0],1u64<<last);assert!(full.ensure(0,curve));assert_eq!(lazy.batches[0][last],full.batches[0][last]);
  fill_packet(&mut full,curve);fill_packet(&mut lazy,curve);assert_eq!(full.next,lazy.next);assert_eq!(full.batches,lazy.batches);assert_eq!(full.expected_ready,lazy.expected_ready);
  let mut a=[0u8;128];let mut b=[0u8;128];XofReader::read(&mut full.reader,&mut a);XofReader::read(&mut lazy.reader,&mut b);assert_eq!(a,b);let shots=lazy.batches.iter().map(Vec::len).sum::<usize>();assert_eq!(shots,NUM_TESTS-next);
  eprintln!("DEFERRED_EXPECTED_READY_ALL_TRIPLES_AND_FINAL_READER_PASS nonce={nonce} shots={shots}");
 }
}
