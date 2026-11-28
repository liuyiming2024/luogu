// P1064 金明的预算方案 · std（主件分组背包）：
// 每个主件与其 ≤2 个附件组成 4 种购买组合（只主 / 主+附1 / 主+附2 / 主+双附），
// 对每组做 0/1 选择；价值 = Σ 价格×重要度。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n,m; if(!(cin>>n>>m)) return 0;
    vector<int> v(m+1), w(m+1), q(m+1);
    vector<vector<int>> att(m+1);
    for(int i=1;i<=m;i++){
        cin>>v[i]>>w[i]>>q[i];
        if(q[i]>0) att[q[i]].push_back(i);
    }
    vector<int> dp(n+1,0);
    for(int i=1;i<=m;i++){
        if(q[i]!=0) continue;                    // 只处理主件
        vector<pair<int,int>> combos;
        combos.push_back({v[i], v[i]*w[i]});
        for(size_t a=0;a<att[i].size();a++)
            combos.push_back({v[i]+v[att[i][a]], v[i]*w[i]+v[att[i][a]]*w[att[i][a]]});
        if(att[i].size()==2)
            combos.push_back({v[i]+v[att[i][0]]+v[att[i][1]],
                              v[i]*w[i]+v[att[i][0]]*w[att[i][0]]+v[att[i][1]]*w[att[i][1]]});
        for(int j=n;j>=0;j--){
            for(auto&c:combos) if(j>=c.first) dp[j]=max(dp[j], dp[j-c.first]+c.second);
        }
    }
    cout<<dp[n]<<'\n'; return 0;
}
