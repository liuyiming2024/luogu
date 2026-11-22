
#include<iostream>
using namespace std;
int main(){
 int n,a1,a2,b1,b2,c1,c2,da,db,dc,ans;
 cin>>n>>a1>>a2>>b1>>b2>>c1>>c2;
 if(n%a1!=0) da=(n/a1+1)*a2; else da=(n/a1)*a2;
 if(n%b1!=0) db=(n/b1+1)*b2; else db=(n/b1)*b2;
 if(n%c1!=0) dc=(n/c1+1)*c2; else dc=(n/c1)*c2;
 if(da<db) ans=da; else ans=db;
 if(dc<ans) ans=dc;
 cout<<ans;
 return 0;
}
