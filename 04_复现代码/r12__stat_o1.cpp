#include<cstdio>
int main(){int n,s=0,x; scanf("%d",&n); for(int i=1;i<=n;i++){scanf("%d",&x); s^=x;} printf("%d",s); return 0;}
