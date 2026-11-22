#include <bits/stdc++.h>
using namespace std;
int a[1001][1001],n;
int main(){
    cin>>n;
    for(int i=0;i<n;i++){
        for(int j=0;j<=i;j++){ cin>>a[i][j]; }
    }
    for(int i=n-1;i>0;i--){
        for(int j=0;j<i;j++){ a[i-1][j]+=max(a[i][j],a[i][j+1]); }
    }
    cout<<a[0][0];
}
