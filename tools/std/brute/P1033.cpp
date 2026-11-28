// P1033 朴素（位移域数值扫描，完全不同实现）：
// 不解析 t 区间，改以「车走过的位移 s」为变量，把 [V*t1, V*t2] 均匀采样，
// 对每个 s 直接检查车覆盖的整数球编号并打标记，最后数标记。
// 网格 20001 点含两端；对拍用例保证覆盖窗口远宽于步长（如实标注）。
#include <bits/stdc++.h>
using namespace std;
int main(){
    double H,S1,V,L,K; int n;
    if(!(cin>>H>>S1>>V>>L>>K>>n)) return 0;
    double t1=sqrt(2.0*(H-K)/10.0), t2=sqrt(2.0*H/10.0);
    double a=V*t1, b=V*t2;
    vector<char> hit(n,0);
    const int N=20000;
    for(int q=0;q<=N;q++){
        double s=a+(b-a)*q/N;
        double tail=S1-s, head=S1+L-s;
        for(int i=0;i<n;i++)
            if(i>=tail-1e-4 && i<=head+1e-4) hit[i]=1;
    }
    int ans=0; for(int i=0;i<n;i++) ans+=hit[i];
    cout<<ans<<'\n'; return 0;
}
