
#include <bits/stdc++.h>
using namespace std;
int a[100010],d[100010],c[100010],n=0;
int main(){
 int x;
 while(cin>>x){ a[++n]=x; }
 memset(d,0x3f,sizeof(d)); memset(c,0x3f,sizeof(c));
 int p=0;
 for(int i=n,j=1; i>=1; i--, j++) {
     p=upper_bound(d+1,d+1+n,a[i])-d; d[p]=a[i];
     p=lower_bound(c+1,c+1+n,a[j])-c; c[p]=a[j];
 }
 int len=1; while(d[len]!=d[0]){ len++; } cout<<len-1<<endl;
 len=1; while(c[len]!=c[0]){ len++; } cout<<len-1<<endl;
 return 0;
}
