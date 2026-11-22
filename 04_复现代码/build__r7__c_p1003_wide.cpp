
#include <bits/stdc++.h>
using namespace std;
int im[100005][4];
int n,x,y,ans=-1;
int main(){
 scanf("%d",&n);
 for(int i=1;i<=n;i++) scanf("%d%d%d%d",&im[i][0],&im[i][1],&im[i][2],&im[i][3]);
 scanf("%d%d",&x,&y);
 for(int i=n;i>=1;i--){
  if(im[i][0]+im[i][2]>=x && im[i][1]+im[i][3]>=y && im[i][0]<=x && im[i][1]<=y){ ans=i; break; }
 }
 printf("%d",ans);
 return 0;
}
