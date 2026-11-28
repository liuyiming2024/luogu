// P1027 朴素：Floyd-Warshall + 枚举平行四边形候选定第 4 点（S≤4）。
#include <bits/stdc++.h>
using namespace std;struct Pt{double x,y;};double dis(Pt a,Pt b){return hypot(a.x-b.x,a.y-b.y);}
Pt fourth(Pt p[3]){Pt cand[3]={{p[0].x+p[1].x-p[2].x,p[0].y+p[1].y-p[2].y},{p[0].x+p[2].x-p[1].x,p[0].y+p[2].y-p[1].y},{p[1].x+p[2].x-p[0].x,p[1].y+p[2].y-p[0].y}};
 for(Pt q:cand){Pt all[4]={p[0],p[1],p[2],q};double mx=-1;
  for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)mx=max(mx,dis(all[i],all[j]));int cmax=0;
  for(int i=0;i<4;i++)for(int j=i+1;j<4;j++)if(fabs(dis(all[i],all[j])-mx)<1e-6)cmax++;
  if(cmax==2)return q;}return cand[0];}
int main(){int n;if(!(cin>>n))return 0;
 while(n--){int S,A,B;double t;cin>>S>>t>>A>>B;vector<vector<Pt>>c(S+1,vector<Pt>(4));vector<double>T(S+1);
  for(int i=1;i<=S;i++){Pt p[3];for(int j=0;j<3;j++)cin>>p[j].x>>p[j].y;cin>>T[i];
   c[i][0]=p[0];c[i][1]=p[1];c[i][2]=p[2];c[i][3]=fourth(p);}
  int V=4*S;vector<vector<double>>d(V+1,vector<double>(V+1,1e100));
  for(int u=1;u<=V;u++){d[u][u]=0;int ci=(u-1)/4+1;
   for(int v=1;v<=V;v++){if(u==v)continue;int cj=(v-1)/4+1;double rate=(ci==cj?T[ci]:t);
    d[u][v]=dis(c[ci][(u-1)%4],c[cj][(v-1)%4])*rate;}}
  for(int k=1;k<=V;k++)for(int i=1;i<=V;i++)for(int j=1;j<=V;j++)d[i][j]=min(d[i][j],d[i][k]+d[k][j]);
  double ans=1e100;for(int a=0;a<4;a++)for(int b=0;b<4;b++)ans=min(ans,d[4*(A-1)+a+1][4*(B-1)+b+1]);printf("%.1f\n",ans);}
 return 0;}
