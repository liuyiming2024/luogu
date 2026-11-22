
#include<bits/stdc++.h>
using namespace std;
int n,x,y,a[1000010],b[1000010];
int main(){
 cin>>n;
 for(int i=1;i<=n;i++){
  cin>>a[i]>>x>>y;
  b[i]=(a[i]+x+y)*1000000+a[i]*1000+n-i;
 }
 sort(b+1,b+n+1);
 for(int i=n;i>n-5;i--){
  cout<<n-b[i]%1000<<" "<<b[i]/1000000<<endl;
 }
 return 0;
}
