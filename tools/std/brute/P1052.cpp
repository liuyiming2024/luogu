// P1052 朴素（**不做任何距离压缩**，直接在真实坐标 0..L 上做原始 DP）：
// 与 std 的压缩版是完全不同的实现；O(L·(T−S+1))，对拍限 L≤300（如实标注）。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int L,S,T,M; if(!(cin>>L)) return 0;
    cin>>S>>T>>M;
    vector<int> isStone(L+T+1,0);
    for(int i=0;i<M;i++){ int x; cin>>x; if(x<=L) isStone[x]=1; }
    const int INF=1e9;
    vector<int> dp(L+T+1,INF); dp[0]=0; int ans=INF;
    for(int i=0;i<=L;i++){
        if(dp[i]>=INF) continue;
        for(int j=S;j<=T;j++){
            int nx=i+j;
            if(nx>=L){ ans=min(ans,dp[i]); continue; }
            dp[nx]=min(dp[nx], dp[i]+isStone[nx]);
        }
    }
    ans=min(ans,dp[L]);
    cout<<ans<<'\n'; return 0;
}
