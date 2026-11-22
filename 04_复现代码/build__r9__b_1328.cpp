
#include<cstdio>
int a[201],b[201]; int ansa=0,ansb=0; int n,na,nb,ma,mb;
int w[5][2]={{1,4},{2,4},{0,3},{0,1},{2,3}};
int main(){
 ma=1,mb=1;
 scanf("%d%d%d",&n,&na,&nb);
 for(int i=1;i<=na;i++) scanf("%d",&a[i]);
 for(int i=1;i<=nb;i++) scanf("%d",&b[i]);
 for(int i=na+1;i<=n;i++){ a[i]=a[ma];ma++; if(ma==na+1) ma=1; }
 for(int i=nb+1;i<=n;i++){ b[i]=b[mb];mb++; if(mb==nb+1) mb=1; }
 for(int i=1;i<=n;i++){
  if(a[i]==b[i]) continue;
  for(int j=0;j<=1;j++) if(b[i]==w[a[i]][j]) ansb++;
  for(int j=0;j<=1;j++) if(a[i]==w[b[i]][j]) ansa++;
 }
 printf("%d %d",ansa,ansb);
 return 0;
}
