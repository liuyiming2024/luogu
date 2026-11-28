// P1040 加分二叉树 · std（区间 DP 迭代填表 + root 记录）：
// f[l][r]=max_k f[l][k-1]*f[k+1][r]+d[k]，空区间=1；相等时取较小 k（遍历顺序保证）。
#include <bits/stdc++.h>
using namespace std;
int n; vector<long long> d;
vector<vector<__int128>> f;
vector<vector<int>> root;
string out128(__int128 v){ if(v==0)return "0"; string s; while(v>0){s+=char('0'+v%10);v/=10;} reverse(s.begin(),s.end()); return s; }
void pre(int l,int r,vector<int>&o){
    if(l>r) return;
    int k=root[l][r]; o.push_back(k);
    pre(l,k-1,o); pre(k+1,r,o);
}
int main(){
    if(!(cin>>n)) return 0; d.assign(n+1,0);
    for(int i=1;i<=n;i++) cin>>d[i];
    f.assign(n+2, vector<__int128>(n+2,1));
    root.assign(n+2, vector<int>(n+2,0));
    for(int i=1;i<=n;i++){ f[i][i]=d[i]; root[i][i]=i; }
    for(int len=2;len<=n;len++)
        for(int l=1;l+len-1<=n;l++){
            int r=l+len-1; __int128 best=-1; int bk=l;
            for(int k=l;k<=r;k++){
                __int128 v=f[l][k-1]*f[k+1][r]+d[k];
                if(v>best){ best=v; bk=k; }
            }
            f[l][r]=best; root[l][r]=bk;
        }
    cout<<out128(f[1][n])<<"\n";
    vector<int> o; pre(1,n,o);
    for(size_t i=0;i<o.size();i++){ if(i) cout<<" "; cout<<o[i]; }
    cout<<"\n"; return 0;
}
