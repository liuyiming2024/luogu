// P1032 std：BFS，规则在所有出现位置替换，深度≤10，串长≤20。
#include <bits/stdc++.h>
using namespace std;int main(){string A,B;if(!(cin>>A>>B))return 0;vector<pair<string,string>>rules;string x,y;
 while(cin>>x>>y)rules.push_back({x,y});if(A==B){cout<<0<<'\n';return 0;}
 map<string,int>seen;queue<pair<string,int>>q;seen[A]=0;q.push({A,0});
 while(!q.empty()){auto[s,d]=q.front();q.pop();if(d>=10)continue;
  for(auto&r:rules){size_t pos=0;while((pos=s.find(r.first,pos))!=string::npos){
   string ns=s.substr(0,pos)+r.second+s.substr(pos+r.first.size());
   if(ns.size()<=20){if(ns==B){int ans=d+1;cout<<ans<<'\n';return 0;}
    if(!seen.count(ns)){seen[ns]=d+1;q.push({ns,d+1});}}pos++;}}}
 cout<<"NO ANSWER!\n";return 0;}
