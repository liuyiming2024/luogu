#include<bits/stdc++.h>
using namespace std;
int n,a[3010],sum=0;
int main(){
    cin>>n;
    for(int i=1;i<=n;i++)cin>>a[i];
    for(int i=1;i<=n;i++){
        for(int j=i-1;j>=1;j--){
            if(a[i]>a[j])sum++;
        }
        cout<<sum<<' ';
        sum=0;
    }
    return 0;
}
