// P1053 篝火晚会 · std（构造目标环 + O(n) 统计对齐不动点）：
// 合法 ⟺ 每人的两个期望邻居恰为目标环上其左右邻居，且环覆盖全部 n 人。
// 代价 = n − max(对齐后的不动点数)；对齐 = 目标环正/反 × 任意旋转，
// 用 diff[i]=(t[i]−1−i) mod n 的频次一次统计，避免 O(n²) 枚举。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; if(!(cin>>n)) return 0;
    vector<array<int,2>> w(n+1);
    for(int i=1;i<=n;i++) cin>>w[i][0]>>w[i][1];
    auto ok=[&](int p,int a,int b){
        return (w[p][0]==a&&w[p][1]==b)||(w[p][0]==b&&w[p][1]==a);
    };
    // 构造目标环（从 1 出发，任选第一个期望邻居作为后继）
    vector<int> t; t.reserve(n);
    vector<char> used(n+1,0);
    t.push_back(1); used[1]=1;
    int prev=0, cur=1;
    bool bad=false;
    for(int step=1;step<n;step++){
        int nxt=0;
        for(int q=0;q<2;q++){
            int c=w[cur][q];
            if(c!=prev && !used[c]){ nxt=c; break; }
        }
        if(!nxt){ bad=true; break; }
        t.push_back(nxt); used[nxt]=1; prev=cur; cur=nxt;
    }
    if(!bad){
        if(!ok(cur,prev,t[0])) bad=true;
        for(int i=0;i<n&&!bad;i++){
            int p=t[i], l=t[(i-1+n)%n], r=t[(i+1)%n];
            if(!ok(p,l,r)) bad=true;
        }
    }
    if(bad){ cout<<-1<<'\n'; return 0; }
    int best=0;
    for(int dir=0;dir<2;dir++){
        vector<int> cnt(n,0);
        for(int i=0;i<n;i++){
            int val = dir==0 ? t[i] : t[(n-i)%n];
            int d=((val-1-i)%n+n)%n;
            cnt[d]++; best=max(best,cnt[d]);
        }
    }
    cout<<n-best<<'\n'; return 0;
}
