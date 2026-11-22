
#include <iostream>
using namespace std;
int main(){
 int n; int a[101]; int b[10001]={0};
 cin>>n;
 for(int i=0;i<n;i++) cin>>a[i];
 for(int i=0;i<n-1;i++) for(int j=i+1;j<n;j++) if(a[i]+a[j]<=10000) b[a[i]+a[j]]=1;
 int count=0;
 for(int i=0;i<n;i++) if(b[a[i]]==1) count++;
 cout<<count;
 return 0;
}
