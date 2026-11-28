// P1002 过河卒 · 本地独立正确解（std）
// 起点先判马控制，再用滚动数组 DP；不用 int 溢出类型。
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n,m,x,y; if(!(cin>>n>>m>>x>>y)) return 0;
    static bool ctrl[25][25];
    const int dx[8]={1,1,2,2,-1,-1,-2,-2}, dy[8]={2,-2,1,-1,2,-2,1,-1};
    auto inside=[&](int a,int b){return a>=0&&a<=n&&b>=0&&b<=m;};
    if(inside(x,y)) ctrl[x][y]=true;
    for(int k=0;k<8;k++){int a=x+dx[k],b=y+dy[k]; if(inside(a,b)) ctrl[a][b]=true;}
    static long long dp[25];
    dp[0]= ctrl[0][0] ? 0 : 1;
    for(int i=0;i<=n;i++){
        for(int j=0;j<=m;j++){
            if(i==0&&j==0) continue;
            long long v=0;
            if(!ctrl[i][j]){
                if(i>0) v+=dp[j];          // 上一行同列（滚动前仍是旧值）
                if(j>0) v+=dp[j-1];        // 本行左列（已更新）
            }
            dp[j]=v;
        }
    }
    cout<<dp[m]<<'\n';
    return 0;
}
