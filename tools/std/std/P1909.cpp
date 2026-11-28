// P1909 买铅笔 · 独立正确解（std）：向上取整一次算盒数，取三种包装最小花费。
#include <bits/stdc++.h>
using namespace std;
int main(){
    long long n; if(!(cin>>n)) return 0;
    long long best = LLONG_MAX;
    for(int i=0;i<3;i++){
        long long c,p; cin>>c>>p;
        long long boxes = (n + c - 1) / c;
        best = min(best, boxes*p);
    }
    cout<<best<<'\n'; return 0;
}
