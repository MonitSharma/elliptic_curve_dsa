// Exact product closure in a specified truth-function subspace.
// Standalone research tool; no candidate/harness changes or quantum lower bound.
#include <array>
#include <bit>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <optional>
#include <random>
#include <string>
#include <utility>
#include <vector>
using Clock=std::chrono::steady_clock;
struct V{
 std::array<uint64_t,4>w{};
 bool any()const{return w[0]||w[1]||w[2]||w[3];}
 int high()const{for(int i=3;i>=0;--i)if(w[i])return i*64+63-std::countl_zero(w[i]);return -1;}
 bool bit(int p)const{return(w[p/64]>>(p%64))&1;}
 void flip(int p){w[p/64]^=uint64_t(1)<<(p%64);}
 V&operator^=(const V&v){for(int i=0;i<4;++i)w[i]^=v.w[i];return*this;}
 friend V operator^(V a,const V&b){return a^=b;}
 friend V operator&(V a,const V&b){for(int i=0;i<4;++i)a.w[i]&=b.w[i];return a;}
 bool operator==(const V&)const=default;
};
struct Basis{
 std::array<V,256>v{};std::array<uint64_t,256>c{};int rank=0;
 bool add(V x,uint64_t coeff=0){while(x.any()){int p=x.high();if(v[p].any()){x^=v[p];coeff^=c[p];}else{v[p]=x;c[p]=coeff;++rank;return true;}}return false;}
 std::optional<uint64_t> expr(V x)const{uint64_t coeff=0;while(x.any()){int p=x.high();if(!v[p].any())return{};x^=v[p];coeff^=c[p];}return coeff;}
 bool has(V x)const{return expr(x).has_value();}
 V residual(V x)const{V out;while(x.any()){int p=x.high();if(v[p].any())x^=v[p];else{x.flip(p);out.flip(p);}}return out;}
};
V constant(int n){V a;for(int i=0;i<(1<<n);++i)a.flip(i);return a;}
std::vector<V>inputs(int n){std::vector<V>v(n);for(int i=0;i<n;++i)for(int j=0;j<(1<<n);++j)if((j>>i)&1)v[i].flip(j);return v;}
V expression(const std::vector<V>&f,uint64_t mask,V one){V out;if(mask>>63)out=one;mask&=~(uint64_t(1)<<63);while(mask){unsigned j=std::countr_zero(mask);assert(j<f.size());out^=f[j];mask&=mask-1;}return out;}
struct Gate{uint64_t a,b;V value;};
struct Result{std::string status;std::vector<V>f;std::vector<Gate>g;Basis span;uint64_t scanned=0;double seconds=0;int closed_dimension=0;};
bool target_in(const Basis&b,const std::vector<V>&target){for(auto t:target)if(!b.has(t))return false;return true;}
Result solve(const std::vector<V>&initial,V one,const std::vector<V>&target,const Basis&allowed,const std::vector<std::pair<V,V>>&priority,uint64_t cap,Clock::time_point deadline,bool naive=false){
 auto start=Clock::now();Result r;r.f=initial;r.span.add(one,uint64_t(1)<<63);for(unsigned i=0;i<initial.size();++i)assert(r.span.add(initial[i],uint64_t(1)<<i));
 auto append=[&](uint64_t a,uint64_t b,V product){assert(allowed.has(product)&&!r.span.has(product));r.g.push_back({a,b,product});unsigned index=r.f.size();assert(index<32);r.f.push_back(product);assert(r.span.add(product,uint64_t(1)<<index));};
 while(!target_in(r.span,target)){
  bool found=false;
  for(auto[a,b]:priority){auto am=r.span.expr(a),bm=r.span.expr(b);if(am&&bm){V p=a&b;if(allowed.has(p)&&!r.span.has(p)){append(*am,*bm,p);found=true;break;}}}if(found)continue;
  const unsigned d=r.f.size();assert(d<32);uint64_t full=(uint64_t(1)<<d)-1,limit=std::min(full,cap);
  if(naive){for(uint64_t a=1;a<=full&&!found;++a)for(uint64_t b=1;b<=full;++b){V p=expression(r.f,a,one)&expression(r.f,b,one);if(allowed.has(p)&&!r.span.has(p)){append(a,b,p);found=true;break;}}}
  else{
   std::vector<std::vector<V>>matrix(d,std::vector<V>(d));for(unsigned i=0;i<d;++i)for(unsigned j=0;j<d;++j)matrix[i][j]=allowed.residual(r.f[i]&r.f[j]);
   std::vector<V>columns(d);V a;
   std::array<V,256>piv{};std::array<uint32_t,256>pc{};std::array<uint64_t,256>stamp{};
   for(uint64_t t=1;t<=limit&&!found;++t){
    unsigned flip=std::countr_zero(t);a^=r.f[flip];for(unsigned i=0;i<d;++i)columns[i]^=matrix[flip][i];uint64_t am=t^(t>>1);++r.scanned;
    for(unsigned i=0;i<d;++i){V cur=columns[i];uint32_t bm=uint32_t(1)<<i;
     while(cur.any()){int p=cur.high();if(stamp[p]==t){cur^=piv[p];bm^=pc[p];}else{stamp[p]=t;piv[p]=cur;pc[p]=bm;break;}}
     if(!cur.any()){V p=a&expression(r.f,bm,one);assert(allowed.has(p));if(!r.span.has(p)){append(am,bm,p);found=true;break;}}
    }
    if((t&1023)==0&&Clock::now()>=deadline){r.status="INCOMPLETE_TIME";break;}
   }
   if(!found&&r.status.empty()&&limit<full)r.status="INCOMPLETE_ENUMERATION_CAP";
  }
  if(!found){if(r.status.empty()){r.status="CLOSED_BELOW_TARGET";r.closed_dimension=d;}break;}
 }
 if(target_in(r.span,target))r.status="TARGET_REACHED";r.seconds=std::chrono::duration<double>(Clock::now()-start).count();return r;
}
void selftest(){
 std::mt19937_64 random(0x563A81B7);auto deadline=Clock::now()+std::chrono::seconds(60);
 for(int n=2;n<=3;++n)for(int trial=0;trial<150;++trial){auto in=inputs(n);auto one=constant(n);std::vector<V>target(2);for(auto&t:target)t.w[0]=random()&one.w[0];Basis w;w.add(one);for(auto x:in)w.add(x);for(auto x:target)w.add(x);
  auto a=solve(in,one,target,w,{},uint64_t(1)<<20,deadline);auto b=solve(in,one,target,w,{},uint64_t(1)<<20,deadline,true);assert(a.status==b.status&&a.span.rank==b.span.rank);for(auto x:a.f)assert(b.span.has(x));for(auto x:b.f)assert(a.span.has(x));
 }
 auto in=inputs(3);auto one=constant(3);V cubic=in[0]&in[1]&in[2];Basis w;w.add(one);for(auto x:in)w.add(x);w.add(cubic);auto blocked=solve(in,one,{cubic},w,{},1000,deadline);assert(blocked.status=="CLOSED_BELOW_TARGET");w.add(in[0]&in[1]);auto lifted=solve(in,one,{cubic},w,{},1000,deadline);assert(lifted.status=="TARGET_REACHED"&&lifted.g.size()==2);
 V majority=(in[0]&in[1])^(in[0]&in[2])^(in[1]&in[2]);Basis m;m.add(one);for(auto x:in)m.add(x);m.add(majority);auto one_gate=solve(in,one,{majority},m,{},1000,deadline);assert(one_gate.status=="TARGET_REACHED"&&one_gate.g.size()==1);
 std::cout<<"SELFTEST_PASS random_subspaces=300 independent_naive_closures=300 cubic_lift=1 quadratic_cancellation=1\n"<<std::flush;
}
V read(std::istream&s){V x;for(auto&w:x.w)s>>w;assert(s);return x;}
void write(const std::string&name,const Result&r,const Basis&allowed,const std::vector<V>&target){
 std::ofstream o(name+".result.txt");o<<"STATUS "<<r.status<<"\nGATES "<<r.g.size()<<"\nSPAN_RANK "<<r.span.rank<<"\nALLOWED_RANK "<<allowed.rank<<"\nSCANNED_A "<<r.scanned<<"\nCLOSED_FEATURE_DIMENSION "<<r.closed_dimension<<"\nSECONDS "<<r.seconds<<'\n';
 for(unsigned i=0;i<r.g.size();++i){auto g=r.g[i];o<<"GATE "<<i<<' '<<g.a<<' '<<g.b;for(auto w:g.value.w)o<<' '<<w;o<<'\n';}
 if(r.status=="TARGET_REACHED")for(unsigned i=0;i<target.size();++i){auto c=r.span.expr(target[i]);assert(c);o<<"OUTPUT "<<i<<' '<<*c<<'\n';}
 o.close();std::cout<<name<<" status="<<r.status<<" AND="<<r.g.size()<<" span="<<r.span.rank<<" allowed="<<allowed.rank<<" A_scanned="<<r.scanned<<" seconds="<<r.seconds<<'\n'<<std::flush;
}
int main(int argc,char**argv){assert(argc==2);selftest();std::ifstream input(argv[1]);int n,nt,np,nl;input>>n>>nt>>np>>nl;assert(n==8&&np==19&&nl==3);std::vector<V>in,target,lifts;std::vector<std::pair<V,V>>priority;for(int i=0;i<n;++i)in.push_back(read(input));for(int i=0;i<nt;++i)target.push_back(read(input));for(int i=0;i<np;++i){V a=read(input),b=read(input);priority.push_back({a,b});}for(int i=0;i<nl;++i)lifts.push_back(read(input));
 V one=constant(n);Basis u;u.add(one);for(auto x:in)u.add(x);for(auto x:target)u.add(x);assert(u.rank==25);auto deadline=Clock::now()+std::chrono::seconds(3600);const uint64_t cap=uint64_t(1)<<22;
 // Known nineteen-AND containing space is a control before searches.
 Basis control=u;for(auto x:lifts)control.add(x);assert(control.rank==28);auto base=solve(in,one,target,control,priority,cap,deadline);assert(base.status=="TARGET_REACHED"&&base.g.size()<=19);write("control19",base,control,target);
 auto pure=solve(in,one,target,u,priority,cap,deadline);write("pure16",pure,u,target);
 for(unsigned mask=1;mask<7;++mask){Basis allowed=u;for(unsigned j=0;j<lifts.size();++j)if((mask>>j)&1)allowed.add(lifts[j]);assert(allowed.rank==25+std::popcount(mask));auto r=solve(in,one,target,allowed,priority,cap,deadline);write("lift"+std::to_string(mask),r,allowed,target);}
}
