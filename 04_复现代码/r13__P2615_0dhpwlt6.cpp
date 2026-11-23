#include<bits/stdc++.h>
using namespace std;
int n,a[45][45],x,y,xx,yy;
int main(){
cin>>n;
memset(a,0,sizeof(a));
x=1; y=n/2+1;
a[x][y]=1;
for(int k=2;k<=n*n;k++){
if(x==1&&y!=n) xx=n,yy=y+1;
else if(y==n&&x!=1) yy=1,xx=x-1;
else if(x==1&&y==n) xx=x+1,yy=y;
else if(x!=1&&y!=n){ if(!a[x-1][y+1]) xx=x-1,yy=y+1; else xx=x+1,yy=y; }
x=xx; y=yy; a[x][y]=k;
}
for(int i=1;i<=n;i++){ for(int j=1;j<=n;j++) cout<<a[i][j]<<" "; cout<<endl; }
return 0;
}
