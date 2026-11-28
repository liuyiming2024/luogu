// P1059 明明的随机数 · 独立正确解（std）：排序 + unique，输出两行。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; if(!(cin>>n)) return 0;
    vector<int> a(n);
    for(int i=0;i<n;i++) cin>>a[i];
    sort(a.begin(),a.end());
    a.erase(unique(a.begin(),a.end()),a.end());
    cout<<a.size()<<'\n';
    for(size_t i=0;i<a.size();i++){ if(i) cout<<' '; cout<<a[i]; }
    cout<<'\n'; return 0;
}
