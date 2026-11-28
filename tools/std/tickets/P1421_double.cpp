// 工单示例：第 7 批甲类题解的复现（double 反复减 1.9）
#include <bits/stdc++.h>
using namespace std;
int main(){
    int a,b; if(!(cin>>a>>b)) return 0;
    double m = a + b/10.0;
    int s=0;
    while(m>=1.9){ m=m-1.9; s++; }
    cout<<s<<'\n'; return 0;
}
