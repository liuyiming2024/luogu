
#include <bits/stdc++.h>
using namespace std;
int main(){
    int n;
    while(cin>>n){
        vector<long long> a(n);
        for(auto &x:a) cin>>x;
        if(n==1){ cout<<"Jolly\n"; continue; }
        vector<long long> d;
        for(int i=0;i<n-1;i++) d.push_back(llabs(a[i+1]-a[i]));
        sort(d.begin(),d.end());
        bool ok=true;
        for(int i=0;i<n-1;i++) if(d[i]!=i+1){ ok=false; break; }
        cout<<(ok?"Jolly":"Not jolly")<<"\n";
    }
    return 0;
}
