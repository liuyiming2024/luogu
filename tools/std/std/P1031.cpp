// P1031 std：贪心，前缀偏差非零即计一次移动。
#include <bits/stdc++.h>
using namespace std;int main(){int n;if(!(cin>>n))return 0;vector<long long>a(n);long long sum=0;
 for(int i=0;i<n;i++){cin>>a[i];sum+=a[i];}long long avg=sum/n,pref=0,ans=0;
 for(int i=0;i<n-1;i++){pref+=a[i]-avg;if(pref!=0)ans++;}
 cout<<ans<<'\n';return 0;}
