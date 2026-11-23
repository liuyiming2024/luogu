#include<cstdio>
int main(){
int k,sum=0,ans=0,t,d,i;
scanf("%d",&k);
for(i=1;;i++){
sum+=i;
ans+=i*i;
if(sum==k){ printf("%d\n",ans); return 0; }
if(sum>k){ t=i-1; break; }
}
ans=0;
for(i=1;i<=t;i++) ans+=i*i;
d=k-sum+t+1;
ans+=d*(t+1);
printf("%d\n",ans);
return 0;
}
