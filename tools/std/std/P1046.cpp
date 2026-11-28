// P1046 陶陶摘苹果 · std：一遍线性扫描计数（手高 + 板凳 30）。
#include <bits/stdc++.h>
using namespace std;
int main(){
    vector<int> h(10); int reach;
    for(int i=0;i<10;i++) if(!(cin>>h[i])) return 0;
    if(!(cin>>reach)) return 0;
    int ans=0; for(int x:h) if(x<=reach+30) ans++;
    cout<<ans<<'\n'; return 0;
}
