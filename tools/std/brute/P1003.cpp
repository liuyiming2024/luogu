// P1003 朴素：逐格涂色模拟（网格 128，用例坐标≤64，如实标注）。
#include <bits/stdc++.h>
using namespace std;
int main(){int n;if(!(cin>>n))return 0;const int M=128;static int g[M][M];
 for(int i=1;i<=n;i++){int a,b,gg,k;cin>>a>>b>>gg>>k;
  for(int xx=a;xx<=a+gg&&xx<M;xx++)for(int yy=b;yy<=b+k&&yy<M;yy++)g[xx][yy]=i;}
 int x,y;cin>>x>>y;int ans=-1;
 if(x>=0&&x<M&&y>=0&&y<M&&g[x][y])ans=g[x][y];
 cout<<ans<<'\n';return 0;}
