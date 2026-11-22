#include <bits/stdc++.h>
using namespace std;
int ans,n,c[105],v,s;
int f(){
    int vv=v; int st[40],top=0; int q[40],head=1;
    for(int i=1;i<=n;i++) q[i]=c[i];
    while(head<=n&&vv>0){
        while(head<=n&&((rand()%9==0)||vv-q[head]<0))
            if(vv-q[head]>=0) st[top++]=q[head++];
            else head++;
        if(head<=n) vv-=q[head++];
        while(top) q[--head]=st[--top];
    }
    return vv;
}
int main(){
    scanf("%d%d",&v,&n);
    for(int i=1;i<=n;i++) scanf("%d",&c[i]);
    sort(c+1,c+n+1,greater<int>());
    ans=v;
    for(int i=1;i<=100;i++) ans=min(ans,f());
    printf("%d",ans);
    return 0;
}
