// Exact conservative symbolic certificate: abstract flags may overestimate
// randomness, but false means the Boolean output has no measurement variables.
#[derive(Clone,Copy)]struct Expr{kind:u8,a:u32,b:u32,random:bool}
struct Dag{nodes:Vec<Expr>,cache:std::collections::HashMap<(u8,u32,u32),u32>}
impl Dag{
 fn new()->Self{Self{nodes:vec![Expr{kind:0,a:0,b:0,random:false},Expr{kind:1,a:0,b:0,random:false}],cache:std::collections::HashMap::new()}}
 fn variable(&mut self,random:bool)->u32{let id=self.nodes.len()as u32;self.nodes.push(Expr{kind:2,a:id,b:0,random});id}
 fn complementary(&self,a:u32,b:u32)->bool{let x=self.nodes[a as usize];let y=self.nodes[b as usize];(x.kind==3&&x.a==1&&x.b==b)||(y.kind==3&&y.a==1&&y.b==a)}
 fn node(&mut self,k:u8,a:u32,b:u32)->u32{let key=(k,a,b);if let Some(id)=self.cache.get(&key){return *id;}let id=self.nodes.len()as u32;self.nodes.push(Expr{kind:k,a,b,random:self.nodes[a as usize].random||self.nodes[b as usize].random});self.cache.insert(key,id);id}
 fn factors(&self,k:u8,id:u32,out:&mut Vec<u32>){let n=self.nodes[id as usize];if n.kind==k&&out.len()<15{self.factors(k,n.a,out);self.factors(k,n.b,out);}else{out.push(id);}}
 fn xor(&mut self,a:u32,b:u32)->u32{if a==b{return 0;}if a==0{return b;}if b==0{return a;}let mut terms=Vec::with_capacity(20);self.factors(3,a,&mut terms);self.factors(3,b,&mut terms);terms.sort_unstable();let mut result=0;let mut i=0;while i<terms.len(){let x=terms[i];let mut j=i+1;while j<terms.len()&&terms[j]==x{j+=1;}if(j-i)%2==1&&x!=0{result=if result==0{x}else{let(a,b)=if result<x{(result,x)}else{(x,result)};self.node(3,a,b)};}i=j;}result}
 fn not(&mut self,a:u32)->u32{self.xor(1,a)}
 fn and(&mut self,a:u32,b:u32)->u32{if a==0||b==0{return 0;}if a==1{return b;}if b==1||a==b{return a;}let mut terms=Vec::with_capacity(20);self.factors(4,a,&mut terms);self.factors(4,b,&mut terms);terms.sort_unstable();terms.dedup();for(i,x)in terms.iter().enumerate(){if *x==0{return 0;}for y in &terms[i+1..]{if self.complementary(*x,*y){return 0;}}}let mut result=1;for x in terms{if x!=1{result=if result==1{x}else{let(a,b)=if result<x{(result,x)}else{(x,result)};self.node(4,a,b)};}}result}
}
