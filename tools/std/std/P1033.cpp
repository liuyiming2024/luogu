// P1033 自由落体 · std（时间域解析）：
// t1=sqrt(2(H-K)/g) 落到车顶，t2=sqrt(2H/g) 落地；
// t 时刻车占 [S1-Vt, S1+L-Vt]，球 i 被接住 ⟺
// [max(t1,(S1-i)/V), min(t2,(S1+L-i)/V)] 非空（含 1e-4 容差，车尾算车内）。
#include <bits/stdc++.h>
using namespace std;
int main(){
    double H,S1,V,L,K; int n;
    if(!(cin>>H>>S1>>V>>L>>K>>n)) return 0;
    double t1=sqrt(2.0*(H-K)/10.0), t2=sqrt(2.0*H/10.0);
    int ans=0;
    for(int i=0;i<n;i++){
        double lo=max(t1,(S1-i)/V), hi=min(t2,(S1+L-i)/V);
        if(hi-lo >= -1e-4) ans++;
    }
    cout<<ans<<'\n'; return 0;
}
