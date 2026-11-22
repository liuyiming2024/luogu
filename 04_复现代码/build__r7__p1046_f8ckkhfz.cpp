
#include <bits/stdc++.h>
using namespace std;
int a[20];
int main(){ int n,cnt=0;
 for(int i=1;i<=10;i++) cin>>a[i];
 cin>>n;
 for(int i=1;i<=10;i++) if(n+30>=a[i]) cnt++;
 cout<<cnt<<endl;
 return 0; }
