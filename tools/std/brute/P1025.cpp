// P1025 朴素：DFS 枚举所有非降序拆分（指数级，对拍 n≤30）。
#include <bits/stdc++.h>
using namespace std;long long dfs(int rem,int parts,int minv){if(parts==0)return rem==0;long long s=0;
 for(int v=minv;v<=rem/parts;v++)s+=dfs(rem-v,parts-1,v);return s;}
int main(){int n,k;if(!(cin>>n>>k))return 0;long long ans=dfs(n,k,1);cout<<ans<<'\n';return 0;}
