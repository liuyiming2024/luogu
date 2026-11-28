// P1048 采药 · std：0/1 背包一维滚动 DP。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int T,M; if(!(cin>>T>>M)) return 0;
    vector<int> dp(T+1,0);
    for(int i=0;i<M;i++){
        int t,v; cin>>t>>v;
        for(int j=T;j>=t;j--) dp[j]=max(dp[j], dp[j-t]+v);
    }
    cout<<dp[T]<<'\n'; return 0;
}
