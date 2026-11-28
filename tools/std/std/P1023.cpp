// P1023 std：volume() 按段线性插值 + 最高价外递减；枚举补贴按 |s| 取最小。
#include <bits/stdc++.h>
using namespace std;int main(){int E;if(!(cin>>E))return 0;long long C,V0;cin>>C>>V0;
 vector<pair<long long,long long>>pt;pt.push_back({C,V0});long long u,v;
 while(cin>>u>>v){if(u==-1&&v==-1)break;pt.push_back({u,v});}long long d;cin>>d;sort(pt.begin(),pt.end());
 long long maxp=pt.back().first,maxv=pt.back().second;
 auto volume=[&](long long p)->long long{if(p<=maxp){
  for(size_t i=0;i+1<pt.size();i++)if(p>=pt[i].first&&p<=pt[i+1].first){long long dx=pt[i+1].first-pt[i].first;if(dx==0)return pt[i].second;
   long long dy=pt[i+1].second-pt[i].second,num=dy*(p-pt[i].first);
   return pt[i].second+(num>=0?num/dx:-((-num+dx-1)/dx));}return pt[0].second;}
  return maxv-d*(p-maxp);};
 long long hiP=maxp+(d>0?maxv/d+2:2),vE=volume(E);int ans=0;bool found=false;
 for(int mag=0;mag<=2000&&!found;mag++)for(int sgn=-1;sgn<=1;sgn+=2){
  if(mag==0&&sgn==1)continue;long long s=(long long)sgn*mag,profitE=(E-C+s)*max(0LL,vE);bool ok=true;
  for(long long p=C;p<=hiP;p++){long long vv=volume(p);if(vv<=0)continue;if((p-C+s)*vv>profitE){ok=false;break;}}
  if(ok){ans=(int)s;found=true;break;}}
 if(!found){cout<<"NO SOLUTION\n";return 0;}cout<<ans<<'\n';return 0;}
