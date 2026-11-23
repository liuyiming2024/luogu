#include<bits/stdc++.h>
using namespace std;
int main(){
int n,a[40][40],x,y;
cin>>n;
memset(a,0,sizeof(a));//初始化x,y
a[x][y]=1;
for(int i=2;i<=n*n;i++)
{
if(x==1&&y!=n) { x=n; y++; }
else if(y==n&&x!=1) { y=1; x--; }
else if(x==1&&y==n) { x++; y=y; }
else if(x!=1&&y!=n) { if(a[x-1][y+1]==0) { x--; y++; } else { x++; y=y; } }
a[x][y]=i;
}
for(int i=1;i<=n;i++) { for(int j=1;j<=n;j++) cout<<a[i][j]<<" "; cout<<endl; }
return 0;
}
