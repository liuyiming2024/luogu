
#include<bits/stdc++.h>
using namespace std;
bool cmp(const long long& a,const long long& b){ return a>b; }
long long shu[300000]={0};
int main(){
 int n,c; scanf("%d%d",&n,&c);
 for(int i=0;i<n;i++)scanf("%lld",&shu[i]);
 sort(shu,shu+n,cmp);
 int t=0,w=1; int tj,wj; int st,sw; long long sum=0;
 while(w<n){
  if(shu[t]-shu[w]>c)t++;
  if(shu[t]-shu[w]<c)w++;
  if(shu[t]-shu[w]==c){
   tj=wj=0; st=t,sw=w;
   for(int i=t;shu[i]==shu[st];i++){ tj++; t++; }
   if(c==0){wj=tj;w=t;}
   else for(int i=w;shu[i]==shu[sw];i++){ wj++; w++; }
   sum+=(long long)tj*(long long)wj;
  }
 }
 printf("%lld",sum); return 0;
}
