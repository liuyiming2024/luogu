// P1038 朴素（反图 DFS 记忆化递归，非拓扑迭代）：
// 从每个节点向上游递归求 C(u)=Σ W·C(前驱)>0 项 − U，输入层直接返回初始值。
#include <bits/stdc++.h>
using namespace std;
struct E{int u; long long w;};
int n,p; vector<long long> C0,U; vector<vector<E>> rev; vector<int> indeg,outdeg;
vector<char> memo; vector<long long> val;
long long f(int u){
    if(memo[u]) return val[u];
    if(indeg[u]==0){ memo[u]=1; return val[u]=C0[u]; }
    long long s=0;
    for(auto&e:rev[u]){ long long c=f(e.u); if(c>0) s+=e.w*c; }
    memo[u]=1; return val[u]=s-U[u];
}
int main(){
    if(!(cin>>n>>p)) return 0;
    C0.assign(n+1,0); U.assign(n+1,0); rev.assign(n+1,{});
    indeg.assign(n+1,0); outdeg.assign(n+1,0);
    for(int i=1;i<=n;i++) cin>>C0[i]>>U[i];
    for(int q=0;q<p;q++){
        int i,j; long long w; cin>>i>>j>>w;
        rev[j].push_back({i,w}); indeg[j]++; outdeg[i]++;
    }
    memo.assign(n+1,0); val.assign(n+1,0);
    bool any=false;
    for(int i=1;i<=n;i++) if(outdeg[i]==0 && f(i)>0){ cout<<i<<" "<<f(i)<<"\n"; any=true; }
    if(!any) cout<<"NULL\n";
    return 0;
}
