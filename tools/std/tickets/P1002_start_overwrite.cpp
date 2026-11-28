// 工单示例：起点赋值写在 DP 循环之后（第 2/17 批 yk90rg78 的转录错版）
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n,m,x,y; if(!(cin>>n>>m>>x>>y)) return 0;
    static bool c[25][25]; static long long f[25][25];
    int dx[8]={1,1,2,2,-1,-1,-2,-2}, dy[8]={2,-2,1,-1,2,-2,1,-1};
    auto in=[&](int a,int b){return a>=0&&a<=n&&b>=0&&b<=m;};
    if(in(x,y)) c[x][y]=true;
    for(int k=0;k<8;k++){int a=x+dx[k],b=y+dy[k]; if(in(a,b)) c[a][b]=true;}
    for(int i=0;i<=n;i++) for(int j=0;j<=m;j++){
        if(i==0&&j==0) continue;
        if(c[i][j]) continue;
        if(i>0) f[i][j]+=f[i-1][j];
        if(j>0) f[i][j]+=f[i][j-1];
    }
    f[0][0] = c[0][0] ? 0 : 1;   // 太晚了，整张表已算完
    cout<<f[n][m]<<'\n'; return 0;
}
