// P1027 std：找直角点定第 4 点；4S 点图 Dijkstra（超级源 = A 城 4 机场）。
#include <bits/stdc++.h>
using namespace std;struct Pt{double x,y;};double dis(Pt a,Pt b){return hypot(a.x-b.x,a.y-b.y);}
int main(){int n;if(!(cin>>n))return 0;cout<<fixed<<setprecision(1);
 while(n--){int S,A,B;double t;cin>>S>>t>>A>>B;vector<vector<Pt>>c(S+1,vector<Pt>(4));vector<double>T(S+1);
  for(int i=1;i<=S;i++){Pt p[3];for(int j=0;j<3;j++)cin>>p[j].x>>p[j].y;cin>>T[i];Pt four=p[0];
   for(int k=0;k<3;k++){Pt o=p[k],a=p[(k+1)%3],b=p[(k+2)%3];double dot=(a.x-o.x)*(b.x-o.x)+(a.y-o.y)*(b.y-o.y);
    if(fabs(dot)<1e-9){four={a.x+b.x-o.x,a.y+b.y-o.y};break;}}
   c[i][0]=p[0];c[i][1]=p[1];c[i][2]=p[2];c[i][3]=four;}
  int V=4*S;const double INF=1e100;vector<double>d(V+1,INF);
  priority_queue<pair<double,int>,vector<pair<double,int>>,greater<pair<double,int>>>pq;
  for(int a=0;a<4;a++){int u=4*(A-1)+a+1;d[u]=0;pq.push({0,u});}
  while(!pq.empty()){auto[du,u]=pq.top();pq.pop();if(du>d[u]+1e-10)continue;int ci=(u-1)/4+1;
   for(int v=1;v<=V;v++){if(u==v)continue;int cj=(v-1)/4+1;double rate=(ci==cj?T[ci]:t);
    double nd=du+dis(c[ci][(u-1)%4],c[cj][(v-1)%4])*rate;if(nd<d[v]-1e-10){d[v]=nd;pq.push({nd,v});}}}
  double ans=INF;for(int a=0;a<4;a++)ans=min(ans,d[4*(B-1)+a+1]);cout<<ans<<"\n";}
 return 0;}
