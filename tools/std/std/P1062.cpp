// P1062 数列 · std（题面序列 = 「N 的二进制位 × k 的幂」）：
// 第 N 项 = Σ (N 的第 i 位为 1 ? k^i : 0)。用 __int128 防溢出后按十进制输出。
#include <bits/stdc++.h>
using namespace std;
int main(){
    long long k,N; if(!(cin>>k>>N)) return 0;
    __int128 p=1, ans=0;
    while(N>0){
        if(N&1) ans+=p;
        p*=k; N>>=1;
    }
    if(ans==0){ cout<<0<<"\n"; return 0; }
    string s; while(ans>0){ s+=char('0'+ans%10); ans/=10; }
    reverse(s.begin(),s.end()); cout<<s<<"\n"; return 0;
}
