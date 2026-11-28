// P1063 能量项链 · std（破环成链 + 区间 DP）：
// f[i][j] = 把 i..j 号珠合并成一颗（头 a[i]、尾 a[j+1]）的最大能量；
// f[i][j] = max_k f[i][k]+f[k+1][j]+a[i]*a[k+1]*a[j+1]，答案 max_s f[s][s+n-1]。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; if(!(cin>>n)) return 0;
    vector<long long> a(2*n+2);
    for(int i=1;i<=n;i++){ cin>>a[i]; a[i+n]=a[i]; }
    a[2*n+1]=a[1];
    vector<vector<long long>> f(2*n+2, vector<long long>(2*n+2,0));
    for(int len=2;len<=n;len++)
        for(int i=1;i+len-1<=2*n;i++){
            int j=i+len-1;
            for(int k=i;k<j;k++)
                f[i][j]=max(f[i][j], f[i][k]+f[k+1][j]+a[i]*a[k+1]*a[j+1]);
        }
    long long ans=0;
    for(int s=1;s<=n;s++) ans=max(ans, f[s][s+n-1]);
    cout<<ans<<'\n'; return 0;
}
