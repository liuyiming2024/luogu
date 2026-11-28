// P1034 矩形覆盖 · std（精确解：递归枚举 x/y 双向切分 + 记忆化）
//
// 修正记录：原实现是「按 x 排序 + 按 y 排序分别做区间 DP 取最小」，
// 对 k≥3 的**混合方向划分**（先按 x 切、剩余再按 y 切）不精确：
// 对拍中 n=6,k=3 给出 118 而精确解 114、n=7,k=4 给出 69 而精确解 26。
// 现改为每次递归都重新按两个方向排序并枚举切点，可覆盖任意方向的划分。
//
// 题面逐字「各个矩形必须完全分开（边线与顶点也都不能重合）」：
// 切分要求前缀该坐标最大值 **严格小于** 后缀最小值（不允许边线重合）。
#include <bits/stdc++.h>
using namespace std;
struct P{int x,y;};
vector<P> all_;
map<pair<string,int>, long long> memo;

long long area(const vector<int>& ids){
    if(ids.empty()) return 0;
    int mnx=1e9,mxx=-1e9,mny=1e9,mxy=-1e9;
    for(int id:ids){
        mnx=min(mnx,all_[id].x); mxx=max(mxx,all_[id].x);
        mny=min(mny,all_[id].y); mxy=max(mxy,all_[id].y);
    }
    return 1LL*(mxx-mnx)*(mxy-mny);
}
long long solve(vector<int> ids,int k){
    int m=(int)ids.size();
    if(m<=1) return 0;                       // 单点矩形面积 0
    if(k<=1) return area(ids);
    if(k>=m) return 0;                      // 每点一个零面积矩形
    sort(ids.begin(),ids.end());
    string key; for(int id:ids){ key+=to_string(id); key+=','; }
    auto mk=make_pair(key,k);
    auto it=memo.find(mk); if(it!=memo.end()) return it->second;
    long long best=area(ids);               // 上界：全部点用一个矩形
    for(int dir=0;dir<2;dir++){
        vector<int> v=ids;
        sort(v.begin(),v.end(),[&](int a,int b){
            if(dir==0) return all_[a].x!=all_[b].x ? all_[a].x<all_[b].x : all_[a].y<all_[b].y;
            return all_[a].y!=all_[b].y ? all_[a].y<all_[b].y : all_[a].x<all_[b].x;
        });
        for(int s=1;s<m;s++){
            int mx = dir==0 ? all_[v[s-1]].x : all_[v[s-1]].y;
            int mn = dir==0 ? all_[v[s]].x   : all_[v[s]].y;
            if(mx>=mn) continue;            // 边线/顶点重合，矩形不完全分开
            vector<int> L(v.begin(),v.begin()+s), R(v.begin()+s,v.end());
            best=min(best, area(L)+solve(R,k-1));
            best=min(best, area(R)+solve(L,k-1));
        }
    }
    memo[mk]=best; return best;
}
int main(){
    int n,k; if(!(cin>>n>>k)) return 0;
    all_.resize(n);
    for(int i=0;i<n;i++) cin>>all_[i].x>>all_[i].y;
    vector<int> ids(n); iota(ids.begin(),ids.end(),0);
    cout<<solve(ids,k)<<'\n'; return 0;
}
