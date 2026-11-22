
#include <bits/stdc++.h>
using namespace std;
int main(){
 double a,b;
 int sum=0;
 cin>>a>>b;
 b=b/10;
 a=a+b;
 while(a>=1.9){ a=a-1.9; sum++; }
 cout<<sum<<endl;
 return 0;
}
