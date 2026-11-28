// P1049 装箱问题 · std：0/1 背包一维 DP 求可装最大体积，答案 V - best。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int V,n; if(!(cin>>V>>n)) return 0;
    vector<int> dp(V+1,0);
    for(int i=0;i<n;i++){
        int w; cin>>w;
        for(int j=V;j>=w;j--) dp[j]=max(dp[j], dp[j-w]+w);
    }
    cout<<V-dp[V]<<'\n'; return 0;
}
