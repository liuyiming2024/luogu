
#include<bits/stdc++.h>
using namespace std;
const int N=1e6+5;
int n,a[N],b[N],j=0;
int main(){
 cin>>n;
 for(int i=1;i<=n;i++) cin>>a[i];
 sort(a+1,a+1+n);
 for(int i=1;i<=n;i++) if(a[i]!=a[i-1]) b[++j]=a[i];
 cout<<j<<"\n";
 for(int i=1;i<=j;i++) cout<<b[i]<<" ";
 return 0;
}
