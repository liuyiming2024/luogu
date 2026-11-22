
#include <bits/stdc++.h>
using namespace std;
int i,j,T,M;
long long t[10001],p[10001],f[10000001];
int main(){
 scanf("%d%d",&T,&M);
 for(i=1;i<=M;i++) scanf("%lld%lld",&t[i],&p[i]);
 for(i=1;i<=M;i++) for(j=t[i];j<=T;j++) f[j]=max(f[j],f[j-t[i]]+p[i]);
 printf("%lld",f[T]);
 return 0;
}
