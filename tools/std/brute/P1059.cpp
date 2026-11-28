// P1059 朴素算法：不用 sort/unique，O(N²) 逐个查重 + 冒泡排序，输出同样两行。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; if(!(cin>>n)) return 0;
    vector<int> a(n), u;
    for(int i=0;i<n;i++) cin>>a[i];
    for(int i=0;i<n;i++){
        bool seen=false;
        for(size_t j=0;j<u.size();j++) if(u[j]==a[i]){ seen=true; break; }
        if(!seen) u.push_back(a[i]);
    }
    for(size_t i=0;i<u.size();i++)
        for(size_t j=i+1;j<u.size();j++)
            if(u[j]<u[i]) swap(u[i],u[j]);
    cout<<u.size()<<'\n';
    for(size_t i=0;i<u.size();i++){ if(i) cout<<' '; cout<<u[i]; }
    cout<<'\n'; return 0;
}
