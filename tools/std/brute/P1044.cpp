// P1044 朴素算法：不写 Catalan 公式，直接递归模拟 push/pop 状态 (已入栈个数, 栈内个数)，
// 枚举所有合法操作序列并计数。指数级，故对拍用例限制 n≤10（题面内小规模）。
#include <bits/stdc++.h>
using namespace std;
int n;
long long f(int pushed,int st){
    if(pushed==n && st==0) return 1;
    long long r=0;
    if(pushed<n) r += f(pushed+1, st+1);   // push
    if(st>0)     r += f(pushed,   st-1);   // pop
    return r;
}
int main(){ if(!(cin>>n)) return 0; cout<<f(0,0)<<'\n'; return 0; }
