// P1038 神经网络 · std（Kahn 拓扑序迭代传播）：
// 输入层保持给定初始 C（不减 U）；非输入层 C = Σ W·C_前驱(仅前驱>0) − U；
// 只有 C>0 才向下游传送；输出层 = 无出边且 C>0，按编号升序。
#include <bits/stdc++.h>
using namespace std;
struct E{int v; long long w;};
int main(){
    int n,p; if(!(cin>>n>>p)) return 0;
    vector<long long> C(n+1), U(n+1), acc(n+1,0);
    vector<int> indeg(n+1,0), outdeg(n+1,0), orig_indeg(n+1,0);
    vector<vector<E>> g(n+1);
    for(int i=1;i<=n;i++) cin>>C[i]>>U[i];
    for(int q=0;q<p;q++){
        int i,j; long long w; cin>>i>>j>>w;
        g[i].push_back({j,w}); indeg[j]++; outdeg[i]++;
    }
    orig_indeg = indeg;          // 拓扑会递减 indeg，输入层判定必须用原始入度
    queue<int> q;
    for(int i=1;i<=n;i++) if(indeg[i]==0) q.push(i);
    while(!q.empty()){
        int u=q.front(); q.pop();
        if(orig_indeg[u]>0) C[u]=acc[u]-U[u];
        if(C[u]>0) for(auto&e:g[u]) acc[e.v]+=e.w*C[u];
        for(auto&e:g[u]){ if(--indeg[e.v]==0) q.push(e.v); }
    }
    bool any=false;
    for(int i=1;i<=n;i++) if(outdeg[i]==0 && C[i]>0){ cout<<i<<" "<<C[i]<<"\n"; any=true; }
    if(!any) cout<<"NULL\n";
    return 0;
}
