
#include <bits/stdc++.h>
using namespace std;
int n,m;
struct node{ double v,w,x; }a[110];
int cmp(node a,node b){ return a.x>b.x; }
int main(){
 cin>>n>>m;
 for(int i=1;i<=n;i++) cin>>a[i].v>>a[i].w,a[i].x=a[i].w/a[i].v;
 sort(a+1,a+n+1,cmp);
 double res=0,weigh=m;
 for(int i=1;i<=n;i++){
     if(weigh){
         if(weigh>=a[i].v){res+=a[i].w,weigh-=a[i].v;}
         else {res+=(weigh/a[i].v)*a[i].w,weigh=0;}
     }
 }
 cout<<fixed<<setprecision(2)<<res<<endl;
 return 0;
}
