
#include<bits/stdc++.h>
using namespace std;
int n,k;
string x,ma="";
int q[10005],p[1005],qp[1005];
string add(string a,string b)
{
 memset(q,0,sizeof(q)); memset(p,0,sizeof(p)); memset(qp,0,sizeof(qp));
 int lx,ly; lx=a.size(); ly=b.size();
 for(int i=1;i<=lx;i++) { q[i]=a[lx-i]-'0'; }
 for(int i=1;i<=ly;i++) { p[i]=b[ly-i]-'0'; }
 for(int i=1;i<=ly;i++) { for(int j=1;j<=lx;j++) { qp[i+j-1]+=q[j]*p[i]; } }
 for(int i=1;i<lx+ly;i++) { if(qp[i]>9) { qp[i+1]+=qp[i]/10; qp[i]%=10; } }
 int len=lx+ly;
 while(len>1&&qp[len]==0) len--;
 string ua="";
 for(int i=len;i>=1;i--) ua+=char(qp[i]+'0');
 return ua;
}
void dfs(int xx,string u,int v,string ans)
{
 if(n-xx<v) return;
 if(v==0) {
  string uu="";
  for(int i=xx-1;i<n;i++) uu+=x[i];
  ans=add(ans,uu);
  if(ans.size()>ma.size()||ans.size()==ma.size()&&ans>ma) ma=ans;
  return;
 }
 u+=x[xx-1];
 if(v>0) { dfs(xx+1,"",v-1,add(ans,u)); }
 dfs(xx+1,u,v,ans);
}
int main()
{
 cin>>n>>k>>x;
 dfs(1,"",k,"1");
 cout<<ma;
 return 0;
}
