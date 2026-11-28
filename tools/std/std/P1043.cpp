// P1043 数字游戏 · std（破环成链 + 区间 DP）：
// 复制一遍，枚举起点，f_min/f_max[t][i] = 前 t 段覆盖到 i 的最小/最大乘积；
// 段和对 10 取模按题面「负数正数取模均为非负值」处理。
#include <bits/stdc++.h>
using namespace std;
int md(long long x){ long long v=x%10; if(v<0)v+=10; return (int)v; }
int main(){
    int n,m; if(!(cin>>n>>m)) return 0;
    vector<long long> a(2*n+1,0);
    for(int i=1;i<=n;i++){ cin>>a[i]; a[i+n]=a[i]; }
    const int INF=1e9;
    int gmin=INF, gmax=-INF;
    for(int s=1;s<=n;s++){
        vector<long long> ps(2*n+1,0);
        for(int i=1;i<=2*n;i++) ps[i]=ps[i-1]+a[s+i-1];
        vector<vector<int>> fmin(m+1, vector<int>(n+1,INF)),
                            fmax(m+1, vector<int>(n+1,-INF));
        fmin[0][0]=fmax[0][0]=1;
        for(int t=1;t<=m;t++)
            for(int i=t;i<=n;i++)
                for(int j=t-1;j<i;j++){
                    if(fmin[t-1][j]>=INF) continue;
                    int v=md(ps[i]-ps[j]);
                    fmin[t][i]=min(fmin[t][i], fmin[t-1][j]*v);
                    fmax[t][i]=max(fmax[t][i], fmax[t-1][j]*v);
                }
        gmin=min(gmin,fmin[m][n]); gmax=max(gmax,fmax[m][n]);
    }
    cout<<gmin<<"\n"<<gmax<<"\n"; return 0;
}
