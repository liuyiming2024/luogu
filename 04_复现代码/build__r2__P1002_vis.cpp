
#include <bits/stdc++.h>
using namespace std;
const int maxn=210;
long long dp[maxn][maxn];
int n,m,a,b;
bool vis[maxn][maxn];
const int x[]={0,-2,-1,1,2,2,1,-1,-2};
const int y[]={0,1,2,2,1,-1,-2,-2,-1};
int main(){
 memset(vis,true,sizeof(vis));
 cin>>n>>m>>a>>b;
 n+=2,m+=2,a+=2,b+=2;
 for(int i=1;i<=8;i++){ vis[a+x[i]][b+y[i]]=false; }
 vis[a][b]=false;
 dp[2][1]=1;
 for(int i=2;i<=n;i++){
  for(int j=2;j<=m;j++){
   if(vis[i][j]){ dp[i][j]=dp[i-1][j]+dp[i][j-1]; }
  }
 }
 cout<<dp[n][m]<<endl;
 return 0;
}
