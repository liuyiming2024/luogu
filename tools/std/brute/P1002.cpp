// P1002 朴素算法：不写 DP，直接递归枚举所有从 (0,0) 到 (n,m) 的路径，
// 跳过马位与其控制点，逐条计数。指数级，故对拍用例限制 n,m≤8（题面内小规模）。
#include <bits/stdc++.h>
using namespace std;
int n,m; bool c[25][25];
long long dfs(int i,int j){
    if(i>n||j>m||c[i][j]) return 0;
    if(i==n&&j==m) return 1;
    return dfs(i+1,j)+dfs(i,j+1);
}
int main(){
    int x,y; if(!(cin>>n>>m>>x>>y)) return 0;
    const int dx[8]={1,1,2,2,-1,-1,-2,-2}, dy[8]={2,-2,1,-1,2,-2,1,-1};
    auto in=[&](int a,int b){return a>=0&&a<=n&&b>=0&&b<=m;};
    if(in(x,y)) c[x][y]=true;
    for(int k=0;k<8;k++){int a=x+dx[k],b=y+dy[k]; if(in(a,b)) c[a][b]=true;}
    cout<<dfs(0,0)<<'\n'; return 0;
}
