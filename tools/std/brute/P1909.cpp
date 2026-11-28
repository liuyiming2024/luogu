// P1909 朴素算法：不写取整公式，一盒一盒累加直到够 n 支，逐盒计数。
#include <bits/stdc++.h>
using namespace std;
int main(){
    long long n; if(!(cin>>n)) return 0;
    long long c[3],p[3];
    for(int i=0;i<3;i++) cin>>c[i]>>p[i];
    long long best = LLONG_MAX;
    for(int i=0;i<3;i++){
        long long have=0;
        for(long long b=1;b<=n+1;b++){
            have += c[i];
            if(have >= n){ best = min(best, b*p[i]); break; }
        }
    }
    cout<<best<<'\n'; return 0;
}
