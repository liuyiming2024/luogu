// P1026 std：从右往左算 num[l][r]，再 dp[t][i]=max dp[t-1][j]+num[j+1][i]。
#include <bits/stdc++.h>
using namespace std;int main(){int p,k;if(!(cin>>p>>k))return 0;string s,tmp;
 for(int i=0;i<p;i++){cin>>tmp;s+=tmp;}int L=(int)s.size();s=" "+s;int sd;cin>>sd;vector<string>w(sd);
 for(int i=0;i<sd;i++)cin>>w[i];vector<int>mend(L+2,1000000000);
 for(int i=1;i<=L;i++)for(string&x:w)if(i+(int)x.size()-1<=L&&s.substr(i,x.size())==x)mend[i]=min(mend[i],i+(int)x.size()-1);
 vector<vector<int>>num(L+2,vector<int>(L+2,0));
 for(int r=1;r<=L;r++)for(int l=r;l>=1;l--)num[l][r]=num[l+1][r]+(mend[l]<=r?1:0);
 const int NEG=-1000000000;vector<vector<int>>dp(k+1,vector<int>(L+1,NEG));dp[0][0]=0;
 for(int t=1;t<=k;t++)for(int i=t;i<=L;i++)for(int j=t-1;j<i;j++)dp[t][i]=max(dp[t][i],dp[t-1][j]+num[j+1][i]);
 cout<<dp[k][L]<<'\n';return 0;}
