// P1039 侦探推理 · std（枚举 罪犯×星期 → 统计确定说谎/真话/未定人数）：
// 每人若证词真值同时含真与假则矛盾；可行 ⟺ L ≤ N ≤ L+未定数。
#include <bits/stdc++.h>
using namespace std;
const vector<string> WEEK={"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"};
int M,N,P; vector<string> names; vector<pair<string,string>> stmt;
// 返回 -1=无关证词；0/1=真值
int truth(const string& speaker,const string& c,const string& culprit,const string& day){
    if(c=="I am guilty.") return speaker==culprit;
    if(c=="I am not guilty.") return speaker!=culprit;
    if(c.rfind("Today is ",0)==0 && c.size()>11 && c.back()=='.'){
        string d=c.substr(9,c.size()-10);
        if(find(WEEK.begin(),WEEK.end(),d)!=WEEK.end()) return d==day;
        return -1;
    }
    const string g=" is guilty.", ng=" is not guilty.";
    if(c.size()>g.size() && c.compare(c.size()-g.size(),g.size(),g)==0){
        string who=c.substr(0,c.size()-g.size());
        if(find(names.begin(),names.end(),who)!=names.end()) return who==culprit;
        return -1;
    }
    if(c.size()>ng.size() && c.compare(c.size()-ng.size(),ng.size(),ng)==0){
        string who=c.substr(0,c.size()-ng.size());
        if(find(names.begin(),names.end(),who)!=names.end()) return who!=culprit;
        return -1;
    }
    return -1;
}
int main(){
    if(!(cin>>M>>N>>P)) return 0;
    names.resize(M);
    for(int i=0;i<M;i++) cin>>names[i];
    string line; getline(cin,line);
    for(int i=0;i<P;i++){ getline(cin,line); size_t q=line.find(": ");
        stmt.push_back({line.substr(0,q), q==string::npos? "":line.substr(q+2)}); }
    set<string> feasible;
    for(auto&culprit:names) for(auto&day:WEEK){
        vector<int> st(M,0);   // 0 未定 / 1 全真 / 2 全假 / 3 矛盾
        bool bad=false;
        for(auto&sp:stmt){
            int t=truth(sp.first,sp.second,culprit,day);
            if(t<0) continue;
            auto it=find(names.begin(),names.end(),sp.first);
            if(it==names.end()) continue;
            int id=(int)(it-names.begin());
            int want=t?1:2;
            if(st[id]==0) st[id]=want;
            else if(st[id]!=want){ bad=true; break; }
        }
        if(bad) continue;
        int L=0,unk=0;
        for(int v:st){ if(v==2) L++; else if(v==0) unk++; }
        if(L<=N && N<=L+unk) feasible.insert(culprit);
    }
    if(feasible.empty()) cout<<"Impossible\n";
    else if(feasible.size()>1) cout<<"Cannot Determine\n";
    else cout<<*feasible.begin()<<"\n";
    return 0;
}
