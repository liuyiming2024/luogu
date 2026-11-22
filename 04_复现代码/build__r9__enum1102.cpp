#include <bits/stdc++.h>
using namespace std;
// 题解逻辑（逐字核心），封装成函数
long long sol(vector<long long> v,int n,int c){
    static long long shu[300000];
    for(int i=0;i<300000;i++) shu[i]=0;
    for(int i=0;i<n;i++) shu[i]=v[i];
    sort(shu,shu+n,[](const long long&a,const long long&b){return a>b;});
    int t=0,w=1,tj,wj,st,sw; long long sum=0;
    while(w<n){
        if(shu[t]-shu[w]>c)t++;
        if(shu[t]-shu[w]<c)w++;
        if(shu[t]-shu[w]==c){
            tj=wj=0; st=t,sw=w;
            for(int i=t;shu[i]==shu[st];i++){ tj++; t++; if(i>299990) return -999; }
            if(c==0)wj=1;
            else for(int i=w;shu[i]==shu[sw];i++){ wj++; w++; if(i>299990) return -999; }
            sum+=(long long)tj*(long long)wj;
        }
    }
    return sum;
}
long long ok(vector<long long> v,int c){
    map<long long,long long> cnt;
    for(auto x:v)cnt[x]++;
    long long a=0;
    vector<pair<long long,long long>> vv(cnt.begin(),cnt.end());
    for(auto &kv:vv) a+=kv.second*cnt[kv.first+c];
    return a;
}
int main(){
    int clean=0,crash=0,total=0;
    vector<string> exClean,exCrash;
    for(int n=1;n<=5;n++) for(int c=0;c<=3;c++){
        int V=4; vector<long long> v(n);
        long long lim=1; for(int i=0;i<n;i++)lim*=V;
        for(long long mask=0;mask<lim;mask++){
            long long m=mask;
            for(int i=0;i<n;i++){v[i]=m%V+1;m/=V;}
            total++;
            long long s=sol(v,n,c), e=ok(v,c);
            if(s==-999){ crash++; if((int)exCrash.size()<4){char b[256];string ss;for(auto x:v)ss+=to_string(x)+" ";sprintf(b,"n=%d c=%d / %s exp=%lld act=越界",n,c,ss.c_str(),e);exCrash.push_back(b);} }
            else if(s!=e){ clean++; if((int)exClean.size()<6){char b[256];string ss;for(auto x:v)ss+=to_string(x)+" ";sprintf(b,"n=%d c=%d / %s exp=%lld act=%lld",n,c,ss.c_str(),e,s);exClean.push_back(b);} }
        }
    }
    printf("total=%d clean_wa=%d crash=%d\n",total,clean,crash);
    for(auto&s:exClean)printf("CLEAN|%s\n",s.c_str());
    for(auto&s:exCrash)printf("CRASH|%s\n",s.c_str());
    return 0;
}
