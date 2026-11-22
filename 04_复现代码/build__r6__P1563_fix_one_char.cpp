
#include <bits/stdc++.h>
using namespace std;
char a[100005][15];
int n,x=1,z=0,m,b[100005],ai,si;
int main(){
 scanf("%d%d",&n,&m);
 for(int o=1;o<n+1;o++) cin>>b[o]>>a[o];
 for(int i=0;i<m;i++){
  scanf("%d%d",&ai,&si);
  if(ai==0&&b[x]==1) z=si;
  if(ai==1&&b[x]==0) z=si;
  if(ai==0&&b[x]==0) z=0-si;
  if(ai==1&&b[x]==1) z=0-si;
  if(z>=0){
   if(z>=n)z=z%n;
   x=x+z;
   if(x>n)x=x%n;
  }else{
   z=-z;
   if(z>=n)z=z%n;
   x=x-z;
   if(x<=0)x=n+x;
   if(x>n)x=x%n;
  }
 }
 printf("%s",a[x]);
 return 0;
}
