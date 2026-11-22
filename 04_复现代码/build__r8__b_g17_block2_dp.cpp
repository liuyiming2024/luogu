
#include<bits/stdc++.h>
using namespace std;
const int N = 100;
int dp[N][N],n;
int main(){
 dp[1][1]=1; scanf("%d",&n);
 for (int i=2;i<=n*2;i++)
  for (int j=0;j<=min(n,i);j++){
   if (j==0) dp[i][j]=dp[i-1][1];
   else { if (j==min(n,i)) dp[i][j]=dp[i-1][i-1]; else dp[i][j]=dp[i-1][j-1]+dp[i-1][j+1]; }
  }
 printf("%d\n",dp[2*n][0]);
 return 0;
}
