// P1028 数的计算 · 独立正确解（std）：f(n)=1+Σ_{i=1..⌊n/2⌋} f(i)，O(n) 递推。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; if(!(cin>>n)) return 0;
    static long long f[1005];
    for(int i=1;i<=n;i++){
        long long s=1;
        for(int j=1;j<=i/2;j++) s+=f[j];
        f[i]=s;
    }
    cout<<f[n]<<'\n'; return 0;
}
