
#include<bits/stdc++.h>
using namespace std;
int main(){ int n; string a; cin>>n>>a;
 for(int i=0;i<(int)a.size();i++){
  if(a[i]+n>'z') a[i]+=n-26; else a[i]+=n;
 }
 cout<<a; return 0; }
