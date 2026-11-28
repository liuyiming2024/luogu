// P1036 选数 · std：DFS 组合枚举 + 试除判素数。
#include <bits/stdc++.h>
using namespace std;
int n,k; vector<long long> x; long long ans=0;
bool prime(long long v){
    if(v<2) return false;
    for(long long d=2;d*d<=v;d++) if(v%d==0) return false;
    return true;
}
void dfs(int i,int left,long long sum){
    if(left==0){ if(prime(sum)) ans++; return; }
    if(i>=n) return;
    dfs(i+1,left-1,sum+x[i]);
    dfs(i+1,left,sum);
}
int main(){ if(!(cin>>n>>k)) return 0; x.resize(n);
 for(int i=0;i<n;i++) cin>>x[i];
 dfs(0,k,0); cout<<ans<<'\n'; return 0; }
