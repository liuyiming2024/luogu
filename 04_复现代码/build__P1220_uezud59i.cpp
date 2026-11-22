
#include<bits/stdc++.h>
using namespace std;
long long n,m,minn,s;
long long a[100001],b[100001];
void dfs(int i,int j,int k,int v,int x)
{
 if (v>minn) return;
 if (i==1 && j==n) { if (v<minn) minn=v; return; }
 if (k==0) { if (i>1) dfs(i-1,j,0,v+x*abs(a[i-1]-a[i]),x-b[i-1]); if (j<n) dfs(i,j+1,1,v+x*abs(a[i]-a[j+1]),x-b[j+1]); }
 if (k==1) { if (j<n) dfs(i,j+1,1,v+x*abs(a[j]-a[j+1]),x-b[j+1]); if (i>1) dfs(i-1,j,0,v+x*abs(a[j]-a[i-1]),x-b[i-1]); }
}
int main(){
 cin>>n>>m;
 minn=1000000000;
 for (int i=1; i<=n; ++i) { cin>>a[i]>>b[i]; s+=b[i]; }
 s-=b[m];
 dfs(m,m,0,0,s);
 cout<<minn;
 return 0;
}
