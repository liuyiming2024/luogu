// P1044 栈 · 独立正确解（std）：Catalan 数递推 h(n)=h(n-1)*(4n-2)/(n+1)。
// n≤18 → h(18)=477638700，long long 安全。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n; if(!(cin>>n)) return 0;
    long long h=1;
    for(int i=1;i<=n;i++) h = h*(4LL*i-2)/(i+1);
    cout<<h<<'\n'; return 0;
}
