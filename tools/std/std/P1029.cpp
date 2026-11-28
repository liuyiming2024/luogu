// P1029 std：y0%x0==0 时答案 = 2^(y0/x0 的不同质因子数)。
#include <bits/stdc++.h>
using namespace std;int main(){long long x,y;if(!(cin>>x>>y))return 0;int ans=0;
 if(y%x==0){long long n=y/x;int cnt=0;for(long long p=2;p*p<=n;p++)if(n%p==0){cnt++;while(n%p==0)n/=p;}if(n>1)cnt++;ans=(1LL<<cnt);}
 cout<<ans<<'\n';return 0;}
