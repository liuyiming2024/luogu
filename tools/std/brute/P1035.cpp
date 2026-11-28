// P1035 朴素（二分 + Kahan 补偿求和，不同实现路径）：
// 不做线性扫描，改为二分答案 n，每次从头用 Kahan 补偿累加重新求和。
#include <bits/stdc++.h>
using namespace std;
long double Hn(long long n){
    long double s=0,c=0;
    for(long long i=1;i<=n;i++){
        long double y=1.0L/i - c, t=s+y;
        c=(t-s)-y; s=t;
    }
    return s;
}
int main(){
    long long k; if(!(cin>>k)) return 0;
    long long lo=1, hi=1;
    while(Hn(hi)<=k) hi*=2;
    while(lo<hi){ long long m=(lo+hi)/2; if(Hn(m)>k) hi=m; else lo=m+1; }
    cout<<lo<<'\n'; return 0;
}
