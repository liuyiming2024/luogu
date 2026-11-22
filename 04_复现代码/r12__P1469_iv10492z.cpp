#include<bits/stdc++.h>
using namespace std;
int n;
vector<int>p;
int main()
{
scanf("%d",&n);
p.resize(n+1);
for(int i=1;i<=n;i++)
scanf("%d",&p[i]);
for(int i=2;i<=n;i++)
p[i]=p[i]^p[i-1];
printf("%d",p[n]);
return 0;
}
