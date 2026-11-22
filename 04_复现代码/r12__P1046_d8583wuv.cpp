#include<bits/stdc++.h>
using namespace std;
int a[15],height,ans;
int main(){
ios::sync_with_stdio(0); cin.tie(0); cout.tie(0);
for(int i=1;i<=10;i++)
cin>>a[i];
cin>>height;
for(int i=1;i<=10;i++)
if(height+30>=a[i])//判断
ans++;//累加
cout<<ans<<endl;//输出
return 0;
}
