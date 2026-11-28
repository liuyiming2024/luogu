// P1023 朴素：显式展开「价位→销量」表再逐项算利润，不用 volume 函数。
#include <bits/stdc++.h>
using namespace std;int main(){int E;if(!(cin>>E))return 0;long long C,V0;cin>>C>>V0;
 vector<pair<long long,long long>>pt;pt.push_back({C,V0});long long u,v;
 while(cin>>u>>v){if(u==-1&&v==-1)break;pt.push_back({u,v});}long long d;cin>>d;sort(pt.begin(),pt.end());
 long long maxp=pt.back().first,maxv=pt.back().second,hiP=maxp+(d>0?maxv/d+2:2);
 vector<long long>vol(hiP-C+1,0);
 for(long long p=C;p<=maxp;p++){long long got=pt[0].second;
  for(size_t i=0;i+1<pt.size();i++)if(p>=pt[i].first&&p<=pt[i+1].first){long long dx=pt[i+1].first-pt[i].first,dy=pt[i+1].second-pt[i].second,num=dy*(p-pt[i].first);
   got=dx?pt[i].second+(num>=0?num/dx:-((-num+dx-1)/dx)):pt[i].second;break;}vol[p-C]=got;}
 for(long long p=maxp+1;p<=hiP;p++)vol[p-C]=maxv-d*(p-maxp);
 long long vE=vol[E-C];int ans=0;bool found=false;
 for(int mag=0;mag<=2000&&!found;mag++)for(int sgn=-1;sgn<=1;sgn+=2){
  if(mag==0&&sgn==1)continue;long long s=(long long)sgn*mag,profitE=(E-C+s)*max(0LL,vE);bool ok=true;
  for(size_t i=0;i<vol.size();i++){if(vol[i]<=0)continue;long long p=C+(long long)i;if((p-C+s)*vol[i]>profitE){ok=false;break;}}
  if(ok){ans=(int)s;found=true;break;}}
 if(!found){cout<<"NO SOLUTION\n";return 0;}cout<<ans<<'\n';return 0;}
