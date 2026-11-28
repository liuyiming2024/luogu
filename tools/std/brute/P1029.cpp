// P1029 朴素：双重枚举 P,Q 逐对判 gcd/lcm（对拍 y0≤2000）。
#include <bits/stdc++.h>
using namespace std;int main(){long long x,y;if(!(cin>>x>>y))return 0;int ans=0;
 for(long long P=x;P<=y;P+=x)for(long long Q=x;Q<=y;Q+=x)if(std::gcd(P,Q)==x&&P*Q/x==y)ans++;
 cout<<ans<<'\n';return 0;}
