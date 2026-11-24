#include <bits/stdc++.h>
using namespace std;
const int N=50;
int n;
string s[N];
bool cmp(string a,string b){
    return a>b;
}
signed main(){
    cin>>n;
    for(int i=1;i<=n;i++){
        cin>>s[i];
    }
    sort(s+1,s+n+1,cmp);
    for(int i=1;i<=n;i++){
        cout<<s[i];
    }
    return 0;
}
