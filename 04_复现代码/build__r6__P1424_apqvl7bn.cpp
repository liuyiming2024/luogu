
#include<cstdio>
int n,k,s=0;
int main(){
 scanf("%d %d",&n,&k);
 for(int i=1;i<=k;i++){
  if(n!=6 && n!=7) s+=250;
  if(n==7) n=1; else n++;
 }
 printf("%d",s);
 return 0;
}
