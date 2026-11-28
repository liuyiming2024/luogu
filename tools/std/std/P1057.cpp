// P1057 传球游戏 · std（环形 DP）：dp[t][i] = 传 t 次后球在 i 的方法数，答案 dp[m][0]。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n,m; if(!(cin>>n>>m)) return 0;
    vector<vector<long long>> dp(m+1, vector<long long>(n,0));
    dp[0][0]=1;
    for(int t=1;t<=m;t++)
        for(int i=0;i<n;i++)
            dp[t][i]=dp[t-1][(i-1+n)%n]+dp[t-1][(i+1)%n];
    cout<<dp[m][0]<<'\n'; return 0;
}
