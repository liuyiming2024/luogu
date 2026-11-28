// P1042 乒乓球 · std：单次增量模拟两种分制，分差≥2 且达标即结算一局。
// E 之后全部忽略（题面附注：E 后可能出现非 WL 字符）。
#include <bits/stdc++.h>
using namespace std;
int main(){
    string s; char c;
    while(cin>>c){ if(c=='E') break; if(c=='W'||c=='L') s+=c; }
    for(int mode : {11,21}){
        int a=0,b=0;
        for(char ch:s){
            if(ch=='W') a++; else b++;
            if(max(a,b)>=mode && abs(a-b)>=2){ cout<<a<<":"<<b<<"\n"; a=b=0; }
        }
        cout<<a<<":"<<b<<"\n";
        if(mode==11) cout<<"\n";
    }
    return 0;
}
