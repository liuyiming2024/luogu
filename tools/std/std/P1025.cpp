// P1025 std：DP f[i][j]=f[i-1][j-1]+f[i-j][j]（非降序拆分）。
#include <bits/stdc++.h>
using namespace std;int main(){int n,k;if(!(cin>>n>>k))return 0;static long long f[205][8];f[0][0]=1;
 for(int i=1;i<=n;i++)for(int j=1;j<=k;j++)if(i>=j)f[i][j]=f[i-1][j-1]+f[i-j][j];
 cout<<f[n][k]<<'\n';return 0;}
