// P1028 朴素算法：完全按题面递归枚举合法数列（末尾追加 ≤ 末项一半的正整数），逐个计数。
#include <bits/stdc++.h>
using namespace std;
long long dfs(int last){
    long long cnt=1;                       // 只有 last 自己
    for(int x=1;x<=last/2;x++) cnt+=dfs(x);
    return cnt;
}
int main(){ int n; if(!(cin>>n)) return 0; cout<<dfs(n)<<'\n'; return 0; }
