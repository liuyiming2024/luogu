// P1060 开心的金明 · std：0/1 背包，价值 = 价格 × 重要度。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n,m; if(!(cin>>n>>m)) return 0;
    vector<int> dp(n+1,0);
    for(int i=0;i<m;i++){
        int v,p; cin>>v>>p; int val=v*p;
        for(int j=n;j>=v;j--) dp[j]=max(dp[j], dp[j-v]+val);
    }
    cout<<dp[n]<<'\n'; return 0;
}
