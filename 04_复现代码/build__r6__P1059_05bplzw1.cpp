
#include<bits/stdc++.h>
using namespace std;
set<int> s;
int main(){
 int n; cin>>n;
 while(n--){ int x; cin>>x; s.insert(x); }
 cout<<s.size()<<endl;
 for(auto it=s.begin();it!=s.end();it++) cout<<*it<<" ";
 return 0;
}
