// P1032 朴素：迭代加深 DFS（非 BFS 队列），visited 按已见最小深度剪枝。
#include <bits/stdc++.h>
using namespace std;string A,B;vector<pair<string,string>>rules;map<string,int>best;int limit;
int dfs(string s,int d){if(d==limit)return s==B?d:-1;if(s==B)return -1;
 for(auto&r:rules){size_t pos=0;while((pos=s.find(r.first,pos))!=string::npos){
  string ns=s.substr(0,pos)+r.second+s.substr(pos+r.first.size());
  if(ns.size()>20){pos++;continue;}
  if(best.count(ns)&&best[ns]<=d+1){pos++;continue;}best[ns]=d+1;
  int got=dfs(ns,d+1);if(got>=0)return got;pos++;}}return -1;}
int main(){if(!(cin>>A>>B))return 0;string x,y;while(cin>>x>>y)rules.push_back({x,y});int ans=-1;
 for(limit=0;limit<=10;limit++){best.clear();best[A]=0;int got=dfs(A,0);if(got>=0){ans=got;break;}}
 if(ans<0){cout<<"NO ANSWER!\n";return 0;}cout<<ans<<'\n';return 0;}
