
#include<bits/stdc++.h>
using namespace std;
int main(){
 int n; long long c; scanf("%d%lld",&n,&c);
 map<long long,long long> cnt;
 for(int i=0;i<n;i++){ long long x; scanf("%lld",&x); cnt[x]++; }
 long long ans=0;
 vector<pair<long long,long long>> v(cnt.begin(),cnt.end());
 for(auto &kv:v) ans+=kv.second*cnt[kv.first+c];
 printf("%lld",ans); return 0;
}
