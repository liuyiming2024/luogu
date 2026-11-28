// P1047 校门外的树 · std：差分标记每个整数点，数未移走的树。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int l,m; if(!(cin>>l>>m)) return 0;
    vector<int> diff(l+3,0);
    for(int q=0;q<m;q++){ int u,v; cin>>u>>v; diff[u]++; diff[v+1]--; }
    int cur=0, ans=0;
    for(int i=0;i<=l;i++){ cur+=diff[i]; if(cur==0) ans++; }
    cout<<ans<<'\n'; return 0;
}
