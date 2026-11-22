
#include <cstdio>
typedef long long LL;
LL gcd(LL x,LL y){ return y?gcd(y,x%y):x; }
void sim(LL &x,LL &y) { LL d=gcd(x,y); x/=d,y/=d; }
void solve(LL a,LL b,LL c,LL d,LL &p,LL &q){
 sim(a,b),sim(c,d);
 LL x=a/b+1,y=(c-1)/d;
 if(x<=y) p=x,q=1;
 else if(!a) p=1,q=d/c+1;
 else if(a<=b&&c<=d) solve(d,c,b,a,q,p);
 else solve(a%b,b,c-d*(a/b),d,p,q),p+=q*(a/b);
}
int main() {
 LL a,b,c,d,p,q;
 while(~scanf("%lld%lld%lld%lld",&a,&b,&c,&d)) {
  solve(a,b,c,d,p,q);
  printf("%lld/%lld\n",p,q);
 }
 return 0;
}
