// P1031 朴素：BFS 状态图搜最少移动（N≤4、总数≤12，如实标注）。
#include <bits/stdc++.h>
using namespace std;string key(const vector<int>&v){string s;for(int x:v)s+=char(x+48);return s;}
int main(){int n;if(!(cin>>n))return 0;vector<int>a(n);int sum=0;for(int i=0;i<n;i++){cin>>a[i];sum+=a[i];}
 int avg=sum/n;vector<int>goal(n,avg);map<string,int>dist;queue<vector<int>>q;dist[key(a)]=0;q.push(a);int ans=-1;
 while(!q.empty()){vector<int>u=q.front();q.pop();int d=dist[key(u)];if(u==goal){ans=d;break;}
  for(int i=0;i<n;i++)for(int dir=-1;dir<=1;dir+=2){int j=i+dir;if(j<0||j>=n)continue;
   for(int m=1;m<=u[i];m++){vector<int>v=u;v[i]-=m;v[j]+=m;string k=key(v);if(!dist.count(k)){dist[k]=d+1;q.push(v);}}}}
 cout<<ans<<'\n';return 0;}
