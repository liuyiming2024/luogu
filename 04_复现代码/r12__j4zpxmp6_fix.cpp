#include<bits/stdc++.h>
using namespace std;
int a,b,c;
bool check1(int n){
    string s=to_string(n);
    if(s.size()!=3) return 0;
    for(int i=0;i<s.size();i++) for(int j=0;j<s.size();j++){
        if(i!=j && s[i]==s[j]) return 0;
        if(s[i]=='0'||s[j]=='0') return 0;
    }
    return 1;
}
bool check2(int n,int m){
    string s=to_string(n),t=to_string(m);
    for(int i=0;i<s.size();i++) for(int j=0;j<t.size();j++) if(s[i]==t[j]) return 0;
    return 1;
}
int main(){
    int cnt=0; cin>>a>>b>>c;
    if(a==0||b==0||c==0){ cout<<"No!!!"; return 0; }
    for(int i=1;i<=9;i++) for(int j=1;j<=9;j++){
        if(i==j) continue;
        for(int k=1;k<=9;k++){
            if(i==k||j==k) continue;
            int n1=i*100+j*10+k;
            if((long long)n1*b%a || (long long)n1*c%a) continue;
            int n2=(long long)n1*b/a, n3=(long long)n1*c/a;
            if(!check1(n2)||!check1(n3)) continue;
            if(!check2(n1,n2)||!check2(n1,n3)||!check2(n2,n3)) continue;
            cnt++; cout<<n1<<" "<<n2<<" "<<n3<<"\n";
        }
    }
    if(cnt==0) cout<<"No!!!";
    return 0;
}
