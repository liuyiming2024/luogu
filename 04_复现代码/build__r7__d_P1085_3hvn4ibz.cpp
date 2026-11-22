
#include<bits/stdc++.h>
using namespace std;
int main(){ int MAX=-30,day=0,a,b;
 for(int i=1;i<=7;i++){ cin>>a>>b; if(a+b-8>MAX && a+b-8>0){ MAX=a+b-8; day=i; } }
 cout<<day; return 0; }
