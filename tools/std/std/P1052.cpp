// P1052 过河 · std（石子坐标距离压缩 + DP）：
// 相邻石子间距 d > S*T 时压到 S*T + (d mod S)，保持 mod S 余数类即可达性等价；
// 压缩后 DP 长度约 M*S*T+T，可处理 L≤1e9。dp[i]=到达 i 的最少踩石子数。
#include <bits/stdc++.h>
using namespace std;
int main(){
    long long L; int S,T,M;
    if(!(cin>>L)) return 0;
    cin>>S>>T>>M;
    vector<long long> st(M);
    for(int i=0;i<M;i++) cin>>st[i];
    sort(st.begin(),st.end());
    const long long CAP=1LL*S*T;
    vector<long long> c(M);
    long long prev=0, acc=0;
    for(int i=0;i<M;i++){
        long long d=st[i]-prev;
        if(d>CAP) d=CAP+(d%S);
        acc+=d; c[i]=acc; prev=st[i];
    }
    long long d=L-prev;
    if(d>CAP) d=CAP+(d%S);
    long long CL=acc+d;                       // 压缩后的终点坐标
    const int INF=1e9;
    vector<int> dp(CL+T+1, INF), isStone(CL+T+1,0);
    for(int i=0;i<M;i++) if(c[i]<=CL) isStone[(int)c[i]]=1;
    dp[0]=0; int ans=INF;
    for(long long i=0;i<=CL;i++){
        if(dp[i]>=INF) continue;
        for(int j=S;j<=T;j++){
            long long nx=i+j;
            if(nx>=CL){ ans=min(ans,dp[i]); continue; }
            dp[nx]=min(dp[nx], dp[i]+isStone[nx]);
        }
    }
    ans=min(ans, dp[CL]);
    cout<<ans<<'\n'; return 0;
}
