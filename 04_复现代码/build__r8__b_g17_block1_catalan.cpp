
#include<bits/stdc++.h>
using namespace std;
int f[1001];
int main(){ int n; scanf("%d",&n);
 f[0]=1;
 for(int i=1;i<=n;i++) for(int j=1;j<=i;j++) f[i]+=f[j-1]*f[i-j];
 printf("%d\n",f[n]); return 0; }
