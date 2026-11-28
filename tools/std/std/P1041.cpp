// P1041 传染病控制 · std（按周期分层递归枚举「本周期切断哪条边」）：
// 模型：每周期从当前感染层到未感染儿子的所有边中切断一条，其余边感染一代；
// 无边可传时结束，取最小感染总数。疑似错题，对拍只在 n≤9 小树上做（如实标注）。
#include <bits/stdc++.h>
using namespace std;
int n,p; vector<vector<int>> ch; vector<int> par;
int dfs(const vector<int>& frontier, vector<char>& inf){
    vector<pair<int,int>> edges;
    for(int u:frontier) for(int v:ch[u]) if(!inf[v]) edges.push_back({u,v});
    if(edges.empty()){
        int c=0; for(int i=1;i<=n;i++) c+=inf[i]; return c;
    }
    int best=1e9;
    for(size_t cut=0;cut<edges.size();cut++){
        vector<char> inf2=inf; vector<int> nf;
        for(size_t j=0;j<edges.size();j++){
            if(j==cut) continue;
            int v=edges[j].second;
            if(!inf2[v]){ inf2[v]=1; nf.push_back(v); }
        }
        best=min(best, dfs(nf, inf2));
    }
    return best;
}
int main(){
    if(!(cin>>n>>p)) return 0;
    ch.assign(n+1,{}); par.assign(n+1,0);
    vector<vector<int>> adj(n+1);
    for(int q=0;q<p;q++){ int i,j; cin>>i>>j; adj[i].push_back(j); adj[j].push_back(i); }
    queue<int> qu; qu.push(1); par[1]=-1;
    while(!qu.empty()){
        int u=qu.front(); qu.pop();
        for(int v:adj[u]) if(v!=par[u]){ par[v]=u; ch[u].push_back(v); qu.push(v); }
    }
    vector<char> inf(n+1,0); inf[1]=1;
    cout<<dfs(vector<int>{1}, inf)<<'\n'; return 0;
}
