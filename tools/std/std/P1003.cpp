// P1003 铺地毯 · std：倒序扫，首个覆盖 (x,y) 的即最上层（边界算覆盖）。
#include <bits/stdc++.h>
using namespace std;
int main(){int n;if(!(cin>>n))return 0;vector<array<int,4>> c(n+1);
 for(int i=1;i<=n;i++)cin>>c[i][0]>>c[i][1]>>c[i][2]>>c[i][3];
 int x,y;cin>>x>>y;int ans=-1;
 for(int i=n;i>=1;i--){int a=c[i][0],b=c[i][1],g=c[i][2],k=c[i][3];
  if(x>=a&&x<=a+g&&y>=b&&y<=b+k){ans=i;break;}}
 cout<<ans<<'\n';return 0;}
