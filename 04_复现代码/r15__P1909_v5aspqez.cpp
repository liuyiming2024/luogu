#include<cstdio>
inline int min(int x,int y){return x<y?x:y;}
int n,ans=2147483647;
int main(){
    scanf("%d",&n);
    for(int i=1;i<=3;i++){
        int a,b;
        scanf("%d%d",&a,&b);
        ans=min(ans,b*((n+a-1)/a));
    }
    printf("%d\n",ans);
}
