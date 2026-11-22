#include <bits/stdc++.h>
using namespace std;
int a,b,n,m;
long long f[23];
bool ma[27][27];
void work(long long x,long long y){
 ma[x][y]=true; ma[x-1][y-2]=true; ma[x-2][y-1]=true; ma[x-2][y+1]=true;
 ma[x-1][y+2]=true; ma[x+1][y-2]=true; ma[x+2][y-1]=true;
 ma[x+2][y+1]=true; ma[x+1][y+2]=true;
}
int main(){
 cin>>n>>m>>a>>b; a+=2; b+=2; n+=2; m+=2; work(a,b);
 f[2]=1;
 for(int i=2;i<=n;i++) for(int j=2;j<=m;j++){
  if(i==2&&j==2)continue;
  if(!ma[i][j])f[j]+=f[j-1]; else f[j]=0;
 }
 cout<<f[m];
 return 0;
}
