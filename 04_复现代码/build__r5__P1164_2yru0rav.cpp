
#include<bits/stdc++.h>
using namespace std;
const int N=110,M=10010;
int f[N][M],n,m,a[N];
int main(){
 cin>>n>>m;
 for(int i=1;i<=n;i++) cin>>a[i];
 for(int i=1;i<=n;i++)
     for(int j=0;j<=m;j++){
         if(j==a[i]) f[i][j]=f[i-1][j]+1;
         if(j>a[i]) f[i][j]=f[i-1][j]+f[i-1][j-a[i]];
         if(j<a[i]) f[i][j]=f[i-1][j];
     }
 cout<<f[n][m];
 return 0;
}
