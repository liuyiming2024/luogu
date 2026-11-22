
#include <bits/stdc++.h>
using namespace std;
int n,k;
int l,r,m;
long long t,tot,a[10000001];
inline bool judge(int x)
{
    for(int i=1;i<=n;i++)
	{
        if((t+a[i])<=x)
		t+=a[i];
        else{
        	t=a[i];
			tot++;
		}
    }
    return tot>=k;
}
int main()
{
    scanf("%d%d",&n,&k);
    for(int i=1;i<=n;i++)
	{
        scanf("%d",&a[i]);
        r+=a[i];
        if(a[i]>l)
        l=a[i];
	}
    while(l<=r)
	{
        m=l+(r-l)/2;
        t=0,tot=0;
        if(judge(m))l=m+1;
        else r=m-1;
    }
    printf("%d",l);
    return 0;
}
