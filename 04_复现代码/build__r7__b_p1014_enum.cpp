
#include <bits/stdc++.h>
using namespace std;
string sol(int N){
    float n=(float)N;
    int k=int(sqrt(n*2-1.75)+0.5);
    n-=(k-1)*k/2;
    char buf[64];
    if(k%2==1) sprintf(buf,"%g/%g",(double)(k-n+1),(double)n);
    else       sprintf(buf,"%g/%g",(double)n,(double)(k-n+1));
    return string(buf);
}
string ok(int N){
    // 整数二分求最小 k 使 k(k+1)/2 >= N
    int l=1,r=5000;
    while(l<r){ int m=(l+r)/2; if((long long)m*(m+1)/2>=N) r=m; else l=m+1; }
    int k=l; int n=N-(k-1)*k/2;
    char buf[64];
    if(k%2==1) sprintf(buf,"%d/%d",k-n+1,n);
    else       sprintf(buf,"%d/%d",n,k-n+1);
    return string(buf);
}
int main(){
    long long bad=0; vector<string> ex;
    for(int N=1;N<=10000000;N++){
        string s=sol(N), o=ok(N);
        if(s!=o){ bad++; if((int)ex.size()<12){ char b[128]; sprintf(b,"N=%d -> sol=%s ok=%s",N,s.c_str(),o.c_str()); ex.push_back(b); } }
    }
    printf("B|bad=%lld\n",bad);
    for(auto &e:ex) printf("B|%s\n",e.c_str());
    return 0;
}
